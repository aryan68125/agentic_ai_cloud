# app/orchestrators/agent_orchestrator.py

from app.models.class_return_model.services_class_response_models import ToolControlsignalResponse

from app.models.class_return_model.services_class_response_models import RepositoryClassResponse

# import status codes from fast-api
from fastapi import status

from app.database.db_transaction_exception_handler import TransactionAbort

# import logging utility
from app.utils.logger import LoggerFactory

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

class AgentOrchestrator:
    def __init__(
        self,
        exploratory_llm_service,      # MODE A
        research_tool_service,        # Perplexity
        verified_answer_service,      # MODE B
        verified_payload_repo,        # persistence
        db
    ):
        self.db = db
        self.mode_a = exploratory_llm_service
        self.research_tool = research_tool_service
        self.mode_b = verified_answer_service
        self.verified_repo = verified_payload_repo

    async def handle_user_prompt(self, request) -> RepositoryClassResponse:
        # Step 1: Always start with MODE A
        result = await self.mode_a.exploratory_llm_service(request)

        debug_logger.debug(f"AgentOrchestrator.handle_user_prompt | await self.mode_a.exploratory_llm_service(request) = {result}")

        # Step 2: If MODE A wants research, orchestrate
        if not isinstance(result, ToolControlsignalResponse):
            # [CONVERSATION MODE]
            debug_logger.debug(f"AgentOrchestrator.handle_user_prompt | await self._handle_research_flow(result.data, request) = {result}")
            return result
        if isinstance(result, ToolControlsignalResponse):
            # [RESEARCH MODE]
            _handle_research_flow_result =  await self._handle_research_flow(result.data, request)
            if not _handle_research_flow_result.status and _handle_research_flow_result:
                error_logger.error(f"AgentOrchestrator.handle_user_prompt | await self._handle_research_flow(result.data, request) = {_handle_research_flow_result}")
                return RepositoryClassResponse(
                    status=_handle_research_flow_result.status,
                    status_code=_handle_research_flow_result.status_code,
                    message=_handle_research_flow_result.message
                )

    async def _handle_research_flow(self, tool_request, request) -> RepositoryClassResponse:
        try:
            # Execute tool
            research_result = await self.research_tool.process_main_LLM_research_query(tool_request)
            debug_logger.debug(f"AgentOrchestrator._handle_research_flow | research_result = {research_result}")
            if not research_result.status:
                error_logger.error(f"AgentOrchestrator._handle_research_flow | research_result = {research_result}")
                return RepositoryClassResponse(
                        status=research_result.status,
                        status_code=research_result.status_code,
                        message=research_result.message
                    )

            verified_payload = research_result.data["verified_research"]
            debug_logger.debug(f"AgentOrchestrator._handle_research_flow | verified_payload = {verified_payload}")

            # Store verified payload
            # [OLD CODE REMOVE LATER]
            # self.verified_repo.insert(
            #     agent_id=request.agent_id,
            #     payload=verified_payload
            # )
            with self.db.begin():   # ← ORCHESTRATOR owns transaction
                insert_result = self.verified_repo.insert(
                    agent_id=request.agent_id,
                    payload=verified_payload
                )
                if not insert_result.status:
                    raise TransactionAbort(insert_result)

                # Dispatch MODE B
                generated_result = await self.mode_b.generate(
                    agent_id=request.agent_id,
                    verified_payload=verified_payload
                )
                debug_logger.debug(f"AgentOrchestrator._handle_research_flow | generated_result = {generated_result}")

                if not generated_result.status:
                    error_logger.error(f"AgentOrchestrator._handle_research_flow | generated_result.message = {generated_result.message}")
                    return RepositoryClassResponse(
                        status=generated_result.status,
                        status_code=generated_result.status_code,
                        message=generated_result.message
                    )
            return RepositoryClassResponse(
                    status=generated_result.status,
                    status_code=generated_result.status_code,
                    message=generated_result.message,
                    data=generated_result.data
                )
        except TransactionAbort as e:
            return RepositoryClassResponse(
                status=False,
                status_code=e.response.status_code,
                message=e.response.message
            )
        except Exception as e:
            error_logger.error(f"AgentOrchestrator._handle_research_flow | {str(e)}")
            return RepositoryClassResponse(
                    status=False,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message=str(e)
                )
