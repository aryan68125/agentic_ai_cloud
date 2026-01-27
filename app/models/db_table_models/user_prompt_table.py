from sqlalchemy import BigInteger, Text, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base

class UserPrompt(Base):
    __tablename__ = "user_prompt_table"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    llm_user_prompt: Mapped[str] = mapped_column(Text, nullable=False)
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
            "llm_user_prompt": self.llm_user_prompt,
            "ai_agent_id": self.ai_agent_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
