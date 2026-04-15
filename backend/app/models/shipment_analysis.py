import uuid
from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


class ShipmentAnalysis(Base):
    __tablename__ = "shipment_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    best_option = Column(String(100), nullable=False)
    reason = Column(String(1000), nullable=False)
    cost_saving = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False, default=0.85)
