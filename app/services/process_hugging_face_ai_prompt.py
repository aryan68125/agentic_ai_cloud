# import fast api libraries
from fastapi import HTTPException, status

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
from app.utils.error_messages import HuggingFaceAIModelAPIErrorMessage

# import helper sub services
from app.services.process_huggingface_ai_response import ProcessPromptResponseService

# import logging utility
from app.utils.logger import LoggerFactory
from app.utils.success_messages import PromptApiSuccessMessages

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

    async def process_user_prompt_llm(self,request) -> RepositoryClassResponse:
        try:
            """
            ai_model
            system_prompt
            agent_id use this get the rest
            user_prompt
            """
            """
            how to process the user prompt here 
            STEP 1 :
            - First use agent_id to insert the user_prompt in the user_prompt table
            STEP 2:
            - Then get the system prompt from the database using agent_id
            STEP 3 : 
            - Make an API call to hugging face send system_prompt and user_prompt (do this only when llm_response_table is empty for the current agent_id)
            - Third get all the user_prompts along with their llm_response from the datbase using agent_id
            STEP 4 :
            - Fourth send all this to hugging face api  
            """
                        
            # get system_prompt from the database using agen_id
            with self.db.begin():
                system_prompt_get_result = self.system_prompt_repo.get_one(agent_id = request.agent_id)
                if not system_prompt_get_result.status:
                    raise TransactionAbort(system_prompt_get_result)
                    
            info_logger.info(f"ProcessHuggingFaceAIPromptService.process_user_prompt_llm | This class hit was a success! ")
            debug_logger.debug(f"ProcessHuggingFaceAIPromptService.process_user_prompt_llm | get auth token from the env file | HUGGING_FACE_AUTH_TOKEN = {self.hugging_face_auth_token}")

            timeout = httpx.Timeout(
                connect=10.0,
                read=120.0,
                write=10.0,
                pool=10.0
            )
            
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

            body = {
                "model": system_prompt_get_result.data.get("ai_model"),
                "messages": [
                    {"role": "system", "content": system_prompt_get_result.data.get("llm_system_prompt")},
                    {"role": "user", "content": request.user_prompt}
                ]
            }

            debug_logger.debug(f"ProcessHuggingFaceAIPromptService.process_user_prompt_llm | make request to hugging face | HEADERS = {headers} , BODY = {body}")
            # make request to hugging face api_model
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(self.HF_API_URL, json=body, headers=headers)
                debug_logger.debug(f"ProcessHuggingFaceAIPromptService.process_user_prompt_llm | executing async with httpx.AsyncClient() | hugging_face_response = {resp}")
                resp.raise_for_status()
                debug_logger.debug(f"ProcessHuggingFaceAIPromptService.process_user_prompt_llm | response data from hugging face resp.json() | data = {resp.json()}")
                data = resp.json()

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
            raise