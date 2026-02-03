import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

class ERPAssistant:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError("錯誤：未設定 Gemini API 金鑰，請檢查 .env 檔案。")
        genai.configure(api_key=self.api_key)

        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.rqeuest_types = "['詢問系統問題', '開啟程式']"


    async def get_user_problem_type(self, user_prompt: str) -> str:
        """
        判斷使用者意圖，回傳 request_types 中對應的字串
        """
        prompt = (
            f"使用者可能的需求類型有: {', '.join(self.request_types)}\n"
            f"請根據以下用戶輸入判斷他這次想做什麼，直接回傳對應的字串:\n"
            f"用戶輸入: {user_prompt}"
        )

        response = await self.model.generate_content_async([{"role": "user", "parts": [prompt]}])
        user_type = response.text.strip()
        
        # 確保 LLM 回傳值在 request_types 裡
        if user_type not in self.request_types:
            user_type = "未知需求"
        return user_type

    async def get_llm_response_with_tool_call(self, system_prompt: str, user_prompt: str) -> dict:
        print("--- LLM INTERACTION WITH GOOGLE GEMINI (TOOL CALL) ---")
        print(f"System Prompt: {system_prompt}")
        print(f"User Prompt: {user_prompt}")

        try:
            messages = [
                {"role": "user", "parts": [system_prompt + "\n\n用戶問題: " + user_prompt]},
            ]

            response = await self.model.generate_content_async(messages)
            llm_response_content = response.text
            print(f"Raw LLM Response (Tool Call): {llm_response_content}")

            # Pre-process: Strip markdown code block delimiters if present
            if llm_response_content.strip().startswith("```json"):
                llm_response_content = llm_response_content.strip()[len("```json"):].strip()
                if llm_response_content.endswith("```"):
                    llm_response_content = llm_response_content[:-len("```")].strip()
            
            try:
                parsed_response = json.loads(llm_response_content)
                llm_text_response = parsed_response.get("llm_text_response", llm_response_content)
                tool_calls = parsed_response.get("tool_calls", [])
                if not isinstance(tool_calls, list):
                    tool_calls = []
                    print("Warning: 'tool_calls' from LLM was not a list. Ignoring tool calls.")
            except json.JSONDecodeError:
                llm_text_response = llm_response_content
                tool_calls = []
                print("Warning: LLM response was not a valid JSON string. Treating as plain text and no tool calls.")

            return {"llm_text_response": llm_text_response, "tool_calls": tool_calls}

        except Exception as e:
            print(f"Error calling Gemini LLM (Tool Call): {e}")
            return {"llm_text_response": f"我目前無法連接到 Gemini 服務或處理請求: {e}", "tool_calls": []}


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
