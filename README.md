# Aryabhatta 
This is the backend for the platform that is used to create AI agents (Simplified version of Relevance) <br>
You can also host this platform on your own infrastructure.

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
│   ├── __pycache__
│   │   └── env.cpython-311.pyc
│   ├── README
│   ├── script.py.mako
│   └── versions
│       ├── 027e8d073bf8_create_ai_agent_table.py
│       ├── 4778aedf35a2_create_ai_agent_table.py
│       ├── 53e83fac2395_create_system_prompt_table.py
│       ├── 6146d779b733_create_system_prompt_table.py
│       ├── b20ac25ffcd0_create_system_prompt_table.py
│       ├── c3c1c2bd75c0_create_system_prompt_table.py
│       ├── ff1251aeb20c_create_user_prompt_table.py
│       └── __pycache__
│           ├── 027e8d073bf8_create_ai_agent_table.cpython-311.pyc
│           ├── 4778aedf35a2_create_ai_agent_table.cpython-311.pyc
│           ├── 53e83fac2395_create_system_prompt_table.cpython-311.pyc
│           ├── 6146d779b733_create_system_prompt_table.cpython-311.pyc
│           ├── b20ac25ffcd0_create_system_prompt_table.cpython-311.pyc
│           ├── c3c1c2bd75c0_create_system_prompt_table.cpython-311.pyc
│           └── ff1251aeb20c_create_user_prompt_table.cpython-311.pyc
├── alembic.ini
├── app
│   ├── apis
│   │   ├── agent_api.py
│   │   ├── hugging_face_api.py
│   │   ├── __init__.py
│   │   ├── prompt_apis.py
│   │   └── __pycache__
│   │       ├── agent_api.cpython-311.pyc
│   │       ├── hugging_face_api.cpython-311.pyc
│   │       ├── __init__.cpython-311.pyc
│   │       └── prompt_apis.cpython-311.pyc
│   ├── configs
│   │   ├── config.py
│   │   ├── __init__.py
│   │   └── __pycache__
│   │       ├── config.cpython-311.pyc
│   │       └── __init__.cpython-311.pyc
│   ├── controllers
│   │   ├── agent_controllers.py
│   │   ├── hugging_face_ai_model_controllers.py
│   │   ├── __init__.py
│   │   ├── prompt_controllers.py
│   │   └── __pycache__
│   │       ├── agent_controllers.cpython-311.pyc
│   │       ├── hugging_face_ai_model_controllers.cpython-311.pyc
│   │       ├── __init__.cpython-311.pyc
│   │       └── prompt_controllers.cpython-311.pyc
│   ├── database
│   │   ├── base.py
│   │   ├── db_session.py
│   │   └── __pycache__
│   │       ├── base.cpython-311.pyc
│   │       └── db_session.cpython-311.pyc
│   ├── dependencies
│   │   ├── controller_dependencies.py
│   │   ├── __init__.py
│   │   └── __pycache__
│   │       ├── controller_dependencies.cpython-311.pyc
│   │       └── __init__.cpython-311.pyc
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
│   │   │   ├── __pycache__
│   │   │   │   ├── __init__.cpython-311.pyc
│   │   │   │   ├── request_models.cpython-311.pyc
│   │   │   │   ├── response_models.cpython-311.pyc
│   │   │   │   └── services_class_response_models.cpython-311.pyc
│   │   │   ├── request_models.py
│   │   │   └── response_models.py
│   │   ├── class_return_model
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── __init__.cpython-311.pyc
│   │   │   │   └── services_class_response_models.cpython-311.pyc
│   │   │   └── services_class_response_models.py
│   │   ├── db_table_models
│   │   │   ├── ai_agent_table.py
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── ai_agent_table.cpython-311.pyc
│   │   │   │   ├── __init__.cpython-311.pyc
│   │   │   │   ├── system_prompt_table.cpython-311.pyc
│   │   │   │   └── user_prompt_table.cpython-311.pyc
│   │   │   ├── system_prompt_table.py
│   │   │   └── user_prompt_table.py
│   │   ├── __init__.py
│   │   └── __pycache__
│   │       └── __init__.cpython-311.pyc
│   ├── __pycache__
│   │   ├── __init__.cpython-311.pyc
│   │   └── main.cpython-311.pyc
│   ├── repositories
│   │   ├── ai_agent_repository.py
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── ai_agent_repository.cpython-311.pyc
│   │   │   ├── __init__.cpython-311.pyc
│   │   │   ├── system_prompt_repository.cpython-311.pyc
│   │   │   └── user_prompt_repository.cpython-311.pyc
│   │   ├── system_prompt_repository.py
│   │   └── user_prompt_repository.py
│   ├── services
│   │   ├── process_huggingface_ai_response.py
│   │   ├── process_prompt.py
│   │   └── __pycache__
│   │       ├── process_huggingface_ai_response.cpython-311.pyc
│   │       └── process_prompt.cpython-311.pyc
│   └── utils
│       ├── db_bootstrap.py
│       ├── db_conn_manager.py
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
│       ├── __pycache__
│       │   ├── db_bootstrap.cpython-311.pyc
│       │   ├── db_conn_manager.cpython-311.pyc
│       │   ├── db_operation_type.cpython-311.pyc
│       │   ├── error_messages.cpython-311.pyc
│       │   ├── field_descriptions.cpython-311.pyc
│       │   ├── get_base_url.cpython-311.pyc
│       │   ├── hugging_face_ai_model_enum.cpython-311.pyc
│       │   ├── __init__.cpython-311.pyc
│       │   ├── logger.cpython-311.pyc
│       │   ├── logger_info_messages.cpython-311.pyc
│       │   ├── log_initializer.cpython-311.pyc
│       │   ├── logs_re_namer.cpython-311.pyc
│       │   └── success_messages.cpython-311.pyc
│       └── success_messages.py
├── README.md
└── requirements.txt
```
## The way I designed the project's flow 
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

## Tool Usage
This is the platform where :
- User will set the system prompt.
- User will select the tools that the LLM should be able to use.
- User will test out his/her agents

Relevance like flow but more simpler

## Reasons for not using Langchain 
Loss of Control
- LangChain:
    - hides agent loops
    - auto-retries silently
    - mutates prompts internally
    - makes debugging painful
- I care about:
    - restart safety
    - determinism
    - exactly-once execution
    - auditability
    - control of what is going on and how it should be done

LangChain violates all of these by default.

Tool Execution is Opaque
- LangChain:
    - executes tools internally
    - retries tools without telling you
    - no guaranteed idempotency
- My requirements 
    - LLM should only decide, backend should execute

Hugging Face Support Is Second-Class
- LangChain works best with:
    - OpenAI / Anthropic
- For Hugging Face:
    - wrappers are brittle
    - streaming is inconsistent
    - function-calling is emulated anyway

I will still need custom glue code.

Performance & Scaling
- LangChain:
    - adds latency
    - adds memory overhead
    - difficult to batch
    - difficult to stream cleanly
- Your custom loop:
    - zero abstraction tax
    - clean async
    - HF-friendly
