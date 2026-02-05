import re
from app.utils.agent_action_tags import AgentActionEnum

def detect_agent_action(text: str):
    if not text:
        return None
    
    clean_text = text.strip()
    if AgentActionEnum.RESEARCH_TAG.value in clean_text:
        return {
            "intent": AgentActionEnum.RESEARCH_TAG.value,
            "raw_text": clean_text
        }

    return None