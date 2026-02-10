"""
LLM MODE B execution pipeline 
"""
# import time
import time

# import asynchronous i/o
import asyncio

from app.utils.back_end_owned_contracts import MainLLMBackEndOwnedContract

#import database transaction exception handler
from app.database.db_transaction_exception_handler import TransactionAbort

# import library required for making request to hugging face
import httpx

# import class response model
from app.models.class_return_model.services_class_response_models import RepositoryClassResponse

# import project's configurations 
from app.configs.config import ProjectConfigurations

# import repositories 
from app.repositories.system_prompt_repository import SystemPromptRepository

# import status codes from fast-api
from fastapi import status

# logging relater imports
from app.utils.logger import LoggerFactory

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

class VerifiedAnswerLLMService:
    def __init__(self, system_prompt_repo, db):
        self.db = db
        self.system_prompt_repo = SystemPromptRepository(db=db)

        self.HF_API_URL = ProjectConfigurations.HF_API_URL.value
        self.hugging_face_auth_token = ProjectConfigurations.HUGGING_FACE_AUTH_TOKEN.value
        self.system_prompt_repo = system_prompt_repo

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

    def _build_system_prompt(self, agent_id, verified_payload):
        base_prompt = self.system_prompt_repo.get_one(agent_id).data["llm_system_prompt"]
        debug_logger.debug(f"VerifiedAnswerLLMService._build_system_prompt | base_prompt = {base_prompt}")

        verified_block = (
            "\n<<VERIFIED_PERPLEXITY_RESPONSE>>\n"
            + str(verified_payload)
            + "\n<<END_VERIFIED_PERPLEXITY_RESPONSE>>\n"
        )
        debug_logger.debug(f"VerifiedAnswerLLMService._build_system_prompt | verified_block = {verified_block}")

        return (
            MainLLMBackEndOwnedContract.BACK_END_NON_NEGOTIABLE_SYS_PROMPT.value
            + verified_block
            + base_prompt
        )

    async def generate(self, agent_id, verified_payload) -> RepositoryClassResponse:
        try:
            system_prompt_repo_result = self.system_prompt_repo.get_one(agent_id)
            if not system_prompt_repo_result.status:
                return RepositoryClassResponse(
                    status=False,
                    status_code=system_prompt_repo_result.status_code,
                    message=system_prompt_repo_result.message
                )

            headers = {"Authorization": f"Bearer {self.hugging_face_auth_token}"}

            system_prompt = self._build_system_prompt(agent_id, verified_payload)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Present the verified information clearly."}
            ]

            body = {
                    "model": "use agent if to find the system prompt and the associated llm model that it's using dynamically",
                    "messages": messages
                }
            debug_logger.debug(f"VerifiedAnswerLLMService.generate | body = {body}")
            
            response = await self._call_huggingface_with_retry(body,headers) 
            content = response["content"]

            if "<<REQUEST_RESEARCH>>" in content:
                error_logger.error(f"VerifiedAnswerLLMService.generate | MODE B VIOLATION | response = {response}")
                raise RuntimeError("MODE B VIOLATION")

            debug_logger.debug(f"VerifiedAnswerLLMService.generate | content = {content}")
            return RepositoryClassResponse(
                status=True,
                status_code=status.HTTP_200_OK,
                message=response.message,
                data={
                    "content":content
                }
            )
        except Exception as e:
            return RepositoryClassResponse(
                status=False,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=str(e)
            )
    
    """
    The reason Mode A and B have seperate _call_huggingface_with_retry methods is to prevent Mode A and B from leaking into each other.
    Mode A and B must be sterile with no infection to make sure that the llm model behaves properly.
    """
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
                    f"VerifiedAnswerLLMService._call_huggingface_with_retry | HuggingFace call attempt={attempt} | status={resp.status_code} , time={duration_ms:.2f}ms"
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
                        f"VerifiedAnswerLLMService._call_huggingface_with_retry | HuggingFace failed after {attempt} attempts | {e}"
                    )
                    raise

                delay = base_delay * (2 ** (attempt - 1))
                warning_msg = (
                    f"VerifiedAnswerLLMService._call_huggingface_with_retry | HuggingFace call failed (attempt {attempt}/{max_attempts}) | retrying in {delay:.2f}s | error={type(e).__name__}"
                )
                error_logger.warning(warning_msg)

                await asyncio.sleep(delay)