# import tools names
from app.utils.ai_tools_enum import AiAgentToolsList

# import logging utility
from app.utils.logger import LoggerFactory

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

class ToolPromptBuilder:
    @staticmethod
    def build(attached_tools: list[str]) -> str:
        info_logger.info(f"ToolPromptBuilder.build | Build a prompt for the tools attached with the agent")
        if not attached_tools:
            debug_logger.debug(f"ToolPromptBuilder.build | No tools attached with the agent")
            tool_prompt = (
                            "\n\n### AVAILABLE TOOLS (STRICT CONTRACT)\n"
                            "NO_TOOLS_ATTACHED\n"
                            + "\n\nRules (MANDATORY):\n"
                            "- When asked about tools, you MUST list ONLY the tools named above.\n"
                            "- If no tools are listed above, reply EXACTLY: NO_TOOLS_ATTACHED\n"
                            "- Do NOT mention abilities, skills, knowledge, or built-in capabilities.\n"
                            "- Do NOT mention external services or APIs.\n"
                        )

        tool_descriptions = []

        for tool in attached_tools:
            debug_logger.debug(f"ToolPromptBuilder.build | tool = {tool}")
            if tool.get("agent_tool_name") == AiAgentToolsList.RESEARCH_TOOL.value:
                tool_descriptions.append(
                    "- Research Tool: You can search the web and summarize factual information."
                )

        if not tool_descriptions:
            debug_logger.debug(f"ToolPromptBuilder.build | No tools description found")
            tool_prompt = (
                            "\n\n### AVAILABLE TOOLS (STRICT CONTRACT)\n"
                            "NO_TOOLS_ATTACHED\n"
                            + "\n\nRules (MANDATORY):\n"
                            "- When asked about tools, you MUST list ONLY the tools named above.\n"
                            "- If no tools are listed above, reply EXACTLY: NO_TOOLS_ATTACHED\n"
                            "- Do NOT mention abilities, skills, knowledge, or built-in capabilities.\n"
                            "- Do NOT mention external services or APIs.\n"
                        )
        else:
            tool_prompt = (
                            "\n\n### AVAILABLE TOOLS (STRICT CONTRACT)\n"
                            "The following tools are attached to this agent:\n"
                            + "\n".join(tool_descriptions)
                            + "\n\nRules (MANDATORY):\n"
                            "- When asked about tools, you MUST list ONLY the tools named above.\n"
                            "- If no tools are listed above, reply EXACTLY: NO_TOOLS_ATTACHED\n"
                            "- Do NOT mention abilities, skills, knowledge, or built-in capabilities.\n"
                            "- Do NOT mention external services or APIs.\n"
                        )
        debug_logger.debug(f"ToolPromptBuilder.build | tool_prompt = {tool_prompt}")
        return tool_prompt
    
    # tomorrow write the documentation related to this chat https://chatgpt.com/c/697ad89b-a404-8324-a879-9fa90fb19392
