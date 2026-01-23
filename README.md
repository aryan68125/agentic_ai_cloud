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
