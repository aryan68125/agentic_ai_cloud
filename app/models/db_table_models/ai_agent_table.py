from sqlalchemy import BigInteger, Text, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base

class AIAgentName(Base):
    __tablename__ = "ai_agent_table"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    ai_agent_name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    ai_agent_id: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

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
            "ai_agent_name": self.ai_agent_name,
            "ai_agent_id": self.ai_agent_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
