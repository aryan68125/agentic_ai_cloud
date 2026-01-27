from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.db_session import get_db
from app.controllers.agent_controllers import AgentController

def get_agent_controller(
    db: Session = Depends(get_db),
) -> AgentController:
    return AgentController(db)
