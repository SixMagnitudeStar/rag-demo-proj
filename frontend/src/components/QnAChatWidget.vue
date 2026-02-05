<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'; // Import useRouter

const userPrompt = ref('');
const llmResponse = ref('');
const toolResult = ref<any>(null);
const isLoading = ref(false);
const router = useRouter(); // Initialize router

const sendMessage = async () => {
  if (!userPrompt.value.trim()) {
    alert('請輸入您的問題！');
    return;
  }

  isLoading.value = true;
  llmResponse.value = '';
  toolResult.value = null;

  try {
    const response = await fetch('http://localhost:8000/api/qna/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ user_prompt: userPrompt.value }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    // Handle different request types from LLM
    if (data.request_type === 'OPEN_APPLICATION') {
      const routeName = data.frontend_route_name;
      if (routeName) {
        llmResponse.value = data.llm_text_response || `正在為您開啟 ${routeName} 頁面...`;
        router.push({ name: routeName });
      } else {
        llmResponse.value = data.llm_text_response || '無法識別要開啟的應用程式頁面。';
      }
    } else if (data.request_type === 'ASK_SYSTEM_QUESTION') {
      llmResponse.value = data.llm_text_response;
      toolResult.value = data.tool_result;
    } else { // UNKNOWN or other types
      llmResponse.value = data.llm_text_response || '抱歉，我不明白您的問題，請再試一次。';
      toolResult.value = null; // Clear any old tool results
    }

    userPrompt.value = ''; // Clear input after sending
  } catch (error: any) {
    llmResponse.value = `查詢失敗: ${error.message}`;
    console.error("Error sending message to Q&A endpoint:", error);
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="qna-container">
    <h3>系統助理</h3>

    <div class="prompt-input-area">
      <textarea
        v-model="userPrompt"
        placeholder="請輸入您需求，例如：開啟訂單管理程式。或者是詢問問題，例如：查詢員工資料，或是查看訂單狀況。"
        rows="5"
        :disabled="isLoading"
      ></textarea>
      <button @click="sendMessage" :disabled="isLoading">
        <span v-if="isLoading">處理中...</span>
        <span v-else>提問</span>
      </button>
    </div>

    <div v-if="llmResponse || toolResult" class="response-area">
      <h3>回答</h3>
      <p class="llm-response-text">{{ llmResponse }}</p>


    </div>
  </div>
</template>

<style scoped>
.qna-container {
  padding: 1rem;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  height: 100%;
}

h3 {
  color: #333;
  text-align: center;
  margin-bottom: 1rem;
}

.prompt-input-area {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  margin-bottom: 1rem;
}

textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
  resize: vertical;
}

button {
  padding: 8px 12px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button:hover:not(:disabled) {
  background-color: #36a16d;
}

button:disabled {
  background-color: #a5d6a7;
  cursor: not-allowed;
}

.response-area {
  background-color: #fff;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  flex-grow: 1;
  overflow-y: auto;
}

.llm-response-text {
  background-color: #e8f5e9;
  padding: 8px;
  border-radius: 4px;
  border-left: 4px solid #42b983;
  margin-bottom: 0.8rem;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.tool-result-display {
  margin-top: 1.2rem;
  border-top: 1px solid #eee;
  padding-top: 1.2rem;
}

pre {
  background-color: #f5f5f5;
  padding: 8px;
  border-radius: 4px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.85rem;
}
</style>
