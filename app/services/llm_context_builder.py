class ContextBuilderService:
    @staticmethod
    def build(
        system_prompt: str,
        conversation_turns: list[dict],
        new_user_prompt: str,
        token_counter,
        max_tokens : int, # 3000
        reserved_for_response : int # 800
    ):
        history_budget = max_tokens - reserved_for_response

        messages = [{"role": "system", "content": system_prompt}]
        token_count = token_counter(system_prompt)

        # iterate from most recent backwards
        for turn in reversed(conversation_turns):
            turn_tokens = token_counter(turn["content"])
            if token_count + turn_tokens > history_budget:
                break
            messages.insert(1, turn)
            token_count += turn_tokens

        messages.append({"role": "user", "content": new_user_prompt})
        return messages
