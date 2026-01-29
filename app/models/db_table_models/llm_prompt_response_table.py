from sqlalchemy import BigInteger, Text, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base

class LLMPromptResponseTable(Base):
    __tablename__ = "llm_prompt_response_table"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    llm_user_prompt_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=False)
    llm_prompt_response : Mapped[str] = mapped_column(Text, nullable=False)
    ai_agent_id: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "llm_user_prompt_id": self.llm_user_prompt_id,
            "llm_prompt_response": self.llm_prompt_response,
            "ai_agent_id": self.ai_agent_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
