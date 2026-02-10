from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter()

@router.post("/system_info/", response_model=schemas.SystemInfo, status_code=status.HTTP_201_CREATED)
def create_system_info(system_info: schemas.SystemInfoCreate, db: Session = Depends(get_db)):
    db_system_info = crud.get_system_info(db, system_name=system_info.system_name)
    if db_system_info:
        raise HTTPException(status_code=400, detail="System Name already registered")
    return crud.create_system_info(db=db, system_info=system_info)

@router.get("/system_info/", response_model=List[schemas.SystemInfo])
def read_all_system_info(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    all_system_info = crud.get_all_system_info(db, skip=skip, limit=limit)
    return all_system_info

@router.delete("/system_info/{system_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_system_info(system_name: str, db: Session = Depends(get_db)):
    if not crud.delete_system_info(db=db, system_name=system_name):
        raise HTTPException(status_code=404, detail="System Info not found")
    return {"ok": True}
