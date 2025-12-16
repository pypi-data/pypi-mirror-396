## Claude Code Guidelines

### Python Devlopment Tooling

We use `uv` to manage the Python environment. For any python related commands, prefix them with `uv run` so that the correct Python environment is used.

For example, to run a script, you can run:

```bash
uv run python -m some_script.py
```

Linting:
```bash
uv run ruff check . --fix
```

Formatting:
```bash
uv run ruff format .
```

## CodeLogician Agent

**IMPORTANT**: The `formalizer/` and `reasoner/` directories are old versions of CodeLogician and will be removed in the future. Ignore these directories when working on CodeLogician.

### Architecture Overview

CodeLogician is a **neurosymbolic AI agent** that creates "mathematical digital twins" of source code for rigorous formal analysis. It transforms source programs into IML (Imandra Modeling Language) formal models that can be analyzed by **ImandraX**, an automated reasoning engine.

#### The CodeLogician → IML → ImandraX Pipeline
- **CodeLogician**: Transforms source code into formal IML models
- **IML**: Formal modeling language based on Higher-Order Logic (subset of OCaml)
- **ImandraX**: Automated reasoning engine that analyzes IML models through:
  - **Verification Goals (VGs)**: Prove or disprove properties with counterexamples
  - **Region Decomposition**: Systematically generate comprehensive test cases

The system handles user requests via commands and maintains a stateful formalization workflow.

#### Core Components

- **Data Models**: `base/` - Core data structures and state management
- **Command System**: `command.py` - User-facing command definitions
- **Graph System**: `graph/` - LangGraph implementation with handlers and routing
- **Tools**: `tools/` - Specialized formalization and verification tools
- **Imandra Integration**: Uses models from `src/utils/imandra/` for formal verification

### Core Data Models (`base/`)

#### FormalizationState
The central state object tracking the **complete stateful formalization workflow** from source code to verified mathematical model.

##### Two-Stage Model Development
1. **Model Admitted**: Model passes type-checking but may contain **opaque functions** (undefined implementations). ImandraX has limited reasoning capabilities.
2. **Model Executable**: All opaque functions have implementations or approximations. ImandraX can perform comprehensive reasoning and generate thorough test cases.

CodeLogician progresses between stages through **refinement** - adding assumptions and approximations to opaque functions.

##### FormalizationState Structure

- **Formalization Status** (progressive workflow):
  - `UNKNOWN`: Initial state, no formalization attempted
  - `INADMISSIBLE`: Model contains errors, cannot be admitted to ImandraX
  - `ADMITTED_WITH_OPAQUENESS`: Model admitted but contains opaque functions (Stage 1)
  - `EXECUTABLE_WITH_APPROXIMATION`: Model executable with opaque approximations (Stage 2)
  - `TRANSPARENT`: Fully formalized model with no opaque functions (Stage 2)

- **Source Information**:
  - `src_code`, `src_lang`: Original program and language
  - `refactored_code`: List of refactoring steps as (step_name, refactored_code) pairs

- **IML Model Information**:
  - `iml_code`, `iml_symbols`: Generated IML code and symbol definitions
  - `opaques`: Opaque functions with assumptions/approximations for refinement
  - `eval_res`: Model evaluation result (errors indicate INADMISSIBLE status)

- **Analysis Results**:
  - `vgs`: Verification goals for property checking
  - `region_decomps`: Region decomposition results for test generation

- **Formalization Context**:
  - `conversion_source_info`: Retrieved examples/references to aid formalization
  - `conversion_failures_info`: Context from previous failures for retry attempts

### Command System (`command.py`)

Commands define the user interface for CodeLogician operations. The actual implementation logic for each command is in the `tools/` directory.

#### Command Categories
1. **Formalization commands**: Modify the FormalizationState (stateful operations)
2. **Read-only commands**: Query/search without state changes (`get_state_element`, `search_fdb`)

#### Recommended Usage Pattern
- **High-level**: Use `agent_formalizer` for automated end-to-end formalization workflows
- **Low-level**: Use individual commands for fine-grained control over specific steps

#### Key Commands

**State Management**:
- `init_state`: Initialize formalization state with source code
- `get_state_element`: Query specific state elements
- `edit_state_element`: Manually update state fields

**Core Formalization**:
- `gen_model`: Generate IML code from source
- `agent_formalizer`: Full automated formalization workflow
- `check_formalization`: Identify unsupported constructs
- `gen_program_refactor`: Apply functional refactorings

**Verification & Analysis**:
- `gen_vgs`: Generate verification goals from code/comments
- `gen_region_decomps`: Perform region decomposition analysis
- `gen_test_cases`: Generate test cases from decomposition results

**Database & Context**:
- `search_fdb`: Query formalization database for examples/references
- `gen_formalization_data`: Retrieve context for formalization
- `gen_formalization_failure_data`: Gather context for retry attempts

**Opaque Function Refinement**:
- `suggest_assumptions`: Add formal assumptions to opaque functions (enables limited reasoning)
- `suggest_approximation`: Create approximations for opaque functions (enables test generation)

**Synchronization**:
- `sync_source`: Update source code to reflect IML changes
- `sync_model`: Update IML code to reflect source changes

#### Graph System (`graph/`)

##### Core Files
- **GraphState**: Manages command execution with steps and interaction trajectories
- **Supervisor**: Routes commands to appropriate node handlers based on command type
- **Base/Tool Handlers**: Process individual commands with prechecks and state updates
- **Message Handlers**: Handle human-in-the-loop interactions and interrupts

##### Workflow
1. Supervisor receives command and checks for formalization state requirements
2. Routes to appropriate handler (tool node vs message node)
3. Handler runs prechecks, applies formalization changes, updates state
4. Returns control to supervisor for next command

### Tools (`tools/`)

The tools directory contains the **actual implementation logic** for each command defined in `command.py`. Each tool transforms the FormalizationState according to its specific purpose.

##### Core Formalization Tools
- **`formalize_to_iml/`**: Convert source code to IML models with sophisticated prompt engineering and error recovery
- **`inappropriateness_check.py`**: Identify unsupported functions/constructs using AST analysis (determines formalizability)
- **`functional_refactor/`**: Apply functional programming refactorings to improve formalizability

##### Verification & Analysis Tools
- **`gen_vgs/`**: Generate verification goals from code comments and natural language (creates boolean IML functions to test properties)
- **`region_decomp/`**: Perform region decomposition analysis and generate comprehensive test cases covering all edge cases

##### Database & Context Tools
- **`fdb/`**: Query formalization database for examples, API references, and error recovery context using RAG

##### Opaque Function Refinement
- **`opaque.py`**: Handle opaque function assumptions and approximations to progress from Stage 1 → Stage 2 models

##### State Synchronization
- **`sync_model.py`**: Synchronize bidirectional changes between source and IML code with diff tracking

### Typical Workflow

1. **Initialize**: `init_state` with source code
2. **Check**: `check_formalization` for unsupported constructs
3. **Refactor**: `gen_program_refactor` if needed for better formalization
4. **Formalize**: `gen_model` to convert source to IML
5. **Verify**: `gen_vgs` to create verification goals
6. **Analyze**: `gen_region_decomps` for comprehensive behavior analysis
7. **Test**: `gen_test_cases` from decomposition results

### Key Features

- **Multi-step Formalization**: Handles complex workflows with state tracking
- **Error Recovery**: Database-driven context retrieval for failed attempts
- **Human-in-the-Loop**: Interactive feedback for ambiguous cases
- **RAG Integration**: Extensive vector database usage for context
- **Traceability**: Complete logging and trajectory tracking
- **Incremental Updates**: Sync changes between source and IML representations

### Key Insights for Future Development

##### Understanding the System Architecture
- **CodeLogician is a stateful agent**: Unlike typical LLM interactions, CodeLogician maintains persistent FormalizationState across multiple command invocations
- **Commands vs Tools separation**: Commands in `command.py` define the interface; Tools in `tools/` provide implementations
- **MCP Integration**: The system prompt document is for MCP (Model Context Protocol) clients - one of several interfaces to CodeLogician

##### FormalizationState as Central Concept
- **Not just data storage**: FormalizationState represents a complete mathematical model development workflow with two distinct stages
- **Progressive refinement**: The status field tracks concrete progress through formalization stages, each with specific capabilities
- **Opaque functions are intentional**: They represent a design choice for handling complex/unsupported constructs, not failures

##### Working with CodeLogician
- **Prefer `agent_formalizer`**: Use the high-level automated workflow unless fine-grained control is needed
- **Always start with `init_state`**: Establishes the FormalizationState context required for all other operations
- **Two-stage model development**: Understand the distinction between Stage 1 (admitted with opaqueness) and Stage 2 (executable) models
- **State inspection**: Use `get_state_element` to understand current formalization progress and decisions
- **Error recovery**: The system has sophisticated failure handling through database context retrieval

##### Tool Implementation Reality
- Each tool in `tools/` performs specific FormalizationState transformations using LLMs, AST analysis, and database queries
- Tools handle the complexity of prompt engineering, error recovery, and context retrieval
- The graph system orchestrates tool execution with prechecks, state validation, and trajectory tracking
