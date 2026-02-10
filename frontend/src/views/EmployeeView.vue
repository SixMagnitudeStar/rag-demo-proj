<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import type { Ref } from 'vue'
import { BASE_API_URL } from '@/api';

interface Employee {
  id: number;
  employee_id: string;
  name: string;
  phone?: string;
  address?: string;
  email?: string;
  gender?: string; // Added gender
  age?: number;    // Added age
}

const employees: Ref<Employee[]> = ref([]);
const newEmployee = reactive({
  employee_id: '',
  name: '',
  phone: '',
  address: '',
  email: '',
  gender: '', // Added gender
  age: ''     // Added age as string for input
});

const fetchEmployees = async () => {
  try {
    const response = await fetch(`${BASE_API_URL}/api/employees/`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    employees.value = await response.json();
  } catch (error) {
    console.error("Error fetching employees:", error);
  }
};

const addEmployee = async () => {
  if (!newEmployee.employee_id || !newEmployee.name) {
    alert('員工代號和姓名為必填欄位！');
    return;
  }

  // Prepare data: convert empty strings to null for optional fields
  const dataToSend = {
    employee_id: newEmployee.employee_id,
    name: newEmployee.name,
    phone: newEmployee.phone === '' ? null : newEmployee.phone,
    address: newEmployee.address === '' ? null : newEmployee.address,
    email: newEmployee.email === '' ? null : newEmployee.email,
    gender: newEmployee.gender === '' ? null : newEmployee.gender, // Added gender
    age: newEmployee.age === '' ? null : Number(newEmployee.age), // Added age, convert to number or null
  };

  try {
    const response = await fetch(`${BASE_API_URL}/api/employees/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(dataToSend),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    // Clear form and refetch employees
    newEmployee.employee_id = '';
    newEmployee.name = '';
    newEmployee.phone = '';
    newEmployee.address = '';
    newEmployee.email = '';
    newEmployee.gender = ''; // Clear gender
    newEmployee.age = '';    // Clear age
    fetchEmployees();
  } catch (error: any) {
    alert(`新增員工失敗: ${error.message}`);
    console.error("Error adding employee:", error);
  }
};

const deleteEmployee = async (employeeId: string) => {
  if (!confirm(`確定要刪除員工代號為 ${employeeId} 的資料嗎？`)) {
    return;
  }

  try {
    const response = await fetch(`${BASE_API_URL}/api/employees/${employeeId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    // Refetch employees or remove from local array
    fetchEmployees();
  } catch (error: any) {
    alert(`刪除員工失敗: ${error.message}`);
    console.error("Error deleting employee:", error);
  }
};

onMounted(fetchEmployees);
</script>

<template>
  <div class="employee-management">
    <h1>員工資料管理</h1>

    <div class="add-employee-form">
      <h2>新增員工</h2>
      <form @submit.prevent="addEmployee">
        <div class="form-group">
          <label for="employee_id">員工代號: *</label>
          <input type="text" id="employee_id" v-model="newEmployee.employee_id" required />
        </div>
        <div class="form-group">
          <label for="name">姓名: *</label>
          <input type="text" id="name" v-model="newEmployee.name" required />
        </div>
        <div class="form-group">
          <label for="phone">電話:</label>
          <input type="text" id="phone" v-model="newEmployee.phone" />
        </div>
        <div class="form-group">
          <label for="address">地址:</label>
          <input type="text" id="address" v-model="newEmployee.address" />
        </div>
        <div class="form-group">
          <label for="email">電子郵件:</label>
          <input type="email" id="email" v-model="newEmployee.email" />
        </div>
        <div class="form-group">
          <label for="gender">性別:</label>
          <input type="text" id="gender" v-model="newEmployee.gender" />
        </div>
        <div class="form-group">
          <label for="age">年齡:</label>
          <input type="number" id="age" v-model="newEmployee.age" />
        </div>
        <button type="submit">新增員工</button>
      </form>
    </div>

    <div class="employee-list">
      <h2>現有員工</h2>
      <p v-if="employees.length === 0">目前沒有員工資料。</p>
      <table v-else>
        <thead>
          <tr>
            <th>ID</th>
            <th>員工代號</th>
            <th>姓名</th>
            <th>電話</th>
            <th>地址</th>
            <th>電子郵件</th>
            <th>性別</th>
            <th>年齡</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="employee in employees" :key="employee.id">
            <td>{{ employee.id }}</td>
            <td>{{ employee.employee_id }}</td>
            <td>{{ employee.name }}</td>
            <td>{{ employee.phone || '無' }}</td>
            <td>{{ employee.address || '無' }}</td>
            <td>{{ employee.email || '無' }}</td>
            <td>{{ employee.gender || '無' }}</td>
            <td>{{ employee.age || '無' }}</td>
            <td>
              <button @click="deleteEmployee(employee.employee_id)" class="delete-button">刪除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.employee-management {
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

.add-employee-form, .employee-list {
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

.form-group input[type="text"],
.form-group input[type="email"] {
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
