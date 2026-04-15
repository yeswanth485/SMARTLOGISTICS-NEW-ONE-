"""
SmartLogistics – SQLAlchemy ORM Models
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    total_cost = Column(Float, nullable=False, default=0.0)
    status = Column(String(50), nullable=False, default="completed")
