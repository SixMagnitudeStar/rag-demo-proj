import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

async def get_llm_response_with_tool_call(system_prompt: str, user_prompt: str) -> dict:
    """
    Function to interact with Google Gemini LLM for Q&A and tool calling.
    It expects the LLM to return a JSON string containing a list of tool calls.

    Args:
        system_prompt (str): The system-level instructions for the LLM, including available tools.
        user_prompt (str): The user's question or request.

    Returns:
        dict: A dictionary containing LLM's text response and a list of tool calls.
              Example: {"llm_text_response": "...", "tool_calls": [...]}
              Or:      {"llm_text_response": "..."}
    """
    print("--- LLM INTERACTION WITH GOOGLE GEMINI (TOOL CALL) ---")
    print(f"System Prompt: {system_prompt}")
    print(f"User Prompt: {user_prompt}")

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    print(f"Debug: GEMINI_API_KEY loaded: {bool(GEMINI_API_KEY)}")
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not found in .env")
        return {"llm_text_response": "錯誤：未設定 Gemini API 金鑰，請檢查 .env 檔案。", "tool_calls": []}

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash') # Using 'gemini-1.5-flash' model for tool calling

        messages = [
            {"role": "user", "parts": [system_prompt + "\n\n用戶問題: " + user_prompt]},
        ]

        response = await model.generate_content_async(messages)
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
            tool_calls = parsed_response.get("tool_calls", []) # Expecting a list now
            if not isinstance(tool_calls, list): # Ensure it's a list
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

async def get_llm_final_answer(original_prompt: str, retrieved_data_json: dict) -> str:
    """
    Function to get a final, summarized answer from the LLM based on the original prompt
    and retrieved data.

    Args:
        original_prompt (str): The user's original question.
        retrieved_data_json (dict): The combined data retrieved from tool calls, in JSON format.

    Returns:
        str: The LLM's final, summarized answer.
    """
    print("--- LLM INTERACTION WITH GOOGLE GEMINI (FINAL ANSWER) ---")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        return "錯誤：未設定 Gemini API 金鑰，無法生成最終回答。"

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash') # Using 'gemini-1.5-flash' model for summarization

        summarization_prompt = (
            f"你是一個智能助理，請根據以下用戶問題和所提供的數據，用繁體中文生成一個清晰、簡潔的回答。\n"
            f"用戶問題: {original_prompt}\n"
            f"查詢到的數據: {json.dumps(retrieved_data_json, ensure_ascii=False, indent=2)}\n\n"
            f"請整合這些資訊並直接提供最終答案，不要提到數據來源或數據本身，只需提供回答。"
        )

        messages = [
            {"role": "user", "parts": [summarization_prompt]},
        ]

        response = await model.generate_content_async(messages)
        final_answer = response.text
        print(f"Final LLM Answer: {final_answer}")
        return final_answer

    except Exception as e:
        print(f"Error calling Gemini LLM (Final Answer): {e}")
        return f"在生成最終回答時發生錯誤: {e}"

