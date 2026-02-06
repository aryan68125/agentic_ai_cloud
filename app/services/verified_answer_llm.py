class VerifiedAnswerLLMService:
    def __init__(self, hf_client, system_prompt_repo):
        self.client = hf_client
        self.system_prompt_repo = system_prompt_repo

    async def generate(self, agent_id: str, verified_payload: dict):
        system_prompt = self._build_system_prompt(agent_id, verified_payload)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Present the verified information clearly."}
        ]

        response = await self.client.call(messages)

        content = response["content"]

        # HARD GUARD
        if "<<REQUEST_RESEARCH>>" in content:
            raise RuntimeError("MODE B violation: research request emitted")

        return content
