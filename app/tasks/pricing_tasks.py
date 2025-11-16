"""Celery tasks for pricing management."""
from datetime import datetime
from app.tasks.outbox_worker import celery_app
from app.infrastructure.db import get_session
from app.domain.models.product import ProductPromotionalPrice


@celery_app.task(bind=True, max_retries=3)
def expire_promotional_prices(self):
    """
    Expire promotional prices automatically when end_date passes.
    This task should be scheduled to run periodically (e.g., daily at midnight).
    """
    with get_session() as session:
        now = datetime.now()
        
        # Find all active promotional prices that have expired
        expired_promotions = session.query(ProductPromotionalPrice).filter(
            ProductPromotionalPrice.is_active == True,
            ProductPromotionalPrice.end_date < now
        ).all()
        
        # Deactivate expired promotions
        for promotion in expired_promotions:
            promotion.is_active = False
        
        if expired_promotions:
            session.commit()
            return f"Expired {len(expired_promotions)} promotional prices"
        
        return "No promotional prices to expire"


