# Oskar Agent

---

## Overview

Oskar is a multipurpose conversational agent. It integrates with the OpenAI Responses API (using `gpt-5` models by default) and activates a dynamic set of tools (Python execution, file read/write, searches, RAG via Faiss, subordinate agents, corporate integrations, etc.). Configuration is done via `AgentConfig` (`Oskar/agent_config.py`), which is responsible for prompts, tools, knowledge bases, and analytical sources.

---

## Prerequisites

- Python 3.12 or higher.

- Dependencies listed in `requirements.txt`.

- Environment variables `OPENAI_API_KEY` (required for online use) and optional `OPENAI_BASE_URL`.

- To enable SerpAPI (`search_web_tool`), set `SERPAPI_API_KEY`.

---

## Essential Concepts of the `Oskar` Class

- `AgentConfig`: dataclass with slots defining model, prompt, tools, knowledge sources (`knowledge_base`), files (`working_files`), and databases (`working_databases`).

- `Oskar.answer(question, **kwargs)`: generates a `message_id`, prepares the interpolated prompt, builds messages with history/attachments via `attached_files`, sets `reasoning_effort`, orchestrates the call to the Responses API (with a tool loop and offline fallback), and aggregates generated artifacts before returning the complete payload (text, metadata, files, and usage).

- `response_callback`: optional function called after each response with the complete payload.

- `attached_files`: parameter that accepts a file path (string or list) to attach content to the question.

---

## Detailed Class Reference

### `AgentConfig`

**Properties**

- `agent_id`: unique identifier of the agent; defaults to `agent_name` when not provided.

- `agent_name`: displayed name of the agent, used in prompts and history (default: `"Oskar"`).

- `model`: primary model used by the agent (default: `"gpt-5"`).

- `model_settings`: optional dictionary with extra parameters (e.g., `history_window_size`, temperature).

- `system_prompt`: custom system instructions; when absent, a default message is generated containing the agent’s name.

- `description`: short text describing the agent for listings or auxiliary prompts.

- `tools_names`: list of allowed tools beyond the defaults (calculator, date/time).

- `custom_tools`: dictionary with dynamically registered external tools.

- `knowledge_base`: list of Chroma sources (`name`, `folder`, `collection`) used to build RAG retrievers.

- `working_files`: metadata for CSV/auxiliary files available during the session (name, description, path).

- `working_databases`: definitions of SQL databases that automatically generate CSVs (`name`, `description`, `connection_string`, `query`).

- `json_config`: `InitVar` used only by the constructor to hydrate the instance from a dictionary.

**Methods**

- `to_json()`: serializes all public fields into a dictionary ready for persistence.

- `restore_from_json(agent_config)`: updates only the attributes present in the provided dictionary.

### `Oskar`

**Exposed properties and attributes**

- `agent_config`: active `AgentConfig` instance for the session.

- `input_data`: dictionary with variables to be interpolated into prompts.

- `session_id`: UUID of the current session (auto-generated if omitted).

- `session_name`: optional label used in persistence and reporting.

- `session_created_at` / `session_updated_at`: ISO timestamps for creation and last update.

- `working_folder`: base directory for generated files and artifacts.

- `is_verbose`: enables detailed logs when `True`.

- `tools`: dictionary with currently enabled tools (default, optional, and corporate).

- `message_history`: structured list of questions, answers, attachments, and token usage.

- `history_window_size`: number of user/agent message pairs kept in short context (default: `5`).

- `retrievers`: RAG collections loaded from the `knowledge_base`.

- `response_callback`: optional function called after each consolidated response.

- `id`: read-only alias for the agent.

- `name`: agent's displayed name.

- `description`: agent description, purpose, and capabilities.

- `model`: returns the model name.

- `reasoning_effort`: sets the agent’s reasoning mode ("none" | "low" | "medium" | "high"), defaulting to "none".

**Public Methods**

- `__init__(..., exec_custom_tool_fn=None)`: instantiates the agent with active configuration and session, prepares factories for tools (default, corporate, and custom), defines callbacks and working directories, and calls `_setup_agent()` to build the OpenAI client, registries, and RAG retrievers.
  
  | Parameter                      | Description                                                | Default          |
  | ------------------------------ | ---------------------------------------------------------- | ---------------- |
  | `agent_config`                 | Agent configuration (model, prompt, tools, RAG sources).   | `AgentConfig()`  |
  | `input_data`                   | Auxiliary variables interpolated in prompts.               | `{}`             |
  | `session_id`                   | Session UUID; auto-generated if absent.                    | `uuid4()`        |
  | `session_name`                 | Friendly session name.                                     | `None`           |
  | `session_created_at`           | Timestamp of session creation.                             | `datetime.now()` |
  | `session_updated_at`           | Timestamp of last update.                                  | `datetime.now()` |
  | `working_folder`               | Base directory for `output/<session_id>`.                  | `Path.cwd()`     |
  | `is_verbose`                   | Enables detailed agent logs.                               | `False`          |
  | `response_callback`            | Optional function called after each consolidated response. | `None`           |
  | `get_builtin_custom_tools_fn`  | Alternative factory for loading corporate tools.           | `None`           |
  | `build_custom_tool_schemas_fn` | Additional builder for custom tool schemas.                | `None`           |
  | `exec_custom_tool_fn`          | Custom executor for custom tools.                          | `None`           |

- `to_json()`: exports `agent_config`, session metadata, derived state (tools, flags), and `message_history` into a dictionary ready for persistence or transport.

- `from_json(data, working_folder)`: class method that reconstructs configuration, session chronology, and history from the snapshot returned by `to_json()`, respecting the provided `working_folder` to rehydrate attachments and outputs.

- `add_subordinated_agent(subordinate_agent, role=None)`: associates another Oskar instance as a subordinate collaborator, allowing only one agent per name, replicating working directory and verbosity, and optionally updating the description with the given role.

- `get_pretty_messages_history(message_format='raw', list_subordinated_agents_history=False)`: formats history into blocks ready for visualization (`raw` or HTML), grouping question/answer pairs and optionally including subordinate agent interactions.

- `answer(question, message_format='raw', attached_files=None, model=None, reasoning_effort=None, action='chat', include_history=True, is_consult_prompt=False)`: prepares the prompt with session variables, ensures output folders exist, attaches files, sets reasoning effort, records input in history, builds tool schemas, and performs up to three iterations with the Responses API (or offline mode), returning content, metadata, attachments, and token usage.

- `delete_old_files(max_age_days=30)`: removes old files sent to the OpenAI API, returning a list of tuples (`id`, filename, creation date) for each removed item.

---

## Converters (`Oskar.converters`)

- `convert_csv_to_markdown_table(csv_data: str)`: converts raw CSV content (with header) into a Markdown table without an index column.

- `convert_dict_to_markdown(data: dict, md_path: str)`: serializes a dictionary into Markdown and writes it to the given path.

- `convert_docx_to_markdown(docx_path: str, md_path: str, media_dir: str | None = None)`: converts a DOCX into Markdown, exporting media to the specified folder.

- `convert_json_to_markdown(json_data: dict | list, doc_title: str = "Documento")`: serializes dictionaries or lists into structured Markdown text.

- `convert_json_to_csv(recs_json: list, filename: str)`: saves a list of dictionaries into a CSV file, sanitizing line breaks and truncating long strings.

- `convert_markdown_to_html(md_path: str, img_dir: str | None = None, insert_header: bool = True)`: generates HTML from Markdown, optionally adjusting image paths and inserting a default header.

- `convert_markdown_to_html_block(text: str, flag_insert_copy_to_clipboard_command: bool = True)`: converts Markdown text into HTML and also returns a list of detected code-block languages.

- `convert_markdown_to_pdf(md_filename: str, img_dir: str)`: renders Markdown as a PDF via `wkhtmltopdf`, reusing the generated intermediate HTML.

- `convert_pdf_to_markdown(pdf_path: str, md_path: str | None = None)`: extracts text from a PDF, attempts to identify headings, and returns the resulting Markdown file path.

- `convert_pptx_to_markdown(pptx_path: str, md_path: str, media_dir: str | None = None)`: converts PPTX slides to Markdown, extracting text, tables, images, and charts.

- `decode_file_from_str(encoded_data: str, out_path: str)`: decodes `b64:` or `b64+zlib:` strings into a binary file.

- `encode_file(pathname: str, compress: bool = True)`: reads a binary file and returns a JSON-safe encoded string, optionally compressing with zlib.

---

## Use Case Examples (`tests/`)

The scripts in `tests/` function as complete recipes. All can be executed directly (`python tests/<script>.py`) after configuring dependencies.

### 1. Basic Usage and Persistence

- `tests/1a_test_basico.py`: instantiates the agent, registers a usage callback, and sends a simple question.

```python
import json
from oskaragent.agent import Oskar
from oskaragent.agent_config import AgentConfig

ag_cfg = AgentConfig(model_settings={"history_window_size": 5})
agent = Oskar(agent_config=ag_cfg, is_verbose=True)
res = agent.answer("Who is the president of Brazil?")
print(json.dumps(res, indent=2, ensure_ascii=False))
```

- `tests/1b_test_history.py`: demonstrates `to_json()` and `Oskar.from_json(...)` to persist the full session history and restore it before the next question.

```python
import json
from oskaragent.agent import Oskar
from oskaragent.agent_config import AgentConfig

ag_cfg = AgentConfig(
    model_settings={"history_window_size": 5},
    system_prompt="You are a helpful assistant named oskaragent.",
)
agent = Oskar(agent_config=ag_cfg, is_verbose=True)
r1 = agent.answer("My favorite color is blue. What is your favorite color?")
snapshot = agent.to_json()
agent2 = Oskar.from_json(snapshot)
r2 = agent2.answer("What is my favorite color?")
print(json.dumps(r2, indent=2, ensure_ascii=False))
```

### 2. Internal Tools

- `tests/2a_test_tool_python.py`: enables `execute_python_code_tool` so the model can generate and run pandas/matplotlib scripts.

```python
import json
from oskaragent.agent import Oskar
from oskaragent.agent_config import AgentConfig

ag_cfg = AgentConfig(
    tools_names=["execute_python_code_tool"],
    system_prompt="Use execute_python_code_tool to run Python code.",
)
agent = Oskar(agent_config=ag_cfg, is_verbose=True)
res = agent.answer(
    "Create and run a bar chart with matplotlib using the execute_python_code_tool."
)
print(json.dumps(res, indent=2, ensure_ascii=False))
```

- `tests/2b_test_tool_calculator.py`: reinforces usage of `calculator_tool`, explicitly invoking it via `action='tool:calculator_tool'`.

```python
import json
from oskaragent.agent import Oskar
from oskaragent.agent_config import AgentConfig

ag_cfg = AgentConfig(
    tools_names=["calculator_tool"],
    system_prompt=(
        "You are an assistant focused on calculations. Whenever there is a mathematical expression, "
        "use the 'calculator_tool'."
    ),
)
agent = Oskar(agent_config=ag_cfg, is_verbose=True)
expression = "1024 + 12 + 1"
question = f"Calculate the expression below using calculator_tool: {expression}"
res = agent.answer(question, action="tool:calculator_tool")
print(json.dumps(res, indent=2, ensure_ascii=False))
```

- `tests/2c_test_savefile_tool.py`: adds `write_file_tool` to save artifacts to disk (e.g., a PlantUML diagram). The agent is instructed to use the tool whenever requested.

```python
import json
from oskaragent.agent import Oskar
from oskaragent.agent_config import AgentConfig

ag_cfg = AgentConfig(
    tools_names=["write_file_tool"],
    system_prompt=(
        "You are an agent named oskaragent. When asked to save content, "
        "use the 'write_file_tool'."
    ),
    model_settings={"history_window_size": 5},
)
agent = Oskar(agent_config=ag_cfg, is_verbose=True)
agent.answer("Generate a PlantUML diagram of a regular expression for international phone numbers.")
res = agent.answer("Save the PlantUML diagram to a file.")
print(json.dumps(res, indent=2, ensure_ascii=False))
```

### 3. File Upload and Manipulation

- `tests/3a_test_upload_md.py`: sends a Markdown file (`tests/sources/cristianismo.md`) so the agent can produce an objective summary. Uses `attached_files` with the absolute file path.

```python
from pathlib import Path
from oskaragent.agent import Oskar
from oskaragent.agent_config import AgentConfig

md_path = Path("sources/cristianismo.md").resolve()
agent = Oskar(agent_config=AgentConfig(), is_verbose=True)
result = agent.answer(
    question="Read the attached file and produce an objective summary in Portuguese.",
    attached_files=str(md_path),
)
print(result.get("content", ""))
```

- `tests/3b_test_upload_img.py`: attaches an image (`tests/sources/img_pent.png`) and requests a detailed description.

```python
from pathlib import Path
from oskaragent.agent import Oskar
from oskaragent.agent_config import AgentConfig

img_path = (Path(__file__).parent / "sources" / "img_pent.png").resolve()
agent = Oskar(agent_config=AgentConfig(), is_verbose=False)
result = agent.answer(
    question="Describe the attached image in detail in Portuguese.",
    attached_files=str(img_path),
)
print(result.get("content", ""))
```

- `tests/3c_test_upload_pdf_compare.py`: sends two PDFs simultaneously and asks for a comparative analysis. Demonstrates that `attached_files` accepts a list.

```python
from pathlib import Path
from oskaragent.agent import Oskar
from oskaragent.agent_config import AgentConfig

pdf1_path = Path("sources/GlobalThreatReport2024.pdf").resolve()
pdf2_path = Path("sources/comptia-state-of-cybersecurity-2025.pdf").resolve()
agent = Oskar(agent_config=AgentConfig(), is_verbose=True)
result = agent.answer(
    question="Create a comparative analysis of these two PDF documents in Portuguese.",
    attached_files=[str(pdf1_path), str(pdf2_path)],
)
print(result.get("content", ""))
```

### 4. Knowledge Retrieval (RAG)

- `tests/4_test_RAG.py`: activates a local Chroma source (`./tests/sources/vectorstore`) and explicitly calls `retriever_tool`.

```python
from oskaragent.agent import Oskar
from oskaragent.agent_config import AgentConfig

ag_cfg = AgentConfig(
    knowledge_base=[{"name": "psychology", "folder": "./sources/vectorstore", "collection": "local-rag"}],
)
agent = Oskar(agent_config=ag_cfg, is_verbose=True)
agent.answer("How many sessions were conducted?", action="tool:retriever_tool")
```

### 5. Multi-Agent System (MAS)

- `tests/5_test_MAS.py`: creates an orchestrator agent and adds a subordinate with specific knowledge using `add_subordinate_agent`, enabling the `ask_to_agent_tool`.

```python
import json
from oskaragent.agent import Oskar
from oskaragent.agent_config import AgentConfig

assist_cfg = AgentConfig(
    agent_id="AssistenteOskar",
    agent_name="Assistant of oskaragent",
    system_prompt="You know all employees of the company.",
)
agent_assistente = Oskar(agent_config=assist_cfg, is_verbose=True)

chefe_cfg = AgentConfig(agent_name="Boss", model_settings={"history_window_size": 5})
agent_chefe = Oskar(agent_config=chefe_cfg, is_verbose=True)

agent_chefe.add_subordinate_agent(
    agent_assistente,
    "Knows all company employees and their respective roles.",
)
res = agent_chefe.answer("What is Jacques’ job role?")
print(json.dumps(res, indent=2, ensure_ascii=False))
```

### 6. Corporate Integrations (`Oskar_cg_tools`)

- `tests/6a_test_cg_tool_Salesforce_OPO.py`: configures a sales persona and enables `get_salesforce_opportunity_info_tool` to query Salesforce opportunities.

```python
import json
from oskaragent.agent import Oskar
from oskaragent.agent_config import AgentConfig
from my_company_tools.agent_cg_tools import (
    build_cg_tool_schemas,
    exec_cg_tool,
    get_builtin_cg_tools,
)

system_prompt = "Act as an analyst specialized in the Salesforce Sales module."
ag_cfg = AgentConfig(
    system_prompt=system_prompt,
    tools_names=["get_salesforce_opportunity_info_tool"],
    model_settings={"history_window_size": 5},
)
agent = Oskar(
    agent_config=ag_cfg,
    get_builtin_custom_tools_fn=get_builtin_cg_tools,
    build_custom_tool_schemas_fn=build_cg_tool_schemas,
    exec_custom_tool_fn=exec_cg_tool,
    is_verbose=True,
)
res = agent.answer("Show the timeline for opportunity OPO-ORIZON-2024-08-0001")
print(json.dumps(res, indent=2, ensure_ascii=False))
```

- `tests/6b_test_cg_tool_Salesforce_ITSM.py`: enables `get_salesforce_case_info_tool` for IT support analysis and instructs the agent to answer in Markdown.

```python
import json
from oskaragent.agent import Oskar
from oskaragent.agent_config import AgentConfig
from my_company_tools.agent_cg_tools import (
    build_cg_tool_schemas,
    exec_cg_tool,
    get_builtin_cg_tools,
)

system_prompt = "Act as an analyst responsible for support tickets in Salesforce Service Cloud."
ag_cfg = AgentConfig(
    system_prompt=system_prompt,
    tools_names=["get_salesforce_case_info_tool"],
    model_settings={"history_window_size": 5},
)
agent = Oskar(
    agent_config=ag_cfg,
    get_builtin_custom_tools_fn=get_builtin_cg_tools,
    build_custom_tool_schemas_fn=build_cg_tool_schemas,
    exec_custom_tool_fn=exec_cg_tool,
    is_verbose=True,
)
res = agent.answer("Show the timeline for case 00042386")
print(json.dumps(res, indent=2, ensure_ascii=False))
```

- `tests/6c_test_custom_tool_SQL.py`: registers a custom SQL tool (`query_pessoas_tool`) via `AgentConfig.custom_tools`, illustrating parametric filters.

```python
import json
from oskaragent.agent import Oskar
from oskaragent.agent_config import AgentConfig
from my_company_tools.agent_cg_tools import (
    build_cg_tool_schemas,
    exec_cg_tool,
    get_builtin_cg_tools,
)

custom_tools_info = {
    "query_pessoas_tool": {
        "func_name": "search_database_tool",
        "description": "Search person data by name.",
        "connection_string": "...",
        "title": "People",
        "queries": [
            {
                "title": "People found (first 30)",
                "query": "select top 10 CO.Nome, CO.Email ... where ...",
            }
        ],
    }
}
ag_cfg = AgentConfig(custom_tools=custom_tools_info, model_settings={"history_window_size": 5})
agent = Oskar(
    agent_config=ag_cfg,
    get_builtin_custom_tools_fn=get_builtin_cg_tools,
    build_custom_tool_schemas_fn=build_cg_tool_schemas,
    exec_custom_tool_fn=exec_cg_tool,
    is_verbose=True,
)
res = agent.answer('List in table format the people whose names match "José Carlos".')
print(json.dumps(res, indent=2, ensure_ascii=False))
```

- `tests/6d_test_custom_tool_DOC_SQL.py`: similar to the previous example, but builds multiple queries (ticket details and associated emails) and uses `input_data` for interpolation.

```python
import json
from oskaragent.agent import Oskar
from oskaragent.agent_config import AgentConfig
from my_company_tools.agent_cg_tools import (
    build_cg_tool_schemas,
    exec_cg_tool,
    get_builtin_cg_tools,
)

custom_tools_info = {
    "get_support_case_info_tool": {
        "func_name": "query_database_tool",
        "description": "Retrieve details of a technical support case.",
        "connection_string": "...",
        "title": "ITSM Support Case",
        "queries": [
            {"title": "Case", "query": "select top 1 CH.NumeroChamado ... where CH.NumeroChamado = '{KEY}'"},
            {"title": "Emails", "query": "select CH.NumeroChamado, MAIL.Assunto ... where CH.NumeroChamado = '{KEY}'"},
        ],
    }
}
ag_cfg = AgentConfig(custom_tools=custom_tools_info, model_settings={"history_window_size": 5})
agent = Oskar(
    agent_config=ag_cfg,
    input_data={"ticket": 42555},
    get_builtin_custom_tools_fn=get_builtin_cg_tools,
    build_custom_tool_schemas_fn=build_cg_tool_schemas,
    exec_custom_tool_fn=exec_cg_tool,
    is_verbose=True,
)
res = agent.answer("Provide a synthesis of ticket {ticket}.")
print(json.dumps(res, indent=2, ensure_ascii=False))
```

### 7. Analytics and BI

- `tests/7a_test_BI_CSV.py`: uses `working_files` pointing to `tests/sources/Basileia.csv` and requests an analysis with a chart generated by the Python tool.

```python
import json
from oskaragent.agent import Oskar
from oskaragent.agent_config import AgentConfig

ag_cfg = AgentConfig(
    working_files=[
        {
            "name": "basileia",
            "description": "Temperature data from the city of Basel",
            "pathname": "./sources/Basileia.csv",
        }
    ],
)
agent = Oskar(agent_config=ag_cfg, is_verbose=True)
res = agent.answer(
    "Create a line chart showing the evolution of the average temperature over the years."
)
print(json.dumps(res, indent=2, ensure_ascii=False))
```

- `tests/7b_test_BI_SQL.py`: provisions a relational database via `working_databases`, generates a CSV in the session folder, and performs visualizations on the imported data.

```python
import json
from oskaragent.agent import Oskar
from oskaragent.agent_config import AgentConfig

ag_cfg = AgentConfig(
    working_databases=[
        {
            "name": "Tickets",
            "description": "Information about technical support tickets",
            "connection_string": "Driver={ODBC Driver 17 for SQL Server};Server=CGSQL07;Database=DB_KPI;Uid=relkpi;Pwd=tele13",
            "query": "select top 100 CH.NumeroChamado ...",
        }
    ],
)
agent = Oskar(agent_config=ag_cfg, is_verbose=True)
res = agent.answer("Create a bar chart by Manufacturer.")
print(json.dumps(res, indent=2, ensure_ascii=False))
```

---

## Best Practices

- Use `is_verbose=True` during development to track tool calls and token usage.

- Always instruct the agent via `system_prompt` when a tool must be prioritized or when specific policies apply.

- Remember to name files generated by responses following the pattern `<message_id>-description.ext`; the `answer` method automatically collects those artifacts.

With these examples, you can adapt the `Oskar` class to any workflow: support, BI, corporate integrations, multi-agent setups, and multimodal artifact generation.

---

## Dependencies (`requirements.txt`)

The libraries below are versioned exactly as in `requirements.txt` and cover the minimum stack required to run the agent and tools.

### Core agent + Knowledge Base

    openai==2.7.1
    faiss-cpu==1.12.0

### Data tools used by `execute_python_code_tool`

    pandas==2.3.0
    numpy==2.3.4
    seaborn==0.13.2
    matplotlib==3.10.7
    tabulate==0.9.0 (necessário para `DataFrame.to_markdown`)

### Document conversion and generation

    pypdf==6.1.3
    pdfkit==1.0.0 (requer `wkhtmltopdf` instalado)
    pdfminer.six==20250506
    python-docx==1.2.0
    markdown2==2.5.4
    beautifulsoup4==4.14.2

### External integrations

    simple-salesforce==1.12.9

### Misc utilities

    pyodbc==5.3.0
    PyYAML==6.0.3
    colorama==0.4.6
