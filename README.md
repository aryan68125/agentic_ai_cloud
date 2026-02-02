# Aryabhatta 
This project is a fault-aware AI prompt processing service built with FastAPI.
It accepts user prompts, applies an agent-specific system prompt, calls a Hugging Face LLM, and atomically stores both the user prompt and AI response only when the LLM call succeeds.

The system is designed to be transaction-safe, network-failure tolerant, and cleanly extensible for production workloads.

At the end what you will see is a basic version of relevance 

I will be adding tools support as well ... 

## How to run this project? 
go to this directory
```bash
cd /home/aditya/github/agentic_ai_cloud
```
type this command to run your uvicorn asgi server
```bash
uvicorn app.main:app --reload
```
This command will run your back-end server in localhost ip but if you want to run your back-end on another ip then simply use the command below
```bash
uvicorn app.main:app --host <yout_laptop's_ip> --port <your_port_number> --reload
```
example : 
```bash
uvicorn app.main:app --host 192.168.1.204 --port 8000 --reload
```
This will allow you to serve your server on a local network over wifi if you want.

## Environment variables
You will have to set the Environment variables ```.env``` related to hugging face api and postgreSql
```bash
HUGGING_FACE_AUTH_TOKEN = hf_mLJifvMK1234567890trAlknGiJDVnVKmL
HF_API_URL = https://router.huggingface.co/v1/chat/completions

DB_CONNECTION_STRING = postgresql://<user_name>:<password>@<db_ip>:5432/<db_name>
```
the ```.env``` file must be at the root project directory

## Managing database migrations 
For this project I am using SQL alchemy to :
- Define the database tables
- Insert , Update , Fetch and Delete the records from the table
and alembic to : 
- Manage the database migrations and schema changes like django

In order to manage db_migrations in alembic 
- Step 1 : go to this dir /home/aditya/github/agentic_ai_cloud/app
```bash
cd /home/aditya/github/agentic_ai_cloud/app
```
- Step 2 : Initialize alembic
```bash
alembic init alembic
```
- Step 3 : Make changes to this ```app/alembic/env.py``` file. I have already made changes to this file you don't have to do it for this project. I am only telling your this so that if you ever want to use alembic to manage your database migrations in fast-api or in flask you can use the code below. 

One thing to note is that the code below will find your .env file and extract the database connection string from there 
```python
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

import os
import sys
from logging.config import fileConfig

from decouple import config as env_config

from app.database.base import Base
from app.models.db_table_models.ai_agent_table import AIAgentName

from sqlalchemy import create_engine

# ---- ADD PROJECT ROOT TO PYTHON PATH ----
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    DATABASE_URL = env_config("DB_CONNECTION_STRING")
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```
- Step 4 : use the commands below to run the migrations (This particular command is to create the table before db operation)
```bash
cd /home/aditya/github/agentic_ai_cloud
alembic revision --autogenerate -m "create ai_agent_table"
alembic -c alembic.ini upgrade head
```

**NOTE:** Make sure that your project structure looks something like this 
```bash
.
├── alembic
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions
│       ├── 027e8d073bf8_create_ai_agent_table.py
│       ├── 20178cf2ef3e_create_user_prompt_table.py
│       ├── 37463c85173b_create_tables.py
│       ├── 4778aedf35a2_create_ai_agent_table.py
│       ├── 53e83fac2395_create_system_prompt_table.py
│       ├── 5cffdaf15574_create_llm_prompt_response_table.py
│       ├── 6146d779b733_create_system_prompt_table.py
│       ├── b20ac25ffcd0_create_system_prompt_table.py
│       ├── c3c1c2bd75c0_create_system_prompt_table.py
│       ├── c7af7dbf402a_create_user_prompt_table.py
│       ├── ff1251aeb20c_create_user_prompt_table.py
├── alembic.ini
├── app
│   ├── apis
│   │   ├── agent_api.py
│   │   ├── hugging_face_api.py
│   │   ├── __init__.py
│   │   ├── prompt_apis.py
│   ├── configs
│   │   ├── config.py
│   │   ├── __init__.py
│   ├── controllers
│   │   ├── agent_controllers.py
│   │   ├── hugging_face_ai_model_controllers.py
│   │   ├── __init__.py
│   │   ├── prompt_controllers.py
│   ├── database
│   │   ├── base.py
│   │   ├── db_session.py
│   │   ├── db_transaction_exception_handler.py
│   ├── dependencies
│   │   ├── controller_dependencies.py
│   │   ├── __init__.py
│   ├── __init__.py
│   ├── logs
│   │   ├── debug
│   │   │   └── debug.log
│   │   ├── error
│   │   │   └── error.log
│   │   └── info
│   │       └── info.log
│   ├── main.py
│   ├── models
│   │   ├── api_request_response_model
│   │   │   ├── __init__.py
│   │   │   ├── request_models.py
│   │   │   └── response_models.py
│   │   ├── class_request_model
│   │   │   ├── class_request_model.py
│   │   │   └── __init__.py
│   │   ├── class_return_model
│   │   │   ├── __init__.py
│   │   │   └── services_class_response_models.py
│   │   ├── db_table_models
│   │   │   ├── ai_agent_table.py
│   │   │   ├── __init__.py
│   │   │   ├── llm_prompt_response_table.py
│   │   │   ├── system_prompt_table.py
│   │   │   └── user_prompt_table.py
│   │   ├── __init__.py
│   ├── repositories
│   │   ├── ai_agent_repository.py
│   │   ├── __init__.py
│   │   ├── llm_prompt_response_repository.py
│   │   ├── system_prompt_repository.py
│   │   └── user_prompt_repository.py
│   ├── services
│   │   ├── process_hugging_face_ai_prompt.py
│   │   ├── process_huggingface_ai_response.py
│   └── utils
│       ├── db_operation_type.py
│       ├── error_messages.py
│       ├── field_descriptions.py
│       ├── get_base_url.py
│       ├── hugging_face_ai_model_enum.py
│       ├── __init__.py
│       ├── logger_info_messages.py
│       ├── logger.py
│       ├── log_initializer.py
│       ├── logs_re_namer.py
│       ├── saved_sql_query
│       └── success_messages.py
├── README.md
└── requirements.txt
```
## The way I designed the project's flow 
### My design philosophy
This project prioritizes correctness over cleverness.

I intentionally avoided premature optimizations (Redis, queues) and focused on:
- clear flow
- strong invariants
- observable behavior (logs + timings)

### Repositories 
```bash
├── repositories
│   │   ├── ai_agent_repository.py
│   │   ├── __init__.py
│   │   ├── system_prompt_repository.py
│   │   └── user_prompt_repository.py
```
The way I designed my repositories:
- These repositories will be responsible for carrying out simple CRUD or complex database queries only
- It return structured result objects
- It also handles the database level exceptions and then pass those exceptions back to the controller layer.
- It own exactly one table in the database and does not know about other tables in the database
- It validate inputs for persistence

### Controllers
```bash
│   ├── controllers
│   │   ├── agent_controllers.py
│   │   ├── hugging_face_ai_model_controllers.py
│   │   ├── __init__.py
│   │   ├── prompt_controllers.py
```
The way I designed my controllers : 
- They do not know SQLAlchemy
- They do not talk to the database
- They do not know about hugging face 
- They are only responsible to orchestrate the services and repositories according to the business logic 
- They translate the result after processing comming from the services and repositories into HTTP 

I made sure that : 
- Repositories return RepositoryClassResponse
- Repositories do not raise HTTPException
- Repositories do not know about FastAPI
- Repositories don’t mix multiple tables casually

### services
```bash
│   ├── services
│   │   ├── process_huggingface_ai_response.py
│   │   ├── process_prompt.py
```
I made this service layer to:
- Orchestrate multiple repositories
- Call external systems
- Implement workflows
- Enforce business sequencing
- Handle retries/timeouts
- Return domain-level results

### apis
```bash
│   ├── apis
│   │   ├── agent_api.py
│   │   ├── hugging_face_api.py
│   │   ├── __init__.py
│   │   ├── prompt_apis.py
```
What I wanted this layer to do:
- define HTTP routes
- bind request/response models
- do dependency injection
- log request metadata
- forward the call to a controller

They do not:
- implement business rules
- talk to repositories
- talk to Hugging Face
- contain workflow logic

Each API file corresponds to:
- a domain concept
- a controller
- a use-case family

API modules define HTTP contracts and routing. They delegate all behavior to controllers and services and remain free of business logic.

### database 
```bash
│   ├── database
│   │   ├── base.py
│   │   ├── db_session.py
│   │   ├── db_transaction_exception_handler.py
```
In this project I intentionally keep database access simple, explicit, and predictable.

Rather than hiding database behavior behind abstractions, I chose the design that makes transaction boundaries and failure behavior obvious to anyone reading the code.

#### **Single source of database access**
The project exposes one canonical way to access the database.
- A single SQLAlchemy engine
- A single session factory
- A single dependency (get_db) used everywhere

This ensures:
- consistent connection pooling
- predictable session lifecycle
- no accidental multiple engines or sessions

All database access flows through one controlled entry point to avoid hidden state and connection leaks.

Transactions are not started implicitly inside repositories.

Instead:
- transactions are started at the service or controller level
- repositories assume a valid session already exists
Rule of thumb is 
- Repositories describe what to write.
- Services decide when it is safe to commit.

Why this matters:
- external calls (like Hugging Face) are never executed inside DB transactions
- slow or failing network calls cannot lock database resources
- rollback behavior is deterministic

Failure-driven rollback using exceptions
- carries a structured domain response
- automatically triggers a rollback when raised inside a transaction block
- avoids mixing HTTP concerns into database logic

# Project's working
## How this project works?
- User sends a prompt to the API
- System fetches the agent’s system prompt
- Prompt is sent to Hugging Face LLM
- Response is validated
- Only after success, both:
    - user prompt
    - LLM response are saved inside a single DB transaction
- If anything fails → automatic rollback
## What I prevented?
- No partial writes if LLM fails
- No DB locks during slow network calls
- No inconsistent prompt–response pairs
- Clear failure boundaries
- Production-safe transaction handling

## Hugging face LLM context management mechanism
### Problem I am trying to solve
Large Language Models (LLMs) accessed via the Hugging Face Inference API are stateless by default.
Each request is processed independently, meaning the model does not “remember” previous interactions unless conversation history is explicitly sent with every request.

For an internal, agent-based platform where:
- multiple employees build their own AI agents,
- agents are expected to hold conversational continuity,
- performance and simplicity are critical,

I needed a reliable, predictable, and controllable way to maintain context without introducing unnecessary complexity or latency.

### I went with **Sliding Window Context**
I implemented server-side sliding window context management, where:
- All user prompts and assistant responses are persisted in a database.
- For each new user request, a bounded subset of recent conversation turns is reconstructed and sent to the LLM.
- Older context is automatically dropped when token limits are reached.

This approach ensures:
- Deterministic behavior
- Full control over what the model sees
- Compatibility with any Hugging Face chat-capable model

### Why This Approach?
#### Why NOT rely on model-side memory?
- Hugging Face API does not provide persistent conversational memory
- Model state cannot be trusted across requests
- Scaling agents would require session pinning (bad for performance)
#### Why NOT store the entire conversation every time?
- Token limits would be exceeded quickly
- Cost and latency increase linearly with conversation length
- Older messages often lose relevance
#### Why Sliding Window?
- Sliding window context is:
- Simple to reason about
- Predictable under load
- Easy to debug
- Model-agnostic
- Safe for internal enterprise use
#### High level LLM context management system architecture
```bash
User Request
   ↓
Fetch System Prompt
   ↓
Fetch Conversation History
   ↓
Context Builder (token-bounded)
   ↓
Hugging Face LLM
   ↓
Persist Response
```
### Context Window Construction Logic
The context is built using three components:
#### System Prompt (Always Included)
The system prompt defines:
- Agent behavior
- Safety constraints
- Output format expectations

This is always injected as the first message.

#### Conversation History (Sliding Window)
Conversation turns are stored as:
- user messages
- assistant messages

The builder:
- Iterates from most recent → oldest
- Adds messages until the token budget is exhausted
- Stops cleanly when the budget is reached

Older messages are intentionally dropped, not truncated.

#### New User Prompt
The current user input is always appended last, ensuring:
- The model responds to the latest intent
- Context does not overshadow the new request

#### Token budget strategy
| Purpose                     | Tokens |
| --------------------------- | ------ |
| Total allowed               | 3000   |
| Reserved for model response | 800    |
| Available for history       | 2200   |

This prevents:
- Model cut-offs
- Partial responses
- Unpredictable truncation by the provider

### Current Token Counting Strategy (v1)
At present, token usage is estimated using a naive word-based counter:
```python
len(text.split())
```
#### Why this is acceptable (for now):
- Fast
- Zero dependencies
- Good enough for early-stage internal tooling
- Keeps the architecture flexible

#### Known Limitations (Intentional)
We explicitly acknowledge the following limitations:
- No long-term memory
    - Facts like names or roles are not permanently remembered
    - Once context slides out, the model forgets
- Naive token estimation
    - Actual tokenizer behavior varies by model
    - This may slightly over/under-estimate capacity
- No semantic relevance scoring
    - Messages are included purely by recency
    - Not by importance or topic relevance

These are design trade-offs, not oversights.

### Future Improvements (Planned, Not Premature)
This design is intentionally extensible. Planned upgrades include:
#### Accurate Token Counting
Replace the naive counter with:
- Hugging Face tokenizer (model-specific)
- or tiktoken for OpenAI-compatible models

This will allow:
- Precise budgeting
- Model-aware limits

#### Structured Long-Term Memory
Introduce a separate agent memory store for:
- Facts (“Aditya is a Python developer”)
- Preferences
- Roles

This memory will be:
- Explicitly injected
- Curated
- Not dependent on conversation recency

#### Relevance-Based Context Selection
Instead of pure recency:
- Score messages by semantic similarity
- Include fewer but more relevant turns
- Reduce noise in long conversations

#### Observability Enhancements
- Per-message token usage logs
- Context diffs between requests
- Debug flags to inspect dropped messages

### Tool orchestration 
For LLm to be able to use the tools for agentic work I chose MCP server 
```bash
Application
 ├─ Agent config (DB)
 ├─ system_prompt (DB)
 ├─ model selector
 ├─ MCP Client
 │    └─ MCP Server
 │         ├─ search tool
 │         ├─ email tool
 │         ├─ db tool
 │         └─ filesystem tool
 └─ Model (Claude / Llama / etc...)

```
What is MCP? 

MCP is a Model Context Protocol. MCP standardizes how an LLM runtime talks to external tools + data sources.

MCP defines:
- how tools are exposed
- how context is injected
- how models request actions
- how responses are structured

MCP server fits this project's use case and what I am trying to do
- per-agent system prompts
- per-agent tool allow/deny
- per-agent model selection
- strong control (what model can/can’t do)
- persistence (DB)
- HF compatibility
- future multi-model support