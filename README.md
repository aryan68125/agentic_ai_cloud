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
alembic -c app/alembic.ini upgrade head
```


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
