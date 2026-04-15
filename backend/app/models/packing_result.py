import uuid
from sqlalchemy import Column, String, Float, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


class PackingResult(Base):
    __tablename__ = "packing_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    box_type = Column(String(100), nullable=False)
    box_dimensions = Column(String(50), nullable=False)   # "LxWxH"
    utilization = Column(Float, nullable=False)            # percentage 0-100
    cost = Column(Float, nullable=False)
    items_placed = Column(JSON, nullable=True)             # list of placed item coords
    items_count = Column(Float, nullable=False, default=0)
