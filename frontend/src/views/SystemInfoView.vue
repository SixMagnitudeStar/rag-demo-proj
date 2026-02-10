<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import type { Ref } from 'vue'
import { BASE_API_URL } from '@/api';

interface SystemInfo {
  id: number;
  system_name: string;
  data_query_function_name: string;
  filterable_columns: string | null;
  frontend_route_name: string | null;
}

const systemInfoList: Ref<SystemInfo[]> = ref([]);
const newSystemInfo = reactive({
  system_name: '',
  data_query_function_name: '',
  filterable_columns: '',
  frontend_route_name: ''
});

const fetchSystemInfo = async () => {
  try {
    const response = await fetch(`${BASE_API_URL}/api/system_info/`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    systemInfoList.value = await response.json();
  } catch (error) {
    console.error("Error fetching system info:", error);
  }
};

const addSystemInfo = async () => {
  if (!newSystemInfo.system_name || !newSystemInfo.data_query_function_name) {
    alert('系統名稱和資料查詢函數名稱為必填欄位！');
    return;
  }

  // Prepare payload, setting filterable_columns and frontend_route_name to null if empty
  const payload = {
    ...newSystemInfo,
    filterable_columns: newSystemInfo.filterable_columns || null,
    frontend_route_name: newSystemInfo.frontend_route_name || null
  };

  // Optional: Basic JSON validation for filterable_columns
  if (payload.filterable_columns) {
    try {
      JSON.parse(payload.filterable_columns);
    } catch (e) {
      alert('可篩選欄位格式不正確，請輸入有效的 JSON 陣列字串，例如：["name", "address"]');
      return;
    }
  }


  try {
    const response = await fetch(`${BASE_API_URL}/api/system_info/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    // Clear form and refetch system info
    newSystemInfo.system_name = '';
    newSystemInfo.data_query_function_name = '';
    newSystemInfo.filterable_columns = '';
    newSystemInfo.frontend_route_name = '';
    fetchSystemInfo();
  } catch (error: any) {
    alert(`新增系統資訊失敗: ${error.message}`);
    console.error("Error adding system info:", error);
  }
};

const deleteSystemInfo = async (systemName: string) => {
  if (!confirm(`確定要刪除系統名稱為 ${systemName} 的資料嗎？`)) {
    return;
  }

  try {
    const response = await fetch(`${BASE_API_URL}/api/system_info/${systemName}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    // Refetch system info or remove from local array
    fetchSystemInfo();
  } catch (error: any) {
    alert(`刪除系統資訊失敗: ${error.message}`);
    console.error("Error deleting system info:", error);
  }
};

onMounted(fetchSystemInfo);
</script>

<template>
  <div class="system-info-management">
    <h1>系統資訊檢索管理</h1>

    <div class="add-system-info-form">
      <h2>新增系統資訊</h2>
      <form @submit.prevent="addSystemInfo">
        <div class="form-group">
          <label for="system_name">系統名稱: *</label>
          <input type="text" id="system_name" v-model="newSystemInfo.system_name" required />
        </div>
        <div class="form-group">
          <label for="data_query_function_name">資料查詢函數名稱: *</label>
          <input type="text" id="data_query_function_name" v-model="newSystemInfo.data_query_function_name" required />
        </div>
        <div class="form-group">
          <label for="filterable_columns">可篩選欄位 (JSON 格式):</label>
          <input type="text" id="filterable_columns" v-model="newSystemInfo.filterable_columns" placeholder='["name", "address"]' />
        </div>
        <div class="form-group">
          <label for="frontend_route_name">前端路由名稱:</label>
          <input type="text" id="frontend_route_name" v-model="newSystemInfo.frontend_route_name" placeholder='例如: employees, orders' />
        </div>
        <button type="submit">新增系統資訊</button>
      </form>
    </div>

    <div class="system-info-list">
      <h2>現有系統資訊</h2>
      <p v-if="systemInfoList.length === 0">目前沒有系統資訊。</p>
      <table v-else>
        <thead>
          <tr>
            <th>ID</th>
            <th>系統名稱</th>
            <th>資料查詢函數名稱</th>
            <th>可篩選欄位</th>
            <th>前端路由名稱</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="info in systemInfoList" :key="info.id">
            <td>{{ info.id }}</td>
            <td>{{ info.system_name }}</td>
            <td>{{ info.data_query_function_name }}</td>
            <td>{{ info.filterable_columns || '無' }}</td>
            <td>{{ info.frontend_route_name || '無' }}</td>
            <td>
              <button @click="deleteSystemInfo(info.system_name)" class="delete-button">刪除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.system-info-management {
  max-width: 900px;
  margin: 2rem auto;
  padding: 1.5rem;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

h1, h2 {
  color: #333;
  text-align: center;
  margin-bottom: 1.5rem;
}

.add-system-info-form, .system-info-list {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-weight: bold;
}

.form-group input[type="text"] {
  width: calc(100% - 20px);
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

button[type="submit"] {
  display: block;
  width: 100%;
  padding: 10px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button[type="submit"]:hover {
  background-color: #36a16d;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

th, td {
  border: 1px solid #eee;
  padding: 10px;
  text-align: left;
}

th {
  background-color: #f2f2f2;
  font-weight: bold;
  color: #333;
}

tr:nth-child(even) {
  background-color: #f8f8f8;
}

.delete-button {
  background-color: #e74c3c;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.delete-button:hover {
  background-color: #c0392b;
}

p {
  text-align: center;
  color: #777;
}
</style>
