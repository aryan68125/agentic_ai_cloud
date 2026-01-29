import hashlib
import time

# db orm related imports
from sqlalchemy.orm import Session
from sqlalchemy import (select, update, delete, text, func)

# imports related to database table models
from app.models.db_table_models.ai_agent_table import AIAgentName

# import messages
from app.utils.success_messages import AiAgentApiSuccessMessage
from app.utils.error_messages import AgentApiErrorMessages

# import class response model
from app.models.class_return_model.services_class_response_models import RepositoryClassResponse

# import status codes from fast-api
from fastapi import status

# import logging utility
from app.utils.logger import LoggerFactory

# initialize logging utility
info_logger = LoggerFactory.get_info_logger()
error_logger = LoggerFactory.get_error_logger()
debug_logger = LoggerFactory.get_debug_logger()

class AIAgentRepository:
    def __init__(self, db: Session):
        self.db = db
        debug_logger.debug(f"AIAgentRepository.__init__ | AIAgentRepository initialized | database_session = {self.db}")

    def _generate_agent_id(self, agent_name: str) -> str:
        raw = f"{agent_name}_{time.time()}"
        ai_agent_id = hashlib.sha256(raw.encode()).hexdigest()
        debug_logger.debug(f"AIAgentRepository._generate_agent_id | generate ai_agent_id | ai_agent_id = {ai_agent_id}")
        return ai_agent_id

    # ---------- CRUD OPERATIONS ----------

    def insert(self, agent_name: str) -> RepositoryClassResponse:
        try:
            agent_id = self._generate_agent_id(agent_name)
           
            obj = AIAgentName(
                ai_agent_name=agent_name,
                ai_agent_id=agent_id,
            )
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            row = obj.to_dict()

            debug_logger.debug(f"AIAgentRepository.insert | {AiAgentApiSuccessMessage.AGENT_NAME_INSERTED.value} | db_result = {row}")
            return RepositoryClassResponse(
                status = True,
                status_code = status.HTTP_200_OK,
                message = AiAgentApiSuccessMessage.AGENT_NAME_INSERTED.value,
                data = row
            )
        except Exception as e:
            error_logger.error(f"AIAgentRepository.insert | {str(e)}")
            return RepositoryClassResponse(
                status = False,
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                message = str(e)
            )

    def update(self, agent_id: str, new_name: str) -> RepositoryClassResponse:
        try:
            if not agent_id or agent_id is None or agent_id == "":
                error_logger.error(f"AIAgentRepository.update | {AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value}")
                return RepositoryClassResponse(
                        status=False,
                        status_code = status.HTTP_400_BAD_REQUEST,
                        message=AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value
                    )
            if not new_name or new_name is None or new_name == "":
                error_logger.error(f"AIAgentRepository.update | {AgentApiErrorMessages.AI_AGENT_NAME_EMPTY.value}")
                return RepositoryClassResponse(
                        status=False,
                        status_code = status.HTTP_400_BAD_REQUEST,
                        message=AgentApiErrorMessages.AI_AGENT_NAME_EMPTY.value
                    )
            obj = (
                update(AIAgentName)
                .where(AIAgentName.ai_agent_id == agent_id)
                .values(ai_agent_name=new_name)
                .returning(AIAgentName)
            )
            row = self.db.execute(obj).scalar_one_or_none()
            self.db.commit()
            row = row.to_dict()

            if not row:
                error_logger.error(
                    f"AIAgentRepository.update | agent not found in database | agent_id = {agent_id}"
                )
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_404_NOT_FOUND,
                    message=AgentApiErrorMessages.AGENT_ID_NOT_FOUND.value
                )
            debug_logger.debug(f"AIAgentRepository.update | update agent_name | db_response = {row}")
            return RepositoryClassResponse(
                    status = True,
                    status_code = status.HTTP_200_OK,
                    message = AiAgentApiSuccessMessage.AGENT_NAME_UPDATED.value,
                    data = row
                )
        except Exception as e:
            error_logger.error(f"AIAgentRepository.update | {str(e)}")
            return RepositoryClassResponse(
                status = False,
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                message = str(e)
            ) 

    def delete(self, agent_id: str) -> RepositoryClassResponse:
        try:
            if not agent_id or agent_id is None or agent_id == "":
                error_logger.error(f"AIAgentRepository.delete | {AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value}")
                return RepositoryClassResponse(
                        status=False,
                        status_code = status.HTTP_400_BAD_REQUEST,
                        message=AgentApiErrorMessages.AI_AGENT_ID_EMPTY.value
                    )
        
            obj = delete(AIAgentName).where(AIAgentName.ai_agent_id == agent_id)
            result = self.db.execute(obj)
            self.db.commit()

            debug_logger.debug(f"AIAgentRepository.delete | delete agent_name | db_response = {result.rowcount > 0}")
            if result.rowcount > 0:
                return RepositoryClassResponse(
                    status = True,
                    status_code = status.HTTP_204_NO_CONTENT,
                    message = AiAgentApiSuccessMessage.AGENT_NAME_DELETED.value,
                    data = {}
                ) 
            else:
                error_logger.error(f"AIAgentRepository.delete | {AgentApiErrorMessages.AGENT_ID_NOT_FOUND.value}")
                return RepositoryClassResponse(
                    status = False,
                    status_code = status.HTTP_404_NOT_FOUND,
                    message = AgentApiErrorMessages.AGENT_ID_NOT_FOUND.value
                ) 
        except Exception as e:
            error_logger.error(f"AIAgentRepository.delete | {str(e)}")
            return RepositoryClassResponse(
                    status = False,
                    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message = str(e)
                ) 

    def get_one(self, agent_id: str = None, agent_name: str = None) -> RepositoryClassResponse:
        try:
            obj = select(AIAgentName)
            if agent_id and agent_name:
                error_logger.error(f"AIAgentRepository.get_one | {AgentApiErrorMessages.AGENT_ID_NOT_FOUND.value}")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=AgentApiErrorMessages.AI_AGENT_NAME_AND_AGENT_ID_IS_NOT_REQUIRED.value
                )
            if agent_id:
                obj = obj.where(AIAgentName.ai_agent_id == agent_id)
            if agent_name:
                obj = obj.where(AIAgentName.ai_agent_name == agent_name)

            row = self.db.execute(obj).scalar_one_or_none()
            if not row:
                error_logger.error(
                    f"AIAgentRepository.get_one | {AgentApiErrorMessages.AGENT_ID_NOT_FOUND.value} | agent_id = {agent_id}"
                )
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_404_NOT_FOUND,
                    message=AgentApiErrorMessages.AGENT_ID_NOT_FOUND.value
                )
            row = row.to_dict()
            debug_logger.debug(f"AIAgentRepository.get_one | {AiAgentApiSuccessMessage.AGENT_NAME_FETCHED.value} | db_response = {row}")
            return RepositoryClassResponse(
                        status = True,
                        status_code = status.HTTP_200_OK,
                        message = AiAgentApiSuccessMessage.AGENT_NAME_FETCHED.value,
                        data = row
                    )
        except Exception as e:
            error_logger.error(f"AIAgentRepository.get_one | {str(e)}")
            return RepositoryClassResponse(
                    status = False,
                    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message = str(e)
                ) 
        
    def _count_all(self) -> int:
        obj = select(func.count()).select_from(AIAgentName)
        return self.db.execute(obj).scalar_one()

    def get_all(self, page : int = 1, page_size : int = 10) -> RepositoryClassResponse:
        try:
            if page is None or page < 1:
                error_logger.error(f"AIAgentRepository.get_all | {AgentApiErrorMessages.PAGE_NUMBER_EMPTY.value}")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=AgentApiErrorMessages.PAGE_NUMBER_EMPTY.value
                )
            if page_size is None or page_size < 1:
                error_logger.error(f"AIAgentRepository.get_all | {AgentApiErrorMessages.PAGE_SIZE_EMPTY.value}")
                return RepositoryClassResponse(
                    status=False,
                    status_code = status.HTTP_400_BAD_REQUEST,
                    message=AgentApiErrorMessages.PAGE_SIZE_EMPTY.value
                )
            offset = (page - 1) * page_size

            obj = (
                select(AIAgentName)
                .order_by(AIAgentName.created_at.desc())
                .offset(offset)
                .limit(page_size)
            )
            rows = self.db.execute(obj).scalars().all()
            items = [row.to_dict() for row in rows]
            total_records = self._count_all()
            total_pages = (total_records + page_size - 1) // page_size
            debug_logger.debug(
                "AIAgentRepository.get_all | "
                f"page={page}, page_size={page_size}, "
                f"returned_rows={len(rows)}, total_records={total_records}, total_pages={total_pages}"
            )
            return RepositoryClassResponse(
                status=True,
                status_code=status.HTTP_200_OK,
                message=AiAgentApiSuccessMessage.AGENT_NAME_FETCHED.value,
                data={
                    "items": items,
                    "page": page,
                    "page_size": page_size,
                    "total_records": total_records,
                    "total_pages": total_pages
                }
            )
        except Exception as e:
            error_logger.error(f"AIAgentRepository.get_all | {str(e)}")
            return RepositoryClassResponse(
                    status = False,
                    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message = str(e)
                ) 
