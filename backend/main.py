from typing import List, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import json
import inspect

from . import crud, models, schemas
from .database import SessionLocal, engine
from .llm_service import get_llm_response_with_tool_call, get_llm_final_answer # Import new summarization function

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:5173",  # Allow the Vue dev server
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global map to store dynamically loaded functions from crud.py
FUNCTION_MAP: Dict[str, Any] = {}

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    print("Application startup event: Populating FUNCTION_MAP.")
    db = SessionLocal()
    try:
        system_infos = crud.get_all_system_info(db)
        if not system_infos:
            print("No SystemInfo found in DB. Please add some via /api/system_info/ endpoint.")
            print("Example: system_name='員工管理', data_query_function_name='get_employees'")

        for info in system_infos:
            func_name = info.data_query_function_name
            # Dynamically get the function from crud module
            if hasattr(crud, func_name) and inspect.isfunction(getattr(crud, func_name)):
                FUNCTION_MAP[func_name] = getattr(crud, func_name)
                print(f"Mapped function: {func_name}")
            else:
                print(f"Warning: Function '{func_name}' not found or not callable in crud.py for SystemInfo '{info.system_name}'")
    finally:
        db.close()
    print(f"FUNCTION_MAP populated: {list(FUNCTION_MAP.keys())}")


@app.get("/")
def read_root():
    return {"Hello": "World from FastAPI with SQLite and LLM Integration"}

# Employee Endpoints
@app.post("/api/employees/", response_model=schemas.Employee, status_code=status.HTTP_201_CREATED)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = crud.get_employee(db, employee_id=employee.employee_id)
    if db_employee:
        raise HTTPException(status_code=400, detail="Employee ID already registered")
    return crud.create_employee(db=db, employee=employee)

@app.get("/api/employees/", response_model=List[schemas.Employee])
def read_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    employees = crud.get_employees(db, skip=skip, limit=limit)
    return employees

@app.delete("/api/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: str, db: Session = Depends(get_db)):
    if not crud.delete_employee(db=db, employee_id=employee_id):
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"ok": True}

# Order Endpoints
@app.post("/api/orders/", response_model=schemas.Order, status_code=status.HTTP_201_CREATED)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    db_order = crud.get_order(db, order_id=order.order_id)
    if db_order:
        raise HTTPException(status_code=400, detail="Order ID already registered")
    return crud.create_order(db=db, order=order)

@app.get("/api/orders/", response_model=List[schemas.Order])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    orders = crud.get_orders(db, skip=skip, limit=limit)
    return orders

@app.delete("/api/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: str, db: Session = Depends(get_db)):
    if not crud.delete_order(db=db, order_id=order_id):
        raise HTTPException(status_code=404, detail="Order not found")
    return {"ok": True}

# SystemInfo Endpoints
@app.post("/api/system_info/", response_model=schemas.SystemInfo, status_code=status.HTTP_201_CREATED)
def create_system_info(system_info: schemas.SystemInfoCreate, db: Session = Depends(get_db)):
    db_system_info = crud.get_system_info(db, system_name=system_info.system_name)
    if db_system_info:
        raise HTTPException(status_code=400, detail="System Name already registered")
    return crud.create_system_info(db=db, system_info=system_info)

@app.get("/api/system_info/", response_model=List[schemas.SystemInfo])
def read_all_system_info(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    all_system_info = crud.get_all_system_info(db, skip=skip, limit=limit)
    return all_system_info

@app.delete("/api/system_info/{system_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_system_info(system_name: str, db: Session = Depends(get_db)):
    if not crud.delete_system_info(db=db, system_name=system_name):
        raise HTTPException(status_code=404, detail="System Info not found")
    return {"ok": True}

# LLM Q&A Endpoint
@app.post("/api/qna/")
async def qna_endpoint(request: Request, db: Session = Depends(get_db)):
    user_data = await request.json()
    user_prompt = user_data.get("user_prompt")

    if not user_prompt:
        raise HTTPException(status_code=400, detail="User prompt is required.")

    # Generate system prompt for LLM based on available SystemInfo
    system_infos = crud.get_all_system_info(db)
    available_tools_description = []
    for info in system_infos:
        available_tools_description.append(
            f"- 系統名稱: {info.system_name}, 查詢函數: {info.data_query_function_name}"
        )

    system_prompt_for_tool_call = (
        "你是一個智能助理，可以根據用戶的問題判斷需要查詢哪些系統的資料。 "
        "以下是你目前可以查詢的系統資訊列表:\n" +
        "\n".join(available_tools_description) +
        "\n\n請根據用戶的問題，判斷需要查詢哪些系統的資料 (可以是一個或多個)。 "
        "以 JSON 格式回應，包含 'llm_text_response' 和 'tool_calls' (一個列表)。 "
        "如果無法判斷或不需要查詢資料，則 'tool_calls' 可以是空列表或省略。 "
        "每個 'tool_call' 物件應包含 'system_name' 和 'function_name' (例如: {\"system_name\": \"員工管理\", \"function_name\": \"get_employees\"})。 "
        "不要包含 'parameters'，因為目前函數不需要參數。\n"
        "範例回應 (單一工具呼叫):\n"
        "{\"llm_text_response\": \"好的，我會為您查詢員工資料。\", \"tool_calls\": [{\"system_name\": \"員工管理\", \"function_name\": \"get_employees\"}]}"
        "\n範例回應 (多個工具呼叫):\n"
        "{\"llm_text_response\": \"好的，我會為您查詢員工和訂單資料。\", \"tool_calls\": [{\"system_name\": \"員工管理\", \"function_name\": \"get_employees\"}, {\"system_name\": \"訂單管理\", \"function_name\": \"get_orders\"}]}"
        "\n或者:\n"
        "{\"llm_text_response\": \"很抱歉，我無法處理您的請求，請提供更具體的資訊。\", \"tool_calls\": []}"
    )

    # First LLM call: Determine tool calls
    llm_tool_call_response = await get_llm_response_with_tool_call(system_prompt_for_tool_call, user_prompt)
    
    llm_initial_text_response = llm_tool_call_response.get("llm_text_response", "未能從LLM獲取文字回應。")
    tool_calls = llm_tool_call_response.get("tool_calls", [])
    print(f"Debug: LLM Initial Text Response: {llm_initial_text_response}")
    print(f"Debug: Tool Calls from LLM: {tool_calls}")

    combined_tool_results = []

    if tool_calls and isinstance(tool_calls, list):
        for tool_call in tool_calls:
            function_name = tool_call.get("function_name")
            system_name = tool_call.get("system_name", "未知系統")
            if function_name and function_name in FUNCTION_MAP:
                try:
                    tool_func = FUNCTION_MAP[function_name]
                    
                    if 'db' in inspect.signature(tool_func).parameters:
                        data = tool_func(db=db)
                    else:
                        data = tool_func()
                    
                    # Convert SQLAlchemy models to Pydantic schemas for consistent JSON output
                    formatted_data = []
                    if function_name == "get_employees":
                        formatted_data = [schemas.Employee.model_validate(item).model_dump() for item in data]
                    elif function_name == "get_orders":
                        formatted_data = [schemas.Order.model_validate(item).model_dump() for item in data]
                    elif function_name == "get_all_system_info":
                        formatted_data = [schemas.SystemInfo.model_validate(item).model_dump() for item in data]
                    else:
                        formatted_data = [{"error": f"Unknown schema for function {function_name}", "data": str(data)}]
                    
                    combined_tool_results.append({
                        "system_name": system_name,
                        "function_name": function_name,
                        "data": formatted_data
                    })
                except Exception as e:
                    combined_tool_results.append({
                        "system_name": system_name,
                        "function_name": function_name,
                        "error": f"執行查詢函數 '{function_name}' 失敗: {str(e)}"
                    })
            else:
                combined_tool_results.append({
                    "system_name": system_name,
                    "function_name": function_name,
                    "error": f"LLM推薦的函數 '{function_name}' 不存在或未被映射。"
                })
    
    print(f"Debug: Combined Tool Results before final LLM call: {combined_tool_results}")
    final_llm_response = llm_initial_text_response # Default to initial response

    # Second LLM call: Summarize retrieved data
    if combined_tool_results: # Only call summarization LLM if there's data to summarize
        final_llm_response = await get_llm_final_answer(user_prompt, combined_tool_results)

    return {
        "llm_text_response": final_llm_response,
        "tool_result": combined_tool_results if combined_tool_results else None
    }
