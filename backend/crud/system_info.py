from sqlalchemy.orm import Session
from .. import models, schemas

# SystemInfo CRUD operations
def get_system_info(db: Session, system_name: str):
    return db.query(models.SystemInfo).filter(models.SystemInfo.system_name == system_name).first()

def get_all_system_info(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.SystemInfo).offset(skip).limit(limit).all()

def create_system_info(db: Session, system_info: schemas.SystemInfoCreate):
    db_system_info = models.SystemInfo(
        system_name=system_info.system_name,
        data_query_function_name=system_info.data_query_function_name,
        filterable_columns=system_info.filterable_columns,
        frontend_route_name=system_info.frontend_route_name
    )
    db.add(db_system_info)
    db.commit()
    db.refresh(db_system_info)
    return db_system_info

def delete_system_info(db: Session, system_name: str):
    db_system_info = db.query(models.SystemInfo).filter(models.SystemInfo.system_name == system_name).first()
    if db_system_info:
        db.delete(db_system_info)
        db.commit()
        return True
    return False
