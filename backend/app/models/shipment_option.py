import uuid
from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


class ShipmentOption(Base):
    __tablename__ = "shipment_options"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    carrier_name = Column(String(100), nullable=False)
    estimated_cost = Column(Float, nullable=False)
    delivery_time = Column(Integer, nullable=False)        # days
    rating = Column(Float, nullable=False)
    status = Column(String(50), nullable=False, default="In Transit")
    tracking_id = Column(String(50), nullable=True)
    color = Column(String(20), nullable=True)
