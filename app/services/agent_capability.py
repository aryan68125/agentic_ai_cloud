from app.utils.ai_tools_enum import AiAgentToolsList

class AgentCapabilityService:
    def __init__(self, tools: list[dict]):
        self.tool_names = {t["agent_tool_name"] for t in tools}

    def has(self, tool_name: str) -> bool:
        return tool_name in self.tool_names

    def allows_research(self) -> bool:
        return AiAgentToolsList.RESEARCH_TOOL.value in self.tool_names

    def allows_email(self) -> bool:
        return "GMAIL_TOOL" in self.tool_names