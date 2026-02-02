# import logging utility
from app.utils.logger import LoggerFactory

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

class ContextBuilderService:
    @staticmethod
    def build(
        model_name : str,
        system_prompt: str,
        conversation_turns: list[dict],
        new_user_prompt: str,
        token_counter,
        max_tokens : int, # 3000
        reserved_for_response : int # 800
    ):
        info_logger.info(f"ContextBuilderService.build | Building context for the hugging face LLM")
        history_budget = max_tokens - reserved_for_response

        messages = [{"role": "system", "content": system_prompt}]
        token_count = token_counter(text=system_prompt,model_name=model_name)

        # iterate from most recent backwards
        for turn in reversed(conversation_turns):
            turn_tokens = token_counter(text=turn["content"],model_name=model_name)
            if token_count + turn_tokens > history_budget:
                break
            messages.insert(1, turn)
            token_count += turn_tokens

        messages.append({"role": "user", "content": new_user_prompt})
        debug_logger.debug(f"ContextBuilderService.build | history_budget = {history_budget}, token_count = {token_count}, messages = {messages}")
        return messages
