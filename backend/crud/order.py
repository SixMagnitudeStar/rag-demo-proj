from sqlalchemy.orm import Session
from typing import Dict, Any
from .. import models, schemas

# Order CRUD operations
def get_order(db: Session, order_id: str):
    return db.query(models.Order).filter(models.Order.order_id == order_id).first()

def get_orders(db: Session, filters: Dict[str, Any] = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Order)
    if filters:
        for column, value in filters.items():
            if hasattr(models.Order, column):
                # Use 'like' for partial string matching
                query = query.filter(getattr(models.Order, column).like(f"%{value}%"))
    return query.offset(skip).limit(limit).all()

def create_order(db: Session, order: schemas.OrderCreate):
    db_order = models.Order(order_id=order.order_id, order_date=order.order_date, order_amount=order.order_amount)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def delete_order(db: Session, order_id: str):
    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if db_order:
        db.delete(db_order)
        db.commit()
        return True
    return False
