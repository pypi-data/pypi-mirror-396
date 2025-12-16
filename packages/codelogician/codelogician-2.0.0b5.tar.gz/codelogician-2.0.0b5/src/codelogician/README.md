# CodeLogician

*CodeLogician* is the neurosymbolic agentic governance framework for AI-powered coding.

*It helps your coding agent think logically about the code it's producing and test cases it's generating.*
The fundamental flaw that all LLM-powered assistants have is the reasoning they're capable of is based on statistics,
while you need rigorous logic-based automated reasoning.

- Generated code is based on explainable logic, not pure statistics
- Generated test cases are generated come with quantitative coverage metrics
- Generated code is consistent with the best security practices leveraging formal verification

To run *CodeLogician*, please obtain an *Imandra Universe API* key available (there's a free starting plan) 
at *[Imandra Universe](https://universe.imandra.ai)* and make sure it's available in your environment as `IMANDRA_UNI_KEY`.

*Three typical workflows*:
1. **DIY mode** - this is where your agent (e.g. Grok) uses the CLI to:
- Learn how to use IML/ImandraX via **`doc`** command (e.g. **`codelogician doc --help`**)
- Synthesizes IML code and uses the **`eval`** command to evaluate it
- If there're errors, use **`codelogician doc view errors`** command to study how to correct the errors and re-evalute the code

2. **Agent/multi-agent mode** - CodeLogician IML Agent is a Langgraph-based agent for automatically formalizing source code into Imandra Modeling Language (IML).
- With `agent` command you can formalize a single source code file (e.g. `codelogician agent PATH_TO_FILE`)
- With `multiagent` command you can formalize a whole directory (e.g. `codelogician agent PATH_TO_DIR`)

3. **Server** 
- This is a "live" and interactive version of the `multiagent` command
- It monitors the filesystem and fire's off formalization tasks on source code updates as necessary
- You can start the server and connect to it with the TUI (we recommend separate terminal screens)


Learn more at *[CodeLogician](https://www.codelogician.dev)!*

To get started, 
```shell
codelogician --help
```