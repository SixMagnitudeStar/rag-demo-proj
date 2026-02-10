import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Get the base directory of the project (one level up from 'backend')
BASE_DIR = Path(__file__).resolve().parent.parent

# Check for DATABASE_URL environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")

# 修改這部分
if not DATABASE_URL:
    # 建議直接寫死路徑在 /app 下，或者當前目錄
    DATABASE_URL = "sqlite:///./sql_app.db"

# 建立 engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
