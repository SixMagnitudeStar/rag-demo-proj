import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from sqlalchemy.orm import Session
from . import crud, models

load_dotenv()

class ERPAssistant:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError("錯誤：未設定 Gemini API 金鑰，請檢查 .env 檔案。")
        genai.configure(api_key=self.api_key)

    async def get_question_scope(self, user_prompt: str, db: Session) -> dict:
        """
        Processes the user's prompt to determine intent (open application or ask system question)
        and extracts relevant information (frontend route or data query parameters).
        """
        # Fetch all system info from the database to build the dynamic prompt
        system_infos = crud.get_all_system_info(db)

        application_descriptions = []
        tool_descriptions = []

        for info in system_infos:
            # For "open application" intent
            if info.frontend_route_name:
                application_descriptions.append(
                    f"- 應用程式名稱: {info.system_name}\n  - 路由名稱: `{info.frontend_route_name}`"
                )
            
            # For "ask system question" intent
            description = f"- 系統名稱: {info.system_name}\n  - 函數名稱: `{info.data_query_function_name}`"
            if info.filterable_columns:
                try:
                    columns = json.loads(info.filterable_columns)
                    description += f"\n  - 可用篩選欄位: {columns}"
                except json.JSONDecodeError:
                    description += f"\n  - 可用篩選欄位: {info.filterable_columns}" # Fallback
            tool_descriptions.append(description)

        system_prompt = f"""
你是一個強大的企業助理，你的任務是根據用戶的問題，判斷其意圖並提供相應的回應。

# 可識別意圖類型
1.  **開啟程式 (OPEN_APPLICATION)**: 用戶想要打開某個應用程式或頁面。
2.  **詢問系統問題 (ASK_SYSTEM_QUESTION)**: 用戶想要查詢系統資料。

# 可用資源
## 可開啟的應用程式列表
{
    "\n".join(application_descriptions)
    if application_descriptions
    else "目前沒有可開啟的應用程式資訊。"
}

## 可查詢的系統資料函數列表
以下是你可用於查詢資料的函數以及它們的詳細資訊：
{
    "\n".join(tool_descriptions)
    if tool_descriptions
    else "目前沒有可查詢的系統資料函數資訊。"
}

# 你的任務
1.  **分析問題**: 仔細閱讀用戶的問題。
2.  **判斷意圖**: 判斷用戶的意圖是「開啟程式」還是「詢問系統問題」。
3.  **提取資訊**:
    *   **如果意圖是「開啟程式」**: 從用戶問題中提取出要開啟的應用程式的「路由名稱」。
    *   **如果意圖是「詢問系統問題」**: 從用戶問題中提取出要查詢的「函數名稱」以及任何與該函數「可用篩選欄位」相符的參數值。
4.  **格式化輸出**: 你的回答必須是嚴格的 JSON 格式，其中包含：
    - `request_type` (字串): 意圖類型，值為 "OPEN_APPLICATION" 或 "ASK_SYSTEM_QUESTION"。
    - `llm_text_response` (字串): 你對用戶的初步回應，例如 "好的，正在為您打開..." 或 "好的，正在為您查詢..."。

    **如果 `request_type` 是 "OPEN_APPLICATION"**:
    - 額外包含 `frontend_route_name` (字串): 要開啟的應用程式頁面的路由名稱。

    **如果 `request_type` 是 "ASK_SYSTEM_QUESTION"**:
    - 額外包含 `tool_calls` (列表): 一個包含所有要呼叫的工具的列表。每個物件應包含：
        - `function_name` (字串): 要呼叫的函數名稱。
        - `system_name` (字串): 該函數對應的系統名稱。
        - `parameters` (物件): 一個包含從用戶問題中提取的篩選欄位和值的物件。

# 範例
## 範例 1: 開啟程式
用戶問題: "打開員工管理頁面"
你的 JSON 回答:
```json
{{
  "request_type": "OPEN_APPLICATION",
  "llm_text_response": "好的，正在為您打開員工管理頁面。",
  "frontend_route_name": "employees"
}}
```

## 範例 2: 詢問系統問題
用戶問題: "我想找住在台北市，姓陳的員工"
你的 JSON 回答:
```json
{{
  "request_type": "ASK_SYSTEM_QUESTION",
  "llm_text_response": "好的，正在為您查詢住在台北市且姓陳的員工資料。",
  "tool_calls": [
    {{
      "function_name": "get_employees",
      "system_name": "員工管理",
      "parameters": {{
        "address": "台北市",
        "name": "陳"
      }}
    }}
  ]
}}
```

# 重要規則
- 如果用戶問題沒有提供任何可以用於篩選的值，`parameters` 應為空物件 `{{}}`。
- 如果沒有判斷出明確意圖或無法提取所需資訊，`request_type` 應設定為 "UNKNOWN" 並提供 `llm_text_response`。
- 你的回答只能是 JSON，不要包含任何額外的文字或解釋。
"""

    async def get_llm_final_answer(self, original_prompt: str, retrieved_data_json: dict) -> str:
        print("--- LLM INTERACTION WITH GOOGLE GEMINI (FINAL ANSWER) ---")

        try:
            summarization_prompt = (
                f"你是一個智能助理，請根據以下用戶問題和所提供的數據，用繁體中文生成一個清晰、簡潔的回答。\n"
                f"用戶問題: {original_prompt}\n"
                f"查詢到的數據: {json.dumps(retrieved_data_json, ensure_ascii=False, indent=2)}\n\n"
                f"請整合這些資訊並直接提供最終答案，不要提到數據來源或數據本身，只需提供回答。"
            )

            messages = [
                {"role": "user", "parts": [summarization_prompt]},
            ]

            response = await self.model.generate_content_async(messages)
            final_answer = response.text
            print(f"Final LLM Answer: {final_answer}")
            return final_answer

        except Exception as e:
            print(f"Error calling Gemini LLM (Final Answer): {e}")
            return f"在生成最終回答時發生錯誤: {e}"

