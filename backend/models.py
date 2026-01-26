from sqlalchemy import Column, Integer, String
from .database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True)
    gender = Column(String, nullable=True) # Added gender field
    age = Column(Integer, nullable=True)   # Added age field

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, unique=True, index=True, nullable=False)
    order_date = Column(String, nullable=False)
    order_amount = Column(Integer, nullable=True) # Added order_amount field

class SystemInfo(Base):
    __tablename__ = "system_info"

    id = Column(Integer, primary_key=True, index=True)
    system_name = Column(String, unique=True, index=True, nullable=False)
    data_query_function_name = Column(String, nullable=False)
