from app.utils.ai_tools_enum import AiAgentToolsList
from app.utils.logger import LoggerFactory

info_logger = LoggerFactory.get_info_logger()
debug_logger = LoggerFactory.get_debug_logger()

class ToolPromptBuilder:
    @staticmethod
    def build(attached_tools: list[dict]) -> str:
        info_logger.info("ToolPromptBuilder.build | Building tool prompt")
        if not attached_tools:
            response = (
                "\n\n### AVAILABLE TOOLS\n"
                "None\n"
            )
            debug_logger.debug(f"ToolPromptBuilder.build | no tool attached | response = {response}")
            return response

        tools = []

        for tool in attached_tools:
            if tool.get("agent_tool_name") == AiAgentToolsList.RESEARCH_TOOL.value:
                tools.append("- Research Tool: Can request verified factual information via the platform.")

        debug_logger.debug(f"ToolPromptBuilder.build | Tools list attached to the agent | tools = {tools}")

        if not tools:
            debug_logger.debug(f"ToolPromptBuilder.build | Tools list empty")
            return (
                "\n\n### AVAILABLE TOOLS\n"
                "None\n"
            )
        final_response = (
            "\n\n### AVAILABLE TOOLS\n"
            + "\n".join(tools)
            + "\n\nRules:\n"
            # [OLD CODE REMOVE LATER]
            # "- If external verified information is required, emit <<REQUEST_RESEARCH>>\n"
            "- Do NOT define formats or schemas\n"
        )
        debug_logger.debug(f"ToolPromptBuilder.build | final_response = {final_response}")
        return final_response
