# Aryabhatta 
This is the backend for the platform that is used to create AI agents.

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
