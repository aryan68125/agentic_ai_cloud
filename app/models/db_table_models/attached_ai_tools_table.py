from sqlalchemy import BigInteger, Text, TIMESTAMP, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base

class AttachedAIToolsTable(Base):
    __tablename__ = "attached_ai_tools_table"

    __table_args__ = (
        UniqueConstraint(
            "ai_agent_id",
            "agent_tool_name",
            name="uq_ai_agent_tool"
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ai_agent_id: Mapped[str] = mapped_column(Text, nullable=False, unique=False)
    agent_tool_name: Mapped[str] = mapped_column(Text, nullable=False)
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
            "ai_agent_id": self.ai_agent_id,
            "agent_tool_name": self.agent_tool_name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
