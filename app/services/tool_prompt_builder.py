from app.utils.ai_tools_enum import AiAgentToolsList
from app.utils.logger import LoggerFactory

info_logger = LoggerFactory.get_info_logger()
debug_logger = LoggerFactory.get_debug_logger()

class ToolPromptBuilder:
    @staticmethod
    def build(attached_tools: list[dict]) -> str:
        info_logger.info("ToolPromptBuilder.build | Building tool prompt")

        if not attached_tools:
            debug_logger.debug("ToolPromptBuilder.build | No tools attached")
            return (
                "\n\n### AVAILABLE TOOLS\n"
                "None\n"
                "\n\nRules:\n"
                "- You MUST NOT claim access to any tools.\n"
                "- You MUST request research ONLY if explicitly allowed by the system.\n"
            )

        tool_descriptions: list[str] = []

        for tool in attached_tools:
            debug_logger.debug(f"ToolPromptBuilder.build | tool = {tool}")

            if tool.get("agent_tool_name") == AiAgentToolsList.RESEARCH_TOOL.value:
                tool_descriptions.append(
                    "- Research Tool: Can request verified factual information via the platform."
                )

        if not tool_descriptions:
            debug_logger.debug("ToolPromptBuilder.build | No matching tool descriptions")
            return (
                "\n\n### AVAILABLE TOOLS\n"
                "None\n"
                "\n\nRules:\n"
                "- You MUST NOT claim access to any tools.\n"
            )

        return (
            "\n\n### AVAILABLE TOOLS\n"
            + "\n".join(tool_descriptions)
            + "\n\nRules:\n"
            "- You may request tool usage ONLY via structured control output.\n"
            "- Do NOT describe tool internals or APIs.\n"
        )
