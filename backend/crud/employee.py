from sqlalchemy.orm import Session
from typing import Dict, Any
from .. import models, schemas

def get_employee(db: Session, employee_id: str):
    return db.query(models.Employee).filter(models.Employee.employee_id == employee_id).first()

def get_employees(db: Session, filters: Dict[str, Any] = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Employee)
    if filters:
        for column, value in filters.items():
            if hasattr(models.Employee, column):
                # Use 'like' for partial string matching
                query = query.filter(getattr(models.Employee, column).like(f"%{value}%"))

    employees = query.offset(skip).limit(limit).all()
    print(f"Debug: get_employees - Retrieved {len(employees)} employees with filters {filters}. First: {employees[0].__dict__ if employees else 'None'}")
    return employees

def create_employee(db: Session, employee: schemas.EmployeeCreate):
    print(f"Debug: create_employee - Incoming data: {employee.model_dump()}")
    db_employee = models.Employee(
        employee_id=employee.employee_id,
        name=employee.name,
        phone=employee.phone,
        address=employee.address,
        email=employee.email,
        gender=employee.gender, # Added gender field
        age=employee.age        # Added age field
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    print(f"Debug: create_employee - Saved db_employee: {db_employee.__dict__}")
    return db_employee

def delete_employee(db: Session, employee_id: str):
    db_employee = db.query(models.Employee).filter(models.Employee.employee_id == employee_id).first()
    if db_employee:
        db.delete(db_employee)
        db.commit()
        return True
    return False
