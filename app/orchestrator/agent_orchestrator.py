# app/orchestrators/agent_orchestrator.py

from app.models.class_return_model.services_class_response_models import ToolControlsignalResponse

# import services
from app.services.process_hugging_face_ai_prompt import ProcessHuggingFaceAIPromptService
from app.services.verified_answer_llm import VerifiedAnswerLLMService

class AgentOrchestrator:
    def __init__(
        self,
        research_tool_service,
        verified_payload_repo,
        hugging_face_auth_token,
        HF_API_URL,
        db
    ):
        self.mode_a = ProcessHuggingFaceAIPromptService(hugging_face_auth_token,HF_API_URL,db)
        self.research_tool = research_tool_service
        self.mode_b = VerifiedAnswerLLMService()
        self.verified_repo = verified_payload_repo

    async def handle_user_prompt(self, request):
        # Step 1: Always start with MODE A
        result = await self.mode_a.exploratory_llm_service(request)

        # Step 2: If MODE A wants research, orchestrate
        if isinstance(result, ToolControlsignalResponse):
            return await self._handle_research_flow(result.data, request)

        # Step 3: Otherwise return MODE A response
        return result

    async def _handle_research_flow(self, tool_request, request):
        # Execute tool
        research_result = await self.research_tool.execute(tool_request)

        verified_payload = research_result.data["verified_research"]

        # Store verified payload
        self.verified_repo.save(
            agent_id=request.agent_id,
            payload=verified_payload
        )

        # Dispatch MODE B
        return await self.mode_b.generate(
            agent_id=request.agent_id,
            verified_payload=verified_payload
        )
