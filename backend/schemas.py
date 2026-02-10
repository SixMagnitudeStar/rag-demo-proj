from typing import Optional
from pydantic import BaseModel

class EmployeeBase(BaseModel):
    employee_id: str
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None # Added gender field
    age: Optional[int] = None   # Added age field

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    id: int

    class Config:
        from_attributes = True # This used to be orm_mode = True in Pydantic v1

class OrderBase(BaseModel):
    order_id: str
    order_date: str
    order_amount: Optional[int] = None

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int

    class Config:
        from_attributes = True

class SystemInfoBase(BaseModel):
    system_name: str
    data_query_function_name: str
    filterable_columns: Optional[str] = None # JSON string of a list
    frontend_route_name: Optional[str] = None # New field for frontend routing

class SystemInfoCreate(SystemInfoBase):
    pass

class SystemInfo(SystemInfoBase):
    id: int

    class Config:
        from_attributes = True
