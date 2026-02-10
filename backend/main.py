from typing import List, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import json
import inspect

from . import crud, models, schemas
from .database import SessionLocal, engine
## from .llm_service import get_llm_response_with_tool_call, get_llm_final_answer # Import new summarization function
from .llm_service import ERPAssistant
from .routers import employees, orders, system_info # Import the new routers



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

# Global map to store dynamically loaded functions and system info
FUNCTION_MAP: Dict[str, Any] = {}
SYSTEM_INFO_MAP: Dict[str, models.SystemInfo] = {}
CONTEXT_LENGTH_LIMIT = 8000  # Max characters for data to be sent to LLM

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    print("Application startup event: Populating FUNCTION_MAP and SYSTEM_INFO_MAP.")
    db = SessionLocal()
    try:
        system_infos = crud.get_all_system_info(db)
        if not system_infos:
            print("No SystemInfo found in DB. Please add some via /api/system_info/ endpoint.")
            print("Example: system_name='員工管理', data_query_function_name='get_employees', filterable_columns='[\"name\", \"address\"]', frontend_route_name='employees'")

        for info in system_infos:
            func_name = info.data_query_function_name
            if hasattr(crud, func_name) and inspect.isfunction(getattr(crud, func_name)):
                FUNCTION_MAP[func_name] = getattr(crud, func_name)
                SYSTEM_INFO_MAP[func_name] = info # Cache the whole info object
                print(f"Mapped function: {func_name}")
            else:
                print(f"Warning: Function '{func_name}' not found or not callable in crud for SystemInfo '{info.system_name}'")
    finally:
        db.close()
    print(f"FUNCTION_MAP populated: {list(FUNCTION_MAP.keys())}")


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

# Include routers
app.include_router(employees.router, prefix="/api", tags=["employees"])
app.include_router(orders.router, prefix="/api", tags=["orders"])
app.include_router(system_info.router, prefix="/api", tags=["system_info"])


# 建立助理實例
assistant = ERPAssistant()

# LLM Q&A Endpoint
@app.post("/api/qna/")
async def qna_endpoint(request: Request, db: Session = Depends(get_db)):
    user_data = await request.json()
    user_prompt = user_data.get("user_prompt")

    if not user_prompt:
        raise HTTPException(status_code=400, detail="User prompt is required.")

    # --- First LLM Call: Process user query for intent and parameters ---
    llm_response_parsed = await assistant.get_question_scope(
        user_prompt=user_prompt, db=db
    )

    request_type = llm_response_parsed.get("request_type", "UNKNOWN")
    llm_initial_text_response = llm_response_parsed.get("llm_text_response", "未能從LLM獲取文字回應。")

    if request_type == "OPEN_APPLICATION":
        frontend_route_name = llm_response_parsed.get("frontend_route_name")
        if frontend_route_name:
            return {
                "request_type": "OPEN_APPLICATION",
                "llm_text_response": llm_initial_text_response,
                "frontend_route_name": frontend_route_name
            }
        else:
            return {
                "request_type": "UNKNOWN",
                "llm_text_response": "抱歉，我無法識別要開啟哪個應用程式。請提供更明確的名稱。"
            }
    
    elif request_type == "ASK_SYSTEM_QUESTION":
        tool_calls = llm_response_parsed.get("tool_calls", [])

        combined_tool_results = []
        data_too_large = False
        guidance_message = ""

        # Execute recommended tool functions with extracted parameters
        if tool_calls and isinstance(tool_calls, list):
            for tool_call in tool_calls:
                function_name = tool_call.get("function_name")
                parameters = tool_call.get("parameters", {})
                system_name = tool_call.get("system_name", "未知系統") # LLM now provides system_name

                # The `system_info` object from SYSTEM_INFO_MAP contains filterable_columns
                system_info = SYSTEM_INFO_MAP.get(function_name)
                # Fallback to system_name from LLM if not found in map (shouldn't happen if LLM is good)
                if not system_info:
                    # Try to get system_info by name if function_name not directly mapped
                    for info_obj in SYSTEM_INFO_MAP.values():
                        if info_obj.system_name == system_name:
                            system_info = info_obj
                            break


                if function_name and function_name in FUNCTION_MAP:
                    try:
                        tool_func = FUNCTION_MAP[function_name]
                        # Check if tool_func expects a 'filters' argument
                        if 'filters' in inspect.signature(tool_func).parameters:
                            data = tool_func(db=db, filters=parameters)
                        else: # Fallback for functions not yet updated with filters
                            data = tool_func(db=db) 

                        # Dynamically get the Pydantic schema for data validation
                        schema_map = {
                            "get_employees": schemas.Employee,
                            "get_orders": schemas.Order,
                            "get_all_system_info": schemas.SystemInfo,
                        }
                        ItemSchema = schema_map.get(function_name)
                        
                        formatted_data = []
                        if ItemSchema:
                            formatted_data = [ItemSchema.model_validate(item).model_dump() for item in data]
                        else:
                            # Fallback for unknown schemas
                            formatted_data = [{"error": f"Unknown schema for function {function_name}", "data": str(data)}]

                        # Check data size before adding to results
                        data_str = json.dumps(formatted_data, ensure_ascii=False)
                        if len(data_str) > CONTEXT_LENGTH_LIMIT:
                            data_too_large = True
                            filterable_cols = system_info.filterable_columns if system_info and system_info.filterable_columns else "無"
                            guidance_message = (
                                f"您查詢的 '{system_name}' 資料量過大，無法直接回答。\n"
                                f"請提供更具體的篩選條件，您可以針對以下欄位進行篩選：{filterable_cols}"
                            )
                            # We break here because one oversized result is enough to stop
                            break 
                        
                        combined_tool_results.append({
                            "system_name": system_name,
                            "function_name": function_name,
                            "data": formatted_data
                        })
                    except Exception as e:
                        combined_tool_results.append({
                            "system_name": system_name,
                            "function_name": function_name,
                            "error": f"執行函數 '{function_name}' 失敗: {str(e)}"
                        })
                else:
                    combined_tool_results.append({
                        "system_name": system_name,
                        "function_name": function_name,
                        "error": f"LLM推薦的函數 '{function_name}' 不存在或未被映射。"
                    })

        # --- Second LLM Call: Summarize data or return guidance ---
        if data_too_large:
            final_llm_response = guidance_message
        elif combined_tool_results:
            final_llm_response = await assistant.get_llm_final_answer(
                user_prompt, combined_tool_results
            )
        else:
            final_llm_response = llm_initial_text_response # If no tool_calls, use initial LLM response

        return {
            "request_type": "ASK_SYSTEM_QUESTION",
            "llm_text_response": final_llm_response,
            "tool_result": combined_tool_results if not data_too_large else None
        }

    else: # UNKNOWN or other request_type
        return {
            "request_type": "UNKNOWN",
            "llm_text_response": llm_initial_text_response
        }

# async def qna_endpoint(request: Request, db: Session = Depends(get_db)):
#     user_data = await request.json()
#     user_prompt = user_data.get("user_prompt")

#     if not user_prompt:
#         raise HTTPException(status_code=400, detail="User prompt is required.")

#     # Generate system prompt for LLM based on available SystemInfo
#     system_infos = crud.get_all_system_info(db)
#     available_tools_description = []
#     for info in system_infos:
#         available_tools_description.append(
#             f"- 系統名稱: {info.system_name}, 查詢函數: {info.data_query_function_name}"
#         )

#     system_prompt_for_tool_call = (
#         "你是一個智能助理，可以根據用戶的問題判斷需要查詢哪些系統的資料。 "
#         "以下是你目前可以查詢的系統資訊列表:\n" +
#         "\n".join(available_tools_description) +
#         "\n\n請根據用戶的問題，判斷需要查詢哪些系統的資料 (可以是一個或多個)。 "
#         "以 JSON 格式回應，包含 'llm_text_response' 和 'tool_calls' (一個列表)。 "
#         "如果無法判斷或不需要查詢資料，則 'tool_calls' 可以是空列表或省略。 "
#         "每個 'tool_call' 物件應包含 'system_name' 和 'function_name' (例如: {\"system_name\": \"員工管理\", \"function_name\": \"get_employees\"})。 "
#         "不要包含 'parameters'，因為目前函數不需要參數。\n"
#         "範例回應 (單一工具呼叫):\n"
#         "{\"llm_text_response\": \"好的，我會為您查詢員工資料。\", \"tool_calls\": [{\"system_name\": \"員工管理\", \"function_name\": \"get_employees\"}]}"
#         "\n範例回應 (多個工具呼叫):\n"
#         "{\"llm_text_response\": \"好的，我會為您查詢員工和訂單資料。\", \"tool_calls\": [{\"system_name\": \"員工管理\", \"function_name\": \"get_employees\"}, {\"system_name\": \"訂單管理\", \"function_name\": \"get_orders\"}]}"
#         "\n或者:\n"
#         "{\"llm_text_response\": \"很抱歉，我無法處理您的請求，請提供更具體的資訊。\", \"tool_calls\": []}"
#     )



#     # First LLM call: Determine tool calls
#     llm_tool_call_response = await get_llm_response_with_tool_call(system_prompt_for_tool_call, user_prompt)
    
#     llm_initial_text_response = llm_tool_call_response.get("llm_text_response", "未能從LLM獲取文字回應。")
#     tool_calls = llm_tool_call_response.get("tool_calls", [])
#     print(f"Debug: LLM Initial Text Response: {llm_initial_text_response}")
#     print(f"Debug: Tool Calls from LLM: {tool_calls}")

#     combined_tool_results = []

#     if tool_calls and isinstance(tool_calls, list):
#         for tool_call in tool_calls:
#             function_name = tool_call.get("function_name")
#             system_name = tool_call.get("system_name", "未知系統")
#             if function_name and function_name in FUNCTION_MAP:
#                 try:
#                     tool_func = FUNCTION_MAP[function_name]
                    
#                     if 'db' in inspect.signature(tool_func).parameters:
#                         data = tool_func(db=db)
#                     else:
#                         data = tool_func()
                    
#                     # Convert SQLAlchemy models to Pydantic schemas for consistent JSON output
#                     formatted_data = []
#                     if function_name == "get_employees":
#                         formatted_data = [schemas.Employee.model_validate(item).model_dump() for item in data]
#                     elif function_name == "get_orders":
#                         formatted_data = [schemas.Order.model_validate(item).model_dump() for item in data]
#                     elif function_name == "get_all_system_info":
#                         formatted_data = [schemas.SystemInfo.model_validate(item).model_dump() for item in data]
#                     else:
#                         formatted_data = [{"error": f"Unknown schema for function {function_name}", "data": str(data)}]
                    
#                     combined_tool_results.append({
#                         "system_name": system_name,
#                         "function_name": function_name,
#                         "data": formatted_data
#                     })
#                 except Exception as e:
#                     combined_tool_results.append({
#                         "system_name": system_name,
#                         "function_name": function_name,
#                         "error": f"執行查詢函數 '{function_name}' 失敗: {str(e)}"
#                     })
#             else:
#                 combined_tool_results.append({
#                     "system_name": system_name,
#                     "function_name": function_name,
#                     "error": f"LLM推薦的函數 '{function_name}' 不存在或未被映射。"
#                 })
    
#     print(f"Debug: Combined Tool Results before final LLM call: {combined_tool_results}")
#     final_llm_response = llm_initial_text_response # Default to initial response

#     # Second LLM call: Summarize retrieved data
#     if combined_tool_results: # Only call summarization LLM if there's data to summarize
#         final_llm_response = await get_llm_final_answer(user_prompt, combined_tool_results)

#     return {
#         "llm_text_response": final_llm_response,
#         "tool_result": combined_tool_results if combined_tool_results else None
#     }
