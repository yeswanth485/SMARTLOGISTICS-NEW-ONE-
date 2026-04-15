import uuid
from sqlalchemy import Column, String, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


class BoxCatalog(Base):
    __tablename__ = "box_catalog"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), nullable=False)
    length = Column(Float, nullable=False)
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    max_weight = Column(Float, nullable=False)
    base_cost = Column(Float, nullable=False)
