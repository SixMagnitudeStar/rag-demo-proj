FROM python:3.12-slim

WORKDIR /app

# 1. 先複製依賴文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install "fastapi[standard]"

# 2. 複製整個專案（包含 backend 資料夾）到容器的 /app 內
COPY . .

# 3. 執行指令
# 這裡用 backend.main:app 是因為你在 /app 目錄下，
# 而 backend 資料夾就在 /app 裡面
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]