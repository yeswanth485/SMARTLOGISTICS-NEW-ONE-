"""
SmartLogistics – Database Initializer & Seeder
"""
import logging
import uuid
from sqlalchemy import text
from app.db.session import engine, Base
from app.core.constants import BOX_CATALOG

logger = logging.getLogger(__name__)


async def init_db() -> None:
    """Create all tables and seed box catalog."""
    async with engine.begin() as conn:
        # Import all models so Base knows about them
        from app.models import order, product, packing_result  # noqa: F401
        from app.models import shipment_option, shipment_analysis, box_catalog, tool  # noqa: F401

        logger.info("Creating database tables...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Tables created successfully.")

    # Seed box catalog if empty
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT COUNT(*) FROM box_catalog"))
        count = result.scalar()
        if count == 0:
            logger.info("Seeding box catalog...")
            for box in BOX_CATALOG:
                await conn.execute(
                    text(
                        "INSERT INTO box_catalog (id, name, length, width, height, max_weight, base_cost) "
                        "VALUES (:id, :name, :length, :width, :height, :max_weight, :base_cost)"
                    ),
                    {"id": str(uuid.uuid4()), **box},
                )
            logger.info(f"Seeded {len(BOX_CATALOG)} box types.")

    # Seed tools registry if empty
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT COUNT(*) FROM tool_registry"))
        tool_count = result.scalar()
        if tool_count == 0:
            logger.info("Seeding backend tool registry...")
            await conn.execute(
                text(
                    "INSERT INTO tool_registry (id, name, description, version, is_active) "
                    "VALUES (:id, :name, :desc, :version, :is_active)"
                ),
                {
                    "id": str(uuid.uuid4()),
                    "name": "fastest_and_best_optimizer_tool",
                    "desc": "Tool to scan the products data and optimally optimize the shipment routing results.",
                    "version": "v1.0.0",
                    "is_active": True
                }
            )
            logger.info("Seeded backend tools.")
