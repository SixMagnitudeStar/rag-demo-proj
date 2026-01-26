<script setup lang="ts">
import { ref, reactive } from 'vue'

const userPrompt = ref('');
const llmResponse = ref('');
const toolResult = ref<any>(null);
const isLoading = ref(false);

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
    llmResponse.value = data.llm_text_response;
    toolResult.value = data.tool_result;

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
    <h1>系統問答</h1>

    <div class="prompt-input-area">
      <textarea
        v-model="userPrompt"
        placeholder="請輸入您的問題，例如：查詢員工資料，或是查看訂單狀況。"
        rows="5"
        :disabled="isLoading"
      ></textarea>
      <button @click="sendMessage" :disabled="isLoading">
        <span v-if="isLoading">處理中...</span>
        <span v-else>提問</span>
      </button>
    </div>

    <div v-if="llmResponse || toolResult" class="response-area">
      <h2>回答</h2>
      <p class="llm-response-text">{{ llmResponse }}</p>


    </div>
  </div>
</template>

<style scoped>
.qna-container {
  max-width: 900px;
  margin: 2rem auto;
  padding: 1.5rem;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

h1 {
  color: #333;
  text-align: center;
  margin-bottom: 2rem;
}

.prompt-input-area {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2rem;
}

textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  resize: vertical;
}

button {
  padding: 10px 15px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1.1rem;
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
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

h2 {
  color: #333;
  margin-bottom: 1rem;
}

.llm-response-text {
  background-color: #e8f5e9;
  padding: 10px;
  border-radius: 4px;
  border-left: 4px solid #42b983;
  margin-bottom: 1rem;
  white-space: pre-wrap; /* Preserves whitespace and wraps text */
  word-wrap: break-word; /* Breaks long words */
}

.tool-result-display {
  margin-top: 1.5rem;
  border-top: 1px solid #eee;
  padding-top: 1.5rem;
}

h3 {
  color: #555;
  margin-bottom: 0.8rem;
}

pre {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', Courier, monospace;
}
</style>
