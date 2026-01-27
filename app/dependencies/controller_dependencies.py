from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.db_session import get_db
from app.controllers.agent_controllers import AgentController
from app.controllers.prompt_controllers import PromptController

def get_agent_controller(
    db: Session = Depends(get_db),
) -> AgentController:
    return AgentController(db)

def get_prompt_controller(
    db: Session = Depends(get_db),
) -> PromptController:
    return PromptController(db)
