# import time
import time

# import fast api libraries
from fastapi import HTTPException, status

# import asynchronous i/o
import asyncio

# import library required for making request to hugging face
import httpx

# import repositories
from app.repositories.user_prompt_repository import UserPromptRepository
from app.repositories.system_prompt_repository import SystemPromptRepository
from app.repositories.llm_prompt_response_repository import LLmPromptResponseRepository

# import models
from app.models.class_return_model.services_class_response_models import RepositoryClassResponse

#import database transaction exception handler
from app.database.db_transaction_exception_handler import TransactionAbort

# import messages
from app.utils.success_messages import HuggingFaceAIModelAPISuccessMessage
from app.utils.error_messages import (HuggingFaceAIModelAPIErrorMessage, AgentApiErrorMessages,SystemPromptApiErrorMessages)

# import helper sub services
from app.services.process_huggingface_ai_response import ProcessPromptResponseService

# import logging utility
from app.utils.logger import LoggerFactory

# import other services on which this service depends on 
from app.services.llm_context_builder import ContextBuilderService
from app.services.token_counter import TokenCounter


# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

class ProcessHuggingFaceAIPromptService:
    def __init__(self,hugging_face_auth_token,HF_API_URL,db):
        self.hugging_face_auth_token = hugging_face_auth_token
        self.HF_API_URL = HF_API_URL
        self.db = db
        self.user_prompt_repo = UserPromptRepository(db=db)
        self.system_prompt_repo = SystemPromptRepository(db=db)
        self.llm_response_repo = LLmPromptResponseRepository(db=db)
        self.process_response_service = ProcessPromptResponseService()

        # initialze the httpx here before making any call to hugging face
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=5.0,
                read=120.0,
                write=5.0,
                pool=5.0,
            ),
            limits=httpx.Limits(
                max_connections=50,
                max_keepalive_connections=20
            )
        )

    async def _call_huggingface_with_retry(self, body: dict, headers: dict):
        max_attempts = 3
        base_delay = 0.5  # seconds

        for attempt in range(1, max_attempts + 1):
            try:
                start = time.perf_counter()

                resp = await self.client.post(
                    self.HF_API_URL,
                    json=body,
                    headers=headers
                )

                duration_ms = (time.perf_counter() - start) * 1000
                debug_logger.debug(
                    f"ProcessHuggingFaceAIPromptService._call_huggingface_with_retry | HuggingFace call attempt={attempt} | status={resp.status_code} , time={duration_ms:.2f}ms"
                )

                # If the status returned by the hugging face api is of status 500 series then retry
                if resp.status_code >= 500:
                    raise httpx.HTTPStatusError(
                        "5xx from Hugging Face",
                        request=resp.request,
                        response=resp
                    )

                # if the return status from the hugging face api is of status 400 series then do not retry
                resp.raise_for_status()
                return resp.json()

            except (httpx.TimeoutException, httpx.TransportError, httpx.HTTPStatusError) as e:
                if attempt == max_attempts:
                    error_logger.error(
                        f"ProcessHuggingFaceAIPromptService._call_huggingface_with_retry | HuggingFace failed after {attempt} attempts | {e}"
                    )
                    raise

                delay = base_delay * (2 ** (attempt - 1))
                warning_msg = (
                    f"ProcessHuggingFaceAIPromptService._call_huggingface_with_retry | HuggingFace call failed (attempt {attempt}/{max_attempts}) | retrying in {delay:.2f}s | error={type(e).__name__}"
                )
                error_logger.warning(warning_msg)

                await asyncio.sleep(delay)

    async def process_user_prompt_llm(self,request) -> RepositoryClassResponse:
        try:                        
            # get system_prompt from the database using agen_id
            with self.db.begin():
                system_prompt_get_result = self.system_prompt_repo.get_one(agent_id = request.agent_id)
                if not system_prompt_get_result.status:
                    raise TransactionAbort(system_prompt_get_result)
                    
            info_logger.info(f"ProcessHuggingFaceAIPromptService.process_user_prompt_llm | This class hit was a success! ")
            debug_logger.debug(f"ProcessHuggingFaceAIPromptService.process_user_prompt_llm | get auth token from the env file | HUGGING_FACE_AUTH_TOKEN = {self.hugging_face_auth_token}")
            
            headers = {"Authorization": f"Bearer {self.hugging_face_auth_token}"}
            
            # Below is the explaination on how the body should be constructed before sending it to the hugging face LLM
            # body = {
            #     "model": request.ai_model,
            #     "messages": [
            #         """
            #             Here you will tell the model how to behave
            #         """
            #         # {"role": "system", "content": "You are a helpful assistant."},
            #         """
            #             Here the end user will write the prompt for it to gain answers from the LLM
            #         """
            #         {"role": "user", "content": request.user_prompt}
            #     ]
            # }

            # [OLD WAY OF SENDING BODY TO THE HF LLM VIA HF API]
            # body = {
            #     "model": system_prompt_get_result.data.get("ai_model"),
            #     "messages": [
            #         {"role": "system", "content": system_prompt_get_result.data.get("llm_system_prompt")},
            #         {"role": "user", "content": request.user_prompt}
            #     ]
            # }

            # [NEW WAY OF SENDING BODY TO HF LLM MAINTAINING LLM CONTEXT]
            # BUILD LLM CONTEXT HERE
            # 1. Fetch conversation history
            with self.db.begin():
                conversation_result = self.llm_response_repo.get_conversation_turns(
                    agent_id=request.agent_id
                )
                if not conversation_result.status:
                    raise TransactionAbort(conversation_result)
            # 2. Build context window
            messages = ContextBuilderService.build(
                model_name=system_prompt_get_result.data["ai_model"],
                system_prompt=system_prompt_get_result.data["llm_system_prompt"],
                conversation_turns=conversation_result.data,
                new_user_prompt=request.user_prompt,
                token_counter=TokenCounter.count,  # or tiktoken wrapper
                max_tokens=3000,
                reserved_for_response=800
            )
            # 3. Create the new body for HF LLM api
            body = {
                "model": system_prompt_get_result.data["ai_model"],
                "messages": messages
            }

            debug_logger.debug(f"ProcessHuggingFaceAIPromptService.process_user_prompt_llm | make request to hugging face | HEADERS = {headers} , BODY = {body}")

            # making hugging face api call 
            data = await self._call_huggingface_with_retry(body, headers)

            # process response from hugging face ai_model
            result_process_response_service = self.process_response_service.extract_content(data)
            if not result_process_response_service:
                return RepositoryClassResponse(
                    status=False,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message=result_process_response_service.message
                )
            
            content = result_process_response_service.data.get("content")
            if not isinstance(content, str) or not content.strip():
                return RepositoryClassResponse(
                    status=False,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message=HuggingFaceAIModelAPIErrorMessage.LLM_PROMPT_HUGGING_FACE_ERROR.value
                )
            
            with self.db.begin():
                user_prompt_insert_result = self.user_prompt_repo.insert(
                    agent_id=request.agent_id,
                    user_prompt=request.user_prompt
                )
                if not user_prompt_insert_result.status:
                    raise TransactionAbort(user_prompt_insert_result)

                llm_response_repo = self.llm_response_repo.insert(
                    agent_id=request.agent_id,
                    llm_user_prompt_id=user_prompt_insert_result.data["id"],
                    llm_prompt_response=content
                )
                if not llm_response_repo.status:
                    raise TransactionAbort(llm_response_repo)
            
            return RepositoryClassResponse(
                    status = True,
                    status_code = status.HTTP_200_OK,
                    message = HuggingFaceAIModelAPISuccessMessage.LLM_USER_PROMPT_SUCCESS.value,
                    data = {
                        "content":content
                    }
                )
        except TransactionAbort as e:
            return RepositoryClassResponse(
                status=False,
                status_code=e.response.status_code,
                message=e.response.message
            )
        except httpx.ReadTimeout:
            return RepositoryClassResponse(
                status=False,
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                message=HuggingFaceAIModelAPIErrorMessage.HUGGING_FACE_LLM_API_TIMEOUT.value
            )
        except Exception as e:
            error_logger.exception(
                f"ProcessHuggingFaceAIPromptService.process_user_prompt_llm | {e}"
            )
            return RepositoryClassResponse(
                status=False,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=str(e)
            )
    
    """
    This service is used to reset the agent 
    - Deletes all the user_prompts from the database
    - Deletes all the llm responses from the database
    - Let the system prompt remain in the database it does not deletes it
    """
    def reset_agent(self, request) -> RepositoryClassResponse:
        try:
            if not request.agent_id or request.agent_id is None or request.agent_id == "":
                return RepositoryClassResponse(
                    status=False,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message=AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value
                )
            with self.db.begin():
                delete_all_user_prompt_result = self.user_prompt_repo.delete_all(request.agent_id)
                delete_all_llm_response_result = self.llm_response_repo.delete_all(request.agent_id)
            if not delete_all_user_prompt_result.status:
                raise TransactionAbort(delete_all_user_prompt_result)
            if not delete_all_llm_response_result.status:
                raise TransactionAbort(delete_all_llm_response_result)
            
            return RepositoryClassResponse(
                    status = True,
                    status_code = status.HTTP_204_NO_CONTENT,
                    message = HuggingFaceAIModelAPISuccessMessage.LLM_CONTEXT_RESET_SUCCESS.value,
                    data = {}
                )
        except TransactionAbort as e:
            return RepositoryClassResponse(
                status=False,
                status_code=e.response.status_code,
                message=e.response.message
            )
        except Exception as e:
            error_logger.exception(
                f"ProcessHuggingFaceAIPromptService.reset_agent | {e}"
            )
            return RepositoryClassResponse(
                status=False,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=str(e)
            )

