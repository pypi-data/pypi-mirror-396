# ruff: noqa: I001,UP031, E501, E741, RUF012, N806

# , E702, E701
import os
import textwrap

import structlog
from typing import Annotated
from pprint import pformat

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from utils.langchain_neo4j import Neo4jGraph, Neo4jVector
from langgraph.graph import END, START, StateGraph
from langsmith import traceable
from pydantic import BaseModel, Field

# fmt: off
from agents.fix_wizard.util import (bind, compose, fboth, filter, flat_map, forkr,
                                    fsnd, lazy, map, maybe_else, not_empty, snd, splice)
from utils.agent.base import (AgentDisclosure, AgentGraph, EndResult,
                              ImandraMetadata, InputBase, NodeMetadata)
from utils.llm import get_llm


logger = structlog.get_logger("agents.fix_wizard.graph")

neo_auth = { 'url'      : os.getenv('FIX_NEO4J_URI')
           , 'password' : os.getenv('FIX_NEO4J_PASSWORD')
           , 'username' : os.getenv('FIX_NEO4J_USERNAME')
           }


def vecdb(node_label, index_name, retrieval_query, embeddings, graph, thresh=0.65, limit=6):
    print("Connecting to Neo4j at: %s" % neo_auth['url'])
    retrieval_query = 'WHERE score > %f %s LIMIT %d' % (thresh, retrieval_query, limit)
    num_entries = graph.query('match (e:%s) return count(e) as n' % node_label)[0]['n']
    print("Wrapping index %s for %d entries..." % (index_name, num_entries))
    return Neo4jVector.from_existing_index(embedding=embeddings, node_label=node_label,
                                        embedding_node_property="embedding",
                                        index_name=index_name,
                                        retrieval_query=retrieval_query, **neo_auth)


vecdb_from_examples = bind(vecdb, "Example", "example_vector",
                           "RETURN node.question AS text, score, {cypher: node.cypher} AS metadata")

vecdb_from_statements = bind(vecdb, "Statement", "statement_vector",
                             "RETURN node.statement AS text, score, {} AS metadata")

vecdb_from_entities3 = bind(vecdb, "NamedEntity", "entity_vector",
                           "RETURN node.name AS text, score, {instances: node.instances} AS metadata")

vecdb_from_entities_queries = bind(vecdb, "EntityNamesQuery", "entities_vector",
                                   "RETURN node.kind AS text, score, {cypher: node.cypher} AS metadata")


class CypherResponse(BaseModel):
    """ Cypher code generated in response to a user request """
    cypher: str = Field(description="The cypher query, conforming to the latest Neo4j standard.")
    graph_id: str = Field(description="The graph_id of the FIX spec to run this query against.")

class GraphIdQuery(BaseModel):
    """ Response to a user request to query or set the graph_id for the FIX spec of interest.
    The 'new_graph_id' will be used for Cypher queries going forward."""
    previous_graph_id: str = Field(description="The graph_id for to the previous Cypher generation.")
    new_graph_id: str = Field(description="The graph_id to use for future Cypher queries.")

class Response(BaseModel):
    """Response to a user request. If the user asks a question that corresponds to a Cypher query,
    respond with a `CypherResponse`. If the user ask about the current FIX model or asks to switch
    to querying a new FIX model, respond with a `GraphIdQuery`. If the user asks a question about a
    different FIX spec, do not use a GraphIdQuery response; use a CypherResponse including the new
    FIX spec graph_id."""
    response_union: CypherResponse | GraphIdQuery

def merge_maybes(left, right, **kwargs):
    # print('--> merging: %s + %s --> %s' % (left, right, right or left))
    return right or left


class GraphConfig(BaseModel):
    fix_graph_id: str | None = None

class InputState(InputBase):
    question: str = Field(description="A question about the FIX spec")
    previous_graph_id: Annotated[str | None, merge_maybes] = \
        Field(description="The graph_id of the previously queried FIX spec")

class GraphState(InputState, AgentDisclosure):
    response: str | Response = None   # reply from Cypher generation LLM
    scope: str | None = None          # set if Cypher execution results in scope fallback
    statements: list[str] = []
    results: list[tuple[str,list[dict]]] = [] # Cypher query results formatted for prompt
    final: AIMessage | None = None    # Reply from question-answering LLM

    def render(self) -> str:
        return ('```\n%s\n```\n%s'
                % (maybe_else('-- No results --', pformat, self.results),
                   maybe_else('-- No answer --', content_of, self.final)))

# def has_tool_calls(msg): return hasattr(msg, 'tool_calls') and len(msg.tool_calls) > 0
def content_of(x): return x.content
def sys_msg(x): return SystemMessage(content=x)
def indent(n): return lambda x: textwrap.indent(x, n*' ')

def state_of_question(q, graph_id=None):
    return InputState(question=q, previous_graph_id=graph_id)

def render_state(state):
    return ('```\n%s\n```\n%s'
            % (maybe_else('-- No results --', pformat, state['results']),
               maybe_else('-- No answer --', content_of, state['final'])))



template = \
    """Task:Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Do not use GROUP BY in the Cypher query as it is not supported.
Make sure not to refer to undefined variables in the Cypher query.
Return distinct results only.

[Begin schema]
%s
[End schema]
"""

qa_prompt = \
    """The query results contain the provided information that you must use to construct
an answer. The provided information is authoritative, you must never doubt it or try
to use your internal knowledge to correct it. Make the answer sound as a response to
the question. Do not mention that you based the result on the given information.
Here is an example using just 1 query and results table:

Cypher query 1:
  MATCH (e:Enum {name:'PutOrCall'})-[r:CASE]->(c:Case) RETURN c.name, r.value
  Full results table:
    The column headings are: [c.name, r.value]
    The rows are:
      "Put","0"
      "Call","1"

Question: What are the cases of the PutOrCall enum? Give me the name and valid value of each case.
Helpful Answer: The cases of the PutOrCall enum are Put<0> and Call<1>.

Follow this example when generating answers.
Describe any validations in simple terms.
If listing entities of mixed types, mention the type of each entity.
Refer to fields as "FieldName<Tag>".
Refer to enum cases as "CaseName<Value>".
Refer to messages as "MessageName<Tag>".

Print the results in a Markdown-formatted table.
"""

scope_preamble = \
    """\nBe sure to mention in your reply that no results were found in FIX \
spec, and that the results in the above tables were found in the \
imported FIX dictionary."""

def filter_schema_lines(lines):
    headers = ['Node properties:', 'Relationship properties:', 'The relationships:']
    irrelevant_labels = ['NamedEntity', 'Example', 'Statement', 'EntityNamesQuery']
    def maybe_indent(l): return l if l in headers else '   ' + l
    def relevant(l): return all(label not in l for label in irrelevant_labels)
    return map(maybe_indent, filter(relevant, lines))

n4j_graph = Neo4jGraph(**neo_auth) # enhanced_schema=True
schema = '\n'.join(filter_schema_lines(n4j_graph.schema.split('\n')))

# def print_message(msg): print("%s:\n%s" % (type(msg), msg.content))

@lazy
def db():
    from langchain_openai import OpenAIEmbeddings

    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    def apply_vecdb(f, thresh, limit):
        db = f(embeddings, n4j_graph, thresh=thresh, limit=limit)
        return bind(db.similarity_search_with_score_by_vector, k=2*limit, query='')
    return {'examples':   apply_vecdb(vecdb_from_examples,   0.64, 6)
           ,'statements': apply_vecdb(vecdb_from_statements, 0.61, 6)
           ,'entities':   apply_vecdb(vecdb_from_entities3,  0.65, 7)
           ,'entities_queries': apply_vecdb(vecdb_from_entities_queries, 0.64, 3)
           ,'embed': embeddings.embed_query
           }


async def rag_cypher(state: InputState, config) -> GraphState:
    DB = db()
    question = state.question
    vector = DB['embed'](state.question)
    print('---> rag_cypher: previons_graph_id = %s' % state.previous_graph_id)
    graph_id = state.previous_graph_id or config['configurable']['fix_graph_id']
    llm = get_llm('gpt-4o', temperature=0.2)

    def escape(s): return s.replace('{', '{{').replace('}','}}')

    def fmt_example(d, score):
        question, response = d.page_content, d.metadata['cypher']
        print("Score:%s\n   Q: %s\n   A: %s" % (score, question, response))
        return map(escape, ["\nQuestion: %s" % question, "Answer: %s" % response])

    def fmt_statement(d, score):
        print("Score:%s - %s" % (score, d.page_content))
        return [d.page_content]

    def fmt_entity(d, score):
        name, instances = d.page_content, d.metadata['instances']
        labels = {s.split("||")[1] for s in instances}
        print("Score:%s - %s : %s" % (score, name, ','.join(labels)))
        return ['%s is the name of nodes with these labels: %s' % (name, l) for l in labels]

    def fmt_entities_query(d, score):
        kind, cypher = d.page_content, d.metadata['cypher']
        hits = n4j_graph.query(cypher.replace('$MAYBE_PROPS$', '{graph_id:"%s"}' % graph_id))
        values = [next(iter(d.values())) for d in hits]
        print("Score:%s\n   %s values: %s" % (score, kind, values))
        return ['%s values: %s' % (kind, ','.join(values))]

    def fmt_section(heading, lines): return [heading, *map(indent(3), lines)]
    @traceable
    def rag_lines(fmt, db_key): return flat_map(splice(fmt), DB[db_key](vector))
    def fmt_rag(heading, fmt, db_key): return fmt_section(heading, rag_lines(fmt, db_key))

    more = [("The current FIX spec has graph_id='%s'."
             "Use this graph_id if no graph_id is implied in the users's question." % graph_id),
            "Do not wrap the Cypher code in markdown."]
    examples = fmt_rag("Here are some examples questions with answers:", fmt_example, 'examples')
    entities = fmt_rag("Named entities with their labels", fmt_entity, 'entities')
    entities2 = fmt_rag("Property values", fmt_entities_query, 'entities_queries')
    sections = map('\n'.join, [entities2, entities, more, examples])
    prompt = template % indent(3)(schema)
    prompt_msg = sys_msg('\n\n'.join([prompt, *filter(not_empty, sections)]))
    st0 = 'Take care to get the direction of any relations correct.'
    statements = rag_lines(fmt_statement, 'statements')
    msgs = [prompt_msg, HumanMessage('\n'.join(["Question: " + question, st0, *statements]))]
    # foreach(print_message, msgs)
    response = await llm.with_structured_output(Response).ainvoke(msgs)
    print('---> LLM response: %s' % response)
    return {'response': response, 'statements': statements, 'results': [],
            'scope': None, 'final': None, 'end_result': EndResult(result='success')}


def run_cypher_node(state: GraphState, config) -> GraphState:
    from agents.fix_wizard import cypher_parser as pa, cypher_printer as pr
    from agents.fix_wizard.cypher_ast import Option
    from agents.fix_wizard.cypher_ops import scoping_analysis, set_scope_and_graph_id, split_unions

    cypher = state.response.response_union.cypher.strip()
    graph_id = state.response.response_union.graph_id

    def needs_rescope(scope, statement):
        match scoping_analysis(statement):
            case (False, True):
                print('No mention of scope, has scopable edges: %s' % scope)
                return (True, Option.SOME(scope))
            case _:
                print('Leaving statement unchanged.')
                return (False, Option.NONE())

    @traceable
    def parse_cypher(cypher): return pa.parse(pa.statement, cypher)

    ast = parse_cypher(cypher)

    @traceable
    def run_in_scope(scope):
        rescoped, scope = needs_rescope(scope, ast)
        ast2 = set_scope_and_graph_id(scope, graph_id)(ast)
        run_ast = compose(forkr(n4j_graph.query), str.strip, pr.to_string, pr.statement)
        return rescoped, map(run_ast, split_unions(ast2))


    def total_rows(x): return sum(map(compose(len, snd), x))
    rescoped, results = run_in_scope('model')
    results, scope = ((results, None) if total_rows(results) > 0 or not rescoped else
                      (snd(run_in_scope('imported')), 'imported'))
    # pprint(results)
    return {'results': results, 'scope': scope, 'previous_graph_id': graph_id}


async def qa_node(state: GraphState, config) -> GraphState:
    llm = get_llm('gpt-4o', temperature=0.2)
    full_prompt = qa_prompt + ('' if state.scope is None else scope_preamble)
    statements = '\n'.join(state.statements)

    def fmt(x): return 'Cypher query with results:\n   Query:\n%s\n   Results:\n%s' % x
    pipeline = compose(sys_msg, fmt, fboth(indent(6)), fsnd(pformat))
    results = map(pipeline, state.results)
    msgs = [sys_msg(full_prompt), *results, HumanMessage('%s\n%s' % (state.question, statements))]
    return {'final': await llm.ainvoke(msgs)}


def graph_id_query(state: GraphState, config) -> GraphState:
    previous_graph_id = state.previous_graph_id or config['configurable']['fix_graph_id']
    graph_id = state.response.response_union.new_graph_id
    content = ('The previous FIX model being queried was _%s_.\n\n'
               'The FIX model to query going forward is _%s_.'
               % (previous_graph_id or graph_id, graph_id))
    return { 'previous_graph_id': graph_id
           , 'final': AIMessage(content=content)
           , 'results': state.results
           }


def metadata(task_name):
    return NodeMetadata(imandra=ImandraMetadata(task_name=task_name))

def build_chat(gb):
    gb.add_node("cypher_gen", rag_cypher,
                metadata=metadata("Answering question about FIX spec"))
    gb.add_node('run_cypher', run_cypher_node,
                metadata=metadata("Running Cypher query"))
    gb.add_node('graph_id_query', graph_id_query,
                metadata=metadata("Handling query about graph_id"))
    gb.add_node('answer', qa_node,
                metadata=metadata("Composing answer to original question"))

    def route(state: GraphState):
        return {CypherResponse: 'run_cypher'
               ,GraphIdQuery: 'graph_id_query'
               }[type(state.response.response_union)]

    gb.add_edge(START, "cypher_gen")
    gb.add_conditional_edges('cypher_gen', route)
    gb.add_edge('graph_id_query', END)
    gb.add_edge('run_cypher', 'answer')
    gb.add_edge('answer', END)

def build_cypher_tester(gb):
    gb.add_node('cypher_gen', rag_cypher)
    gb.add_node('run_cypher', run_cypher_node)

    gb.add_edge(START, 'cypher_gen')
    gb.add_edge('cypher_gen', 'run_cypher')
    gb.add_edge('run_cypher', END)

    return gb


def state_graph(): return StateGraph(GraphState, input_schema=InputState, context_schema=GraphConfig)

def build_graph(builder, memory):
    gb = state_graph()
    builder(gb)
    return (gb.compile() if memory is None else
            gb.compile(checkpointer=memory))

graph = build_graph(build_chat, None)
agent = AgentGraph(
    agent_type="one_shot_tool",
    full_name="FIX Wizard",
    use_case="Answer questions about a FIX spec",
    task_name="FIX wizard",
    tool_description=("Answer questions about elements of a FIX spec, including"
                      " datatypes, enums, fields, repeating groups and messages."),
    input_schema=InputState,
    state_schema=GraphState,
    config=GraphConfig,
)


if __name__ == "__main__":
    import datetime
    with open(f"mermaid_{datetime.datetime.now().strftime('%m%d%H%M')}.md", "w") as f:
        f.write("```mermaid\n%s\n```" % graph.get_graph(xray=True).draw_mermaid())
