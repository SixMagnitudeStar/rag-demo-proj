from sqlalchemy.orm import Session
from . import models, schemas

def get_employee(db: Session, employee_id: str):
    return db.query(models.Employee).filter(models.Employee.employee_id == employee_id).first()

def get_employees(db: Session, skip: int = 0, limit: int = 100):
    employees = db.query(models.Employee).offset(skip).limit(limit).all()
    print(f"Debug: get_employees - Retrieved {len(employees)} employees. First: {employees[0].__dict__ if employees else 'None'}")
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

# Order CRUD operations
def get_order(db: Session, order_id: str):
    return db.query(models.Order).filter(models.Order.order_id == order_id).first()

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).offset(skip).limit(limit).all()

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

# SystemInfo CRUD operations
def get_system_info(db: Session, system_name: str):
    return db.query(models.SystemInfo).filter(models.SystemInfo.system_name == system_name).first()

def get_all_system_info(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.SystemInfo).offset(skip).limit(limit).all()

def create_system_info(db: Session, system_info: schemas.SystemInfoCreate):
    db_system_info = models.SystemInfo(
        system_name=system_info.system_name,
        data_query_function_name=system_info.data_query_function_name
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
