This is documentation about SpecLogician, intended for developers working on
the project.

# Core architecture

The intended purpose of SpecLogician is to translate natural language specs
into IPL models, to reason about the source spec using IPL-based tools like
region decomposition, [unsat analysis](https://github.com/imandra-ai/ipl-unsat-analyzer), etc.

SpecLogician uses LLMs in the translation pipeline. However, it _does not_ use
LLMs to directly translate the user's input spec to IPL. Instead, LLMs are used
to generate an intermediate, formal representaion of the user's input spec,
using a DSL that we call FormalSpec. The LLM-generated FormalSpec code is then
programmatically compiled to IPL. To summarize:

1. Natural language spec (user input) --> FormalSpec (LLM)
2. FormalSpec --> IPL (regular Python code)

We talk about FormalSpec in more detail in its own section below.

# SpecLogician agents

SpecLogician is implemented as a LangGraph agent/graph. There are currently two
SpecLogician agents/graphs:

- `spec_logician_formal`: this is the "old" implementation of the agent. Its
  modules can be found in `./formal_spec/`, and the graph itself is defined in
  `./formal_spec/graph.py`. Currently we only use this agent in the [VS Code
  extension](https://github.com/imandra-ai/spec-logician-vscode), with plans to
  completely replace it with the "new" SpecLogician agent soon.
- `spec_logician`: this is the "new" implementation of the agent, following a
  state transition-based architecture originally introduced in CodeLogician.

## State transition-based agent

The "new" SpecLogician agent is based on state transitions. The agent's
`GraphState` keeps a `FormalizationState` object that tracks the formalization
process. This state evolves as the user issues commands to the agent (via MCP,
VS Code extension commands, Python API, etc.). The formalization state is
defined in `./formalization_state.py`.

The commands that users can issue to the agent are specified by the type
`UserCommand`, defined in `./graph.py`. Most commands correspond to actions
that (destructively) modify the agent's internal state, but some of them are
purely read-only.

To have the agent execute a command, we set the `command` field of
`GraphState`, and invoke the graph. The agent will start running from its
`exec_command` node, which is a "supervisor" node that reads the `UserCommand`
stored in the `command` field and invokes the appropriate handler for that
command.

Most of the functionality offered by the agent is implemented as
state-transition functions in `./tools.py`. These funtions are used by the
agent in `./graph.py` to handle the various `UserCommand`s.

Since LangGraph doesn't provide a direct way for graph invocations to return a
result, we use `GraphState`'s field `end_result` of type `EndResult` to store
the result of each invocation. To return data from command executions, we set
the `info` field of the `end_result` object; this is a string field, so
non-string data is stored JSON-encoded.

## MCP server

The state transition-based agent also constitutes the basis for the
SpecLogician MCP server, as implemented in
`../../../packages/iu-mcp/src/iu_mcp/servers/spec_logician`. Most MCP
tools/functions implemented there correspond 1-to-1 to `UserCommand`
constructors as defined in ./graph.py`, and are essentially just wrappers for
graph invocations.

# FormalSpec DSL

The idea of FormalSpec is to define an intermediate syntax for SpecLogician
that sits, syntactically and semantically, in between natural language Gherkin
specs and IPL models. It tries to achieve this by representing specs with the
same overall structure as Gherkin (user stories/scenarios, Given/When/Then
clauses, etc.), but with more contrained syntactic rules, and the ability to
embed IPL code, among other things. The prompt in `./formal_spec/sys-prompt.md`
gives a detailed description of the DSL and its components and terminology.

In SpecLogician, the LLM generates FormalSpec code rather than IPL models. The
point of this is to make the generative process easier for the LLM, as the
language gap between the natural language spec and FormalSpec is shorter
compared to that between natural language and raw IPL. Having obtained a formal
spec from the LLM, we can _then_ generate an IPL model from it via purely
programmatic, and deterministic, processes. The design goal of FormalSpec is
therefore to be an intermediate formal language that is as close as possible to
natural language Gherkin specs, while also being formal and unambiguous to the
point that we can deterministically extract IPL models from it.

Modules relating to FormalSpec are contained in `./formal_spec/dsl/`. These modules
implement various aspects of the DSL, like:

- `syntax.py`: types defining the syntax (AST) of the DSL
- `ipl.py`: types defining the syntax (AST) of (a subset of) IPL. The prompt in
  `./formal_spec/ipl-expr-101.md` given an overview of the kind of IPL construct
  we support in SpecLogician.
- `checking.py`: validation logic for the DSL
- `codegen.py`: functions to generate IPL code from FormalSpec constructs
- `diff.py`: functions to compute structured diffs between two FormalSpec specs
- `feedback.py`: types defining all the errors/warnings that can arise from
  validating a FormalSpec feature. Also includes functions to generate error
  messages to be fed to the LLM during the formalization loop
- `ipl_parser.py`: parsing logic for IPL expressions and statements, as defined in `./formal_spec/dsl/ipl.py`
- `parser.py`: parsing logic for FormalSpec constructs, as defined in `./formal_spec/dsl/syntax.py`
- `pretty_printing.py`: functions to pretty-print FormalSpec features from
  their AST representation as defined in `./formal_spec/dsl/syntax.py`

## Supported IPL constructs

We don't currently support all of IPL in SpecLogician, but only a select subset
of them. The main reason is that adding more construct would not be trivial
(see next section), and until now we prioritized getting a few things to work
reasonably well rather than implementing a lot of things that only work 30% of
the time.

## State of IPL generation

Convinging the LLM to generate correct IPL code (even when only considering a
subset of it) is perhaps the main challenge with SpecLogician. Most of these
challenges are a consequence of various quirks and idiosyncrasies of IPL that
can sometimes be a bit confusing to LLMs. Some examples are:

- The subscript syntax `foo[i]` only indexes into maps. It's not valid for
  extracting elements out of lists. In any case, `foo[i]` is only valid if `foo`
  is an identifier; when `foo` is a more complex expression, like
  `(fn_returning_a_map())[0]`, we get a parse error.
- Functions acting on datastructures are a mix of purely functional and
  imperative, and there's no way to tell which paradigm is used for which
  function. For example: `add` on lists is functional (it returns a new list),
  but `insert` on maps and sets is imperative (it destructively updates the
  argument); most of the functions operating on lists are functional, but the
  only way to iterate over lists is with an imperative for-loop.
- Many basic functions that people (and LLMs!) would expect from a general
  purpose programming language are missing from the collection of builtin
  functions. For example: there is no builtin way to index into a list or
  Update its elements; there is a `take` function for lists, but no `drop`.
  See [this open issue](https://github.com/imandra-ai/iu-agents/issues/231) for
  an alternative discussion on this point.
- The errors produced by the LSP can sometimes be quite confusing and a bit
  misleading. Very often, syntactic problems in the source code will give rise to
  type errors involving the `unknown type`. See [this open
  issue](https://github.com/imandra-ai/ipl/issues/1697) for an example.
- Empty actions are allowed, but empty messages are [rejected with confusing
  errors](https://github.com/imandra-ai/ipl/issues/1685).

Obviously, with most of these issues, IPL isn't actually at fault: until
now, IPL has been almost exclusively used in a very specific domain, to model
financial venues. While there's always room for improvement, in those scenarios
IPL was enough. The problem is that in the context of SpecLogician, we are
trying to use IPL to model general purpose systems, even though IPL is not (at
the moment) a general purpose language.

There is [ongoing effort](https://github.com/imandra-ai/ipl-langium) to port
IPL from Xtext to Typefox's new Langium framework, which will definitely take
care of some of the quirks (especially around the LSP, error messages, type
checking, formatting, etc.). More work needs to be done, however, to bring IPL
to a level of feature richness that allows it to properly handle
general-purpose modelling tasks. With still at least about a year to go before
the Langium transition is complete (at the time of writing, July 2025), we
might not get a general-purpose IPL until quite a while into the future. In
light of this, going forward with SpecLogician, it might make more sense in
the medium term to develop a dedicated "IPL-like" language that compiles to IPL
but offers some additional features (like more builtin functions) and better
error message (via a custom parser and type checker).

## Validation

FormalSpec validation is a core part of the agentic workflow of SpecLogician.
While structured output ensures that the FormalSpec ASTs produced by the LLM
are syntactically well-formed, nothing is stopping it from producing semantic
nonsense. Obviously there's a limit to what can be checks by automated tools,
but some validation is certainly better than nothing (although experience also
tells us that _too much_, or _too aggressive_ validation can end up confusing
the LLM even more).

Since FormalSpec features are split into a _preamble_ part and a _scenarios_
part, a significant portion of the validations we run focus on making sure that
these two parts agree with each other. This involves, for example, checking
that all identifiers declared in the preamble are used at least once in the
scenarios.

Validation functions are defined in `./formal_spec/dsl/checking.py`, with the
function `check_feature` being the main entry point. This function calls, in
turn, several other functions that perform specific checks on the various part
of a FormalSpec feature.

All the functions in `checking.py` are generators that produce objects of type
`Feedback`, as defined in `./formal_spec/dsl/feedback.py`. Each constructor of
`Feedback` represents a class of problems that can be found in a FormalSpec
feature. `feedback.py` also provides a pretty-printing function for `Feedback`
terms, that is used to create a textual description of the errors in a
FormalSpec feature to be reported back to the LLM. Extending the `checking.py`
module with new checks typically involves creating a new `Feedback` constructor
in `feedback.py` and adding the necessary pretty-printing logic.

### IPL validation

FormalSpec features often contain embedded IPL code, such as function
definitions in the preamble or expressions within scenario clauses. A crucial
step in validating a FormalSpec feature is therefore to verify the correctness
of this embedded IPL.

For this purpose, we leverage the validation capabilities of the IPL Language
Server Protocol (LSP), accessible through the Imandra Python library. These
functions provide accurate diagnostics, identical to those in an editor with IPL
support. However, a significant challenge arises from the nature of the LSP,
which is designed to operate on complete, well-formed IPL files. The IPL code
within FormalSpec, particularly the expressions in scenarios, are mere snippets
and not valid top-level IPL constructs. Consequently, these expressions cannot
be validated in isolation by the LSP.

To bridge this gap, we have devised a strategy to make these IPL expressions
palatable to the LSP. Our approach involves programmatically constructing a
single, valid IPL model from all the scattered IPL expressions within a
FormalSpec feature. Each expression is wrapped in a synthetic, temporary IPL
function, allowing it to exist as a valid top-level entity. These wrapper
functions are then aggregated into one IPL model file, which can be sent to the
LSP for a comprehensive validation pass.

This aggregation strategy introduces a secondary challenge: tracing validation
errors from the consolidated model back to their original source expressions in
the FormalSpec. Since the LSP reports errors with line numbers corresponding to
the generated model, we need a mechanism to map these locations back. The
current solution is to track the line number range of each expression
as it is placed into the consolidated model. When the LSP returns an error, we
use its source line information to identify the specific FormalSpec expression
that was responsible for the issue. See [this
comment](https://github.com/imandra-ai/iu-agents/pull/178#discussion_r1993983801).

While this method of generating a temporary model and mapping error locations
is functional, it is not without its complexities. An alternative approach
would be to validate each expression individually by creating a dedicated IPL
model for each one and making a separate LSP call. However, this would likely
be less performant due to the significant overhead of numerous network requests
to the validation API. Therefore, the current batch-validation approach remains
our pragmatic choice.

## JSON vs pretty-printed FormalSpec

The syntax of FormalSpec that we show to the user is essentially defined by the
pretty-printing functions in `./formal_spec/dsl/pretty_printing.py`. Arguably
this is the "real" syntax of FormalSpec. However, when using LLMs to generate
FormalSpec code from natural language specs, we don't actually ask the LLM to
directly generate pretty-printed FormalSpec, but rather the LLM generates JSON
that directly maps to FormalSpec AST objects from
`./formal_spec/dsl/syntax.py`. This is because we use the _structured output_
functionality to generate syntactically well-formed FormalSpec, and the
structured output functionality relies, at the moment, on JSON.

This effectively means that there are two FormalSpec "representations" at play
here: the pretty-printed FormalSpec and the JSON FormalSpec. In the future,
when grammar-based structured output from LLMs becomes a thing, it would be
nice to ditch the JSON representation and only use the pretty-printed syntax as
the one true syntax of FormalSpec, both for LLM generation and for user
consumption.
