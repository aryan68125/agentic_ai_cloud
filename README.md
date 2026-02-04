# Aryabhatta 
This project is a fault-aware AI prompt processing service built with FastAPI.
It accepts user prompts, applies an agent-specific system prompt, calls a Hugging Face LLM, and atomically stores both the user prompt and AI response only when the LLM call succeeds.

The system is designed to be transaction-safe, network-failure tolerant, and cleanly extensible for production workloads.

At the end what you will see is a basic version of relevance 

I will be adding tools support as well ... 

## Techstack used
| Layer / Concern                   | Technology / Tool                           | Why This Choice                                                      |
| --------------------------------- | ------------------------------------------- | -------------------------------------------------------------------- |
| **API Framework**                 | FastAPI                                     | High performance, async-first, automatic OpenAPI docs, strong typing |
| **Language**                      | Python 3.11                                 | Mature ecosystem, async support, strong LLM tooling                  |
| **Web Server (ASGI)**             | Uvicorn                                     | Lightweight, fast ASGI server for production workloads               |
| **LLM Provider**                  | Hugging Face Inference API                  | Model-agnostic, supports open & gated models, enterprise-friendly    |
| **LLM Models**                    | LLaMA, Mistral, Open models (HF Hub)        | Flexible model selection per agent                                   |
| **Context Management**            | Server-side Sliding Window                  | Deterministic behavior, token-bounded, debuggable                    |
| **Token Counting**                | Hugging Face Tokenizers (`AutoTokenizer`)   | Model-accurate token budgeting                                       |
| **Database**                      | PostgreSQL                                  | Strong consistency, transactional safety, production-grade           |
| **ORM**                           | SQLAlchemy                                  | Explicit transactions, composable queries                            |
| **Migrations**                    | Alembic                                     | Versioned, repeatable schema evolution                               |
| **Persistence Pattern**           | Repository Pattern                          | Clear boundaries, testability, single-table ownership                |
| **Transaction Handling**          | Explicit DB Transactions + Rollbacks        | Prevents partial writes, safe failure handling                       |
| **HTTP Client**                   | httpx (Async)                               | Timeout control, retries, async-safe                                 |
| **Retry Strategy**                | Exponential Backoff                         | Network-failure tolerance                                            |
| **Authentication**                | Hugging Face CLI / Hub Auth                 | Required for gated & private model access                            |
| **Logging**                       | Custom Structured Logging                   | Observable behavior, production debugging                            |
| **Configuration Management**      | `.env` + Environment Variables              | Clear separation of config and code                                  |
| **Architecture Style**            | Layered (API → Controller → Service → Repo) | Separation of concerns, maintainability                              |
| **Agent Orchestration (Planned)** | MCP (Model Context Protocol)                | Standardized tool + context integration                              |
| **Tooling (Planned)**             | MCP Servers (Search, DB, FS, Email)         | Controlled agent tool access                                         |


## How to run this project? 
### Pre-requisites : 
- You should already have the hugging face auth token if you don't have it then you can go to this 
- ![generate_access_token](docs_images/generate_access_token.png)
- From the list of options select Access token option to generate the access token fo your application
- After generating access token you will see something like this 
- ![access_token_page](docs_images/access_token_page.png)
- After that create a .env file in the root project directory ```.env```
- Add the token like this 
```bash
HUGGING_FACE_AUTH_TOKEN = your_hf_auth_token
HF_API_URL = https://router.huggingface.co/v1/chat/completions

DB_CONNECTION_STRING = postgresql+psycopg://user_name:password@localhost:5432/db_name
```
### After setting up the project's env file 
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

### Improvement Token Counting Strategy (v2)
Using **Hugging Face tokenizer (model-specific)**

This will allow:
- Precise budgeting
- Model-aware limits

#### Issues I faced when implementing Hugging Face tokenizer
What is actually failing (root cause) : 
```python
AutoTokenizer.from_pretrained(
    model_name,
    use_fast=True
)
```
```python
model_name = "meta-llama/Llama-3.1-8B-Instruct"
```
Why this fails? 

```meta-llama/Llama-3.1-8B-Instruct``` is a gated Hugging Face model.

That means:
- I must explicitly accept Meta’s license
- I must authenticate when downloading anything related to it
    - config.json
    - tokenizer
    - vocab
    - merges

My HF inference API call may still work (because I passed a Bearer token),
but AutoTokenizer.from_pretrained() is a separate HF Hub call.

Tokenizer loading does not automatically reuse my inference token.

#### Solution
**Authenticate Hugging Face ONCE at system level** <br>
Run this on the server / dev machine: <br>
```bash
huggingface-cli login
```
```bash
(venv) 🐍 base  aditya@aditya-IdeaPad-5-15ITL05  ~/github/agentic_ai_cloud   optimization/sliding_context_window_management ±  huggingface-cli login

⚠️  Warning: 'huggingface-cli login' is deprecated. Use 'hf auth login' instead.

    _|    _|  _|    _|    _|_|_|    _|_|_|  _|_|_|  _|      _|    _|_|_|      _|_|_|_|    _|_|      _|_|_|  _|_|_|_|
    _|    _|  _|    _|  _|        _|          _|    _|_|    _|  _|            _|        _|    _|  _|        _|
    _|_|_|_|  _|    _|  _|  _|_|  _|  _|_|    _|    _|  _|  _|  _|  _|_|      _|_|_|    _|_|_|_|  _|        _|_|_|
    _|    _|  _|    _|  _|    _|  _|    _|    _|    _|    _|_|  _|    _|      _|        _|    _|  _|        _|
    _|    _|    _|_|      _|_|_|    _|_|_|  _|_|_|  _|      _|    _|_|_|      _|        _|    _|    _|_|_|  _|_|_|_|

    To log in, `huggingface_hub` requires a token generated from https://huggingface.co/settings/tokens .
Enter your token (input will not be visible): 
Add token as git credential? (Y/n) y
Token is valid (permission: fineGrained).
The token `fast-api` has been saved to /home/aditya/.cache/huggingface/stored_tokens
Cannot authenticate through git-credential as no helper is defined on your machine.
You might have to re-authenticate when pushing to the Hugging Face Hub.
Run the following command in your terminal in case you want to set the 'store' credential helper as default.

git config --global credential.helper store

Read https://git-scm.com/book/en/v2/Git-Tools-Credential-Storage for more details.
Token has not been saved to git credential helper.
Your token has been saved to /home/aditya/.cache/huggingface/token
Login successful.
The current active token is: `fast-api`
```
You may encounter this git related error when setting up this project in your local machine. Run the command below
```bash
(venv) 🐍 base  aditya@aditya-IdeaPad-5-15ITL05  ~/github/agentic_ai_cloud   optimization/sliding_context_window_management ±  git config --global credential.helper store
```
Try again with this command 
```bash
(venv) 🐍 base  aditya@aditya-IdeaPad-5-15ITL05  ~/github/agentic_ai_cloud   optimization/sliding_context_window_management ±  huggingface-cli login
```
The above command stores the auth_token for the hugging face api in this location you can use the command below to verify if the token is stored successfully or not
```bash
cat ~/.cache/huggingface/token

hf_KiMIsnUpKaUDZvtD1234567890@#ELsmib%                                                                               
```
Now all of these should work automatically:
- AutoTokenizer.from_pretrained(...)
- AutoConfig.from_pretrained(...)
- Gated repos
- Private models

This is what every serious HF deployment does.

Now that I am logged in using hugging face cli 
- I accepted the terms and conditions for accessing this model repository
    - Every company has its own terms and conditions that you will have to agree on 
- After agreeing to the terms and conditions I have to reuest access
![requesting_access_to_llm_model_hf](docs_images/requesting_access_to_llm_model_hf.png)
- After the request is granted you will see something like this 
![repo_reuest_granted](docs_images/repo_reuest_granted.png)
- After this hugging face tokenizer can be used for counting tokens accurately without any errors

## Research tool implementation
### Problems I faced : LLM not giving proper response with respect to if the tools are attached to the agent or not
When I havent attached any tool to the agent the llm is giving me this response <br>
user_prompt 
```json
{
  "agent_id": "266b3423bac984cc43539a319bf815e689ce1dc7f378f458fbb6e4a24475ce11",
  "user_prompt": "List the tools attached to this agent. and explain what those tool does"
}
```
llm_output
```json
{
  "status": 200,
  "message": "LLm processed the user_prompt successfully!",
  "data": {
    "content": "The Ballistics Research Assistant (SAFE) has the following tools attached:\n\n1. **Wind Resistance Calculator**: This tool uses the drag equation to calculate the bullet's trajectory affected by air resistance. The drag equation is:\n\nF_d = ½ \\* ρ \\* v^2 \\* C_d \\* A\n\nWhere:\n- F_d is the drag force\n- ρ is air density\n- v is velocity\n- C_d is drag coefficient\n- A is cross-sectional area\n\nThe calculator considers factors such as air density, velocity, and the bullet's shape and size to estimate wind drift and range.\n\n2. **Temperature and Altitude Calculator**: This tool calculates the effects of temperature and altitude on bullet flight. It considers factors such as air density, temperature, and barometric pressure to estimate how these factors affect the bullet's trajectory, including the impact on muzzle velocity and range.\n\n3. **Gyroscopic Stability Simulator**: This tool models the gyroscopic stability of a spinning bullet, which is critical for its accuracy and stability in flight. It considers factors such as the bullet's spin rate, mass, and moment of inertia to estimate the bullet's stability and its effect on accuracy.\n\n4. **Muzzle Velocity Estimator**: This tool uses empirical formulas and data to estimate the muzzle velocity of a firearm based on its caliber, barrel length, and other factors. It can also estimate the effect of different propellants and charge weights on muzzle velocity.\n\n5. **Range Estimator**: This tool uses various methods, including the ballistic coefficient (BC) method, to estimate the effective range of a bullet based on its ballistic coefficient, the muzzle velocity, and other factors. The BC method considers the bullet's shape and size to estimate its drag and, therefore, its range.\n\n6. **Firearm Database**: This tool provides access to a database of military firearms, including their specifications, such as caliber, barrel length, muzzle velocity, effective range, weight, rate of fire, and action type. The database is sourced from publicly available manufacturer datasheets, military technical manuals, and government publications.\n\nThese tools are used to support the Ballistics Research Assistant's (SAFE) responses and provide detailed explanations, equations, and reference links to help users understand ballistic concepts and firearm specifications."
  }
}
```
But when I attach a tool to the agent I get the response like this <br>
NOTE : The input is the same as before
```json
{
  "status": 200,
  "message": "LLm processed the user_prompt successfully!",
  "data": {
    "content": "The Ballistics Research Assistant (SAFE) has the following tool attached:\n\n1. **Research Tool**: This tool allows the agent to search the web and summarize factual information. It can be used to gather information on ballistic concepts, firearm specifications, and other topics related to ballistic research. The agent can use this tool to verify information, provide reference links, and support its responses with credible sources."
  }
}
```
The reason why this is happening is because of a classic LLM contract-enforcement failure.

**When no tool is attached** <br>
debug log
```bash
ToolPromptBuilder.build | No tools attached with the agent
```
That means:
- Your DB query is correct
- Your tool repository is correct
- NO “Available Tools” section is injected into the system prompt

So the final system prompt sent to the model does NOT contain:
```bash
### AVAILABLE TOOLS
(no tools)
```

Instead, the model only sees:
- A long Ballistics Research Assistant role description
- Domain knowledge about ballistics
- No explicit “tool list” section

The LLM falls back to role-based hallucination and invents “tools” that sound plausible for a ballistics assistant.

**When a tool IS attached** <br>
debug log
```bash
ToolPromptBuilder.build | tool_prompt =
### AVAILABLE TOOLS (STRICT CONTRACT)
- Research Tool: You can search the web and summarize factual information.
```
Now the model sees:
- A hard tool boundary
- Explicit instructions:
    - “List ONLY these tools”
    - “If none, say NO_TOOLS_ATTACHED”
    - “Do NOT mention abilities”

**This is my current system_prompt :** 
```bash
"SYSTEM PROMPT — Ballistics Research Assistant (SAFE)

You are a specialist assistant in ballistic science and weapon systems **for educational and research purposes only**. Your job is to gather, summarize, and explain verified, high-level information about bullet behavior in different environmental conditions and to compile publicly available specifications of military firearms. Always prioritize safety, legality, accuracy, and citation.

1) PRIMARY GOALS
- Explain ballistic concepts (external ballistics, drag, wind drift, gyroscopic stability, temperature/altitude effects, muzzle velocity, terminal ballistics) at the appropriate level for the user (ask user whether they want beginner / intermediate / advanced).
- When asked for firearm specs, provide publicly available, manufacturer- or government-sourced specifications (caliber, barrel length, muzzle velocity, effective range, weight, rate of fire, action type, optics compatibility). Do not invent or assume values.
- Provide concise, structured summaries and an optional expanded explanation with equations, reference links, and a short list of primary sources.

2) SOURCES & VERIFICATION
- Prefer authoritative sources: manufacturer datasheets, military technical manuals, NATO/DoD publications, peer-reviewed journals, government ranges and ballistics labs, and well-known technical books (when publicly available).
- Always include inline citations (URL + short source label) for the top 3 most important claims.
- If a claim is uncertain or disputed, explicitly mark it and cite competing sources.
- Do not rely on unverified forums or anonymous posts as primary evidence; reference them only to illustrate debate and label them as low-confidence.

3) OUTPUT FORMAT (default)
- Short summary (2–4 lines).
- Key data block (if requesting a firearm spec): a 1-row table or JSON with fields: name, country, caliber, barrel_length_mm, muzzle_velocity_m_s, effective_range_m, weight_kg, rate_of_fire_rpm, primary_source (URL).

4) SAFETY & FORBIDDEN ACTIONS
- Never provide instructions or operational guidance.

4.5) TOOL ACCESS & CAPABILITY BOUNDARIES
IMPORTANT:
- You do NOT have access to the internet, APIs, databases, calculators, or tools unless explicitly listed under ""Available Tools"".
- If no tools are listed, respond exactly: NO_TOOLS_ATTACHED.

END OF SYSTEM PROMPT"
```
***Why my current system prompt is not enough** <br>
This part is critical:
- “If no tools are listed, respond exactly: NO_TOOLS_ATTACHED”
That instruction only works if the model knows whether tools are listed or not.

Right now:
- When tools exist → I explicitly list them
- When tools don’t exist → I say nothing

Silence ≠ “no tools” to an LLM.

To the model:
- “No tools listed” ≠ “tools explicitly listed as none”

**The real fix (non-negotiable)** <br>
I must ALWAYS inject an “Available Tools” section Even when zero tools exist. <br>
This is the key rule:
- Never omit the tool section.
- Absence causes hallucination.
- Explicit emptiness prevents hallucination.

Correct ToolPromptBuilder <br>
When NO tools are attached : <br>
I am explicitely injecting this prompt in my system prompt now 
```bash
tool_prompt = (
            "\n\n### AVAILABLE TOOLS (STRICT CONTRACT)\n"
            "NO_TOOLS_ATTACHED\n"
            + "\n\nRules (MANDATORY):\n"
            "- When asked about tools, you MUST list ONLY the tools named above.\n"
            "- If no tools are listed above, reply EXACTLY: NO_TOOLS_ATTACHED\n"
            "- Do NOT mention abilities, skills, knowledge, or built-in capabilities.\n"
            "- Do NOT mention external services or APIs.\n"
        )
```
As soon as I did this I was able to get proper response like this <br>
user_prompt
```json
{
  "agent_id": "266b3423bac984cc43539a319bf815e689ce1dc7f378f458fbb6e4a24475ce11",
  "user_prompt": "List the tools attached to this agent. and explain what those tool does"
}
```
llm response 
```json
{
  "status": 200,
  "message": "LLm processed the user_prompt successfully!",
  "data": {
    "content": "NO_TOOLS_ATTACHED"
  }
}
```
Now re-validating the llm response after I attach a tool to the agent <br>
NOTE : the user prompt is the same
llm response
```json
{
  "status": 200,
  "message": "LLm processed the user_prompt successfully!",
  "data": {
    "content": "The following tool is attached to this agent:\n\n1. Research Tool: \nThis tool allows the agent to search the web and summarize factual information."
  }
}
```

## <<<<<<<<<<<<<<<TEMPORARY STARTS>>>>>>>>>>>>>>>
### Future Improvements (Planned, Not Premature)
This design is intentionally extensible. Planned upgrades include:

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

## <<<<<<<<<<<<<<<TEMPORARY ENDS>>>>>>>>>>>>>>>

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

## <<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

## Research tool implementation proposal (Planned)
```bash
User Prompt
   ↓
Primary Agent (DeepSeek / Llama)
   ↓
Detects need for fresh info
   ↓
Calls "research tool"
   ↓
Research tool = Perplexity R1 + DuckDuckGo
   ↓
Structured factual findings
   ↓
Primary Agent synthesizes final answer

```
This architecture avoids model hellucination.

### What each model should do (clear responsibility split)
#### DeepSeek-R1 / Llama-3.1 (PRIMARY AGENTS)
Role
- Reasoning
- Planning
- Tool orchestration
- Memory
- Safety enforcement
- Final answer generation

They should:
- Decide when information is outdated
- Decide what to search
- Decide how to combine sources

#### Perplexity R1 (RESEARCH ENGINE)
Role
- Fast factual lookup
- Web-grounded summaries
- Source-heavy answers
- No memory
- No tool loops
- No agent autonomy

It should:
- Answer narrow research questions
- Return facts + citations
- Be stateless

#### DuckDuckGo (RAW DATA SOURCE)
Role
- Fresh web content
- Breadth over depth

Used by:
- Perplexity directly
- OR your own search tool

#### The correct execution pattern (IMPORTANT)
What NOT to do
- Don’t let Perplexity talk directly to users
- Don’t let Perplexity manage memory
- Don’t let Perplexity decide tools
- Don’t mix Perplexity into your chat loop

#### What TO do (recommended)
**Step 1: Primary agent decides it needs fresh data** <br>
```bash
If information may be outdated or time-sensitive,
request the research tool instead of answering.
```

**Step 2: Research tool calls Perplexity** <br>
```python
class ResearchTool:
    async def run(self, query: str) -> dict:
        """
        1. Call Perplexity R1 (flattened prompt)
        2. Optionally call DuckDuckGo directly
        3. Normalize output
        """
```

Perplexity prompt example (single-shot):
```bash
Provide a factual, up-to-date summary for:

"<query>"

Rules:
- Use recent sources
- Cite sources
- Be concise
```

**Step 3: Normalize output (CRITICAL)** <br>
You should never pass raw Perplexity text back. Normalize it:
```bash
{
  "summary": "…",
  "key_facts": [
    "Fact 1",
    "Fact 2"
  ],
  "sources": [
    {"title": "...", "url": "..."}
  ],
  "confidence": "high"
}
```
This protects your system from:
- Prompt injection
- Formatting chaos
- Model bias

**Step 4: Primary agent synthesizes final answer** <br>
Now DeepSeek / Llama gets:
```bash
Research findings (from web):

Summary: ...
Key facts: ...
Sources: ...

Now answer the user clearly and safely.
```
This gives you:
- Reasoning + grounding
- Up-to-date info
- Clean citations
- Predictable behavior

#### Why this is a STRONG design choice
Advantages :
- Best of both worlds
- No hallucination
- Model-agnostic
- MCP-compatible later
- Easy to audit
- Easy to cache
- Easy to rate-limit

If you don’t do this
- Agents hallucinate
- Users lose trust
- Models fight each other
- Debugging becomes hell