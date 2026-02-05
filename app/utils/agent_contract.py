import json
import re

def detect_agent_action(text: str):
    try:
        match = re.search(r'\{[\s\S]*\}', text)
        if not match:
            return None
        parsed = json.loads(match.group(0))
        if isinstance(parsed, dict) and "action" in parsed:
            return parsed
    except Exception:
        return None
