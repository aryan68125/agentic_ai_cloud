"""
This service and all the llm api calls will be stateless 
- i.e nothing will be stored in the database 
- All the calls will be logged for debugging purposes
"""

# import time
import time

# import fast api libraries
from fastapi import HTTPException, status

# import asynchronous i/o
import asyncio

# import library required for making request to hugging face
import httpx

# import models
from app.models.class_return_model.services_class_response_models import (RepositoryClassResponse)

# import messages
from app.utils.success_messages import ResearchToolSuccessMessages
from app.utils.error_messages import (HuggingFaceAIModelAPIErrorMessage, ResearchToolErrorMessages)

# import helper sub services
from app.services.process_huggingface_ai_response import ProcessPromptResponseService

# import logging utility
from app.utils.logger import LoggerFactory
from app.utils.agent_contract import detect_agent_action
from app.utils.agent_action_tags import AgentActionEnum
from app.tools.tool_utility.research_tool_related_const import (ResearchToolLLMSysPromptenum, ResearchToolLLMNameEnum)

# import other services on which this service depends on 
from app.services.llm_context_builder import ContextBuilderService
from app.services.token_counter import TokenCounter
from app.services.tool_prompt_builder import ToolPromptBuilder
from app.services.agent_capability import AgentCapabilityService
from app.tools.research_tool.services.research_response_parser import ResearchTagParser
from app.tools.research_tool.services.confidence_compute import compute_confidence

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

class ProcessPerplexityAIPromptService:
    # def __init__(self,hugging_face_auth_token,HF_API_URL,db):
    def __init__(self,hugging_face_auth_token,HF_API_URL):
        self.hugging_face_auth_token = hugging_face_auth_token
        self.HF_API_URL = HF_API_URL
        # self.db = db
        # instead of accepting user prompt this service will accept a json as a response from the back-end 
        # self.user_prompt_repo = UserPromptRepository(db=db)
        # instead of user defined system prompt the back-end will set the system_prompt for perplexity llm model hosted on hugging face
        # self.system_prompt_repo = SystemPromptRepository(db=db)
        # instead of saving the response from perplexity the response will be sent back to the main llm as an input for it to process
        # self.llm_response_repo = LLmPromptResponseRepository(db=db)
        # The tools will not be attached dynamically for perplexity llm there are only two tools that it can use 
        # - duckduckgo search api 
        # - wikipedia api 
        # self.tools_repository = AIAgentToolsRepository(db=db)
        # will use the same prompt resposne service same as the main llm 
        self.process_response_service = ProcessPromptResponseService()
        self.process_research_response_service = ResearchTagParser()
        # Will use custom tool prompt builder not the one main llm is using 
        # self.tool_prompt_builder_service = ToolPromptBuilder()

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
                debug_logger.debug(f"ProcessPerplexityAIPromptService._call_huggingface_with_retry | response from qwen research tool llm | resp = {resp}")
                duration_ms = (time.perf_counter() - start) * 1000
                debug_logger.debug(
                    f"ProcessPerplexityAIPromptService._call_huggingface_with_retry | HuggingFace call attempt={attempt} | status={resp.status_code} , time={duration_ms:.2f}ms"
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
                        f"ProcessPerplexityAIPromptService._call_huggingface_with_retry | HuggingFace failed after {attempt} attempts | {e}"
                    )
                    raise

                delay = base_delay * (2 ** (attempt - 1))
                warning_msg = (
                    f"ProcessPerplexityAIPromptService._call_huggingface_with_retry | HuggingFace call failed (attempt {attempt}/{max_attempts}) | retrying in {delay:.2f}s | error={type(e).__name__}"
                )
                error_logger.warning(warning_msg)

                await asyncio.sleep(delay)

    async def process_main_LLM_research_query(self,tool_request) -> RepositoryClassResponse:
        try:
            MAX_RETRIES = 3
            parsed_items = None
            raw_text = None

            info_logger.info(f"ProcessPerplexityAIPromptService.process_main_LLM_research_query | This class hit was a success! ")
            debug_logger.debug(f"ProcessPerplexityAIPromptService.process_main_LLM_research_query | get auth token from the env file | HUGGING_FACE_AUTH_TOKEN = {self.hugging_face_auth_token}")
            
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
            body = {
                "model": ResearchToolLLMNameEnum.Qwen_LLM_NAME.value,
                "messages": [
                    {"role": "system", "content": ResearchToolLLMSysPromptenum.QWEN_SYSTEM_PROMPT.value},
                    {"role": "user", "content": tool_request.query}
                ]
            }

            debug_logger.debug(f"ProcessPerplexityAIPromptService.process_main_LLM_research_query | make request to hugging face | HEADERS = {headers} , BODY = {body}")

            for attempt in range(1, MAX_RETRIES + 1):
                # making hugging face api call 
                raw_data = await self._call_huggingface_with_retry(body, headers)
                debug_logger.debug(f"ProcessPerplexityAIPromptService.process_main_LLM_research_query | Research llm resposne raw_data | raw_data = {raw_data}")

                # process response from hugging face ai_model
                extracted_data_obj = self.process_response_service.extract_content(raw_data)
                
                if not extracted_data_obj:
                    return RepositoryClassResponse(
                        status=False,
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        message=extracted_data_obj.message
                    )
                
                # 1. Extract raw LLM text
                data = extracted_data_obj.data.get("content")
                if not isinstance(data, str) or not data.strip():
                    error_logger.error(f"ProcessPerplexityAIPromptService.process_main_LLM_research_query | Invalid research LLM response: content missing or not a string")
                    return RepositoryClassResponse(
                        status=False,
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        message="Invalid research LLM response: content missing or not a string"
                    )
                debug_logger.debug(f"ProcessPerplexityAIPromptService.process_main_LLM_research_query | perplexity llm response data  = {data}")

                # 2. Parse TAG PROTOCOL
                parsed_items = self.process_research_response_service.parse(text=data)
                if parsed_items:
                    debug_logger.debug(
                        f"Research tag protocol satisfied on attempt {attempt}"
                    )
                    break

                # HARDEN PROMPT ON RETRY
                body["messages"][0]["content"] += (
                    "\n\nSTRICT REMINDER:\n"
                    "- DO NOT output <think> or reasoning\n"
                    "- DO NOT output malformed tags\n"
                    "- OUTPUT ONLY the TAG PROTOCOL\n"
                )

            if not parsed_items:
                """
                I want to implement retry strategy here if the parsed_item is invalid 
                The back-end must retry 3 times
                """
                error_logger.error(f"ProcessPerplexityAIPromptService.process_main_LLM_research_query | Research LLM output violated tag protocol")
                return RepositoryClassResponse(
                    status=False,
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    message="Research LLM output violated tag protocol"
                )
            debug_logger.debug(f"ProcessPerplexityAIPromptService.process_main_LLM_research_query | parsed_items = {parsed_items}")
            
            # 3. Validate + canonicalize
            validated_facts = []
            sources = []
            for item in parsed_items:
                if not item["answer"]:
                    continue
                if not item["source"].startswith("http"):
                    continue

                validated_facts.append(item)
                sources.append(item["source"])
            if not validated_facts:
                error_logger.error(f"ProcessPerplexityAIPromptService.process_main_LLM_research_query | No valid research facts found")
                return RepositoryClassResponse(
                    status=False,
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    message="No valid research facts found"
                )
            debug_logger.debug(f"ProcessPerplexityAIPromptService.process_main_LLM_research_query | validated_facts = {validated_facts} , sources = {sources}")

            # 4. Compute confidence
            confidence = compute_confidence(sources)
            debug_logger.debug(f"ProcessPerplexityAIPromptService.process_main_LLM_research_query | confidence of the researched material | confidence = {confidence}")

            # 5. Generate payload
            verified_payload = {
                "facts": validated_facts,
                "confidence": confidence,
                "source_policy": tool_request.source_policy
            }
            debug_logger.debug(f"ProcessPerplexityAIPromptService.process_main_LLM_research_query | Final research llm validated response | verified_payload = {verified_payload}")
            return RepositoryClassResponse(
                    status = True,
                    status_code = status.HTTP_200_OK,
                    message = ResearchToolSuccessMessages.MAIN_LLM_QUERY_PROCESSED.value,
                    data = {
                        "verified_research":verified_payload
                    }
                )
        
        except httpx.ReadTimeout:
            error_logger.exception(
                f"ProcessPerplexityAIPromptService.process_main_LLM_research_query | Research llm hugging face llm api time out | {httpx.ReadTimeout}"
            )
            return RepositoryClassResponse(
                status=False,
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                message="Research llm hugging face llm api time out"
            )
        except Exception as e:
            error_logger.exception(
                f"ProcessPerplexityAIPromptService.process_main_LLM_research_query | {e}"
            )
            return RepositoryClassResponse(
                status=False,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=str(e)
            )

