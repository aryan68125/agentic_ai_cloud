from fastapi import FastAPI,status, Request, HTTPException
from fastapi.responses import JSONResponse

# custom routes
from app.apis.prompt_apis import router as prompt_api_routers
from app.apis.hugging_face_api import router as hugging_face_api_routers
from app.apis.agent_api import router as agent_api_routers

# import logging utility
from app.utils.logger import LoggerFactory

# import logger info messages
from app.utils.logger_info_messages import LoggerInfoMessages, PromptApiUrls

# get base url for the fast-api server
from app.utils.get_base_url import FastApiServer

# database related imports
from app.utils.db_conn_manager import PostgresConnectionManager

# import database bootstrap
from app.utils.db_bootstrap import DatabaseBootstrap

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

app = FastAPI(title = "Relevance Agentic AI")

# include custome routes here
# ingest_data router
app.include_router(prompt_api_routers, prefix="/process")
app.include_router(hugging_face_api_routers, prefix="/process")
app.include_router(agent_api_routers, prefix="/process")

# Global error exception response handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": exc.status_code,
            "error": exc.detail
        }
    )

# Test api
@app.get("/health",status_code = status.HTTP_200_OK)
def health(request: Request):
    BASE_URL_FAST_API_SERVER = FastApiServer.get_base_url(request)
    info_logger.info(f"health | url = {BASE_URL_FAST_API_SERVER}{PromptApiUrls.FAST_API_HEALTH_CHECK_URL.value} | {LoggerInfoMessages.API_HIT_SUCCESS.value}")
    return {
        "status": status.HTTP_200_OK,
        "message":"success check ok!"
    }