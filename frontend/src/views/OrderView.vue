<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import type { Ref } from 'vue'
import { BASE_API_URL } from '@/api';

interface Order {
  id: number;
  order_id: string;
  order_date: string;
  order_amount?: number;
}

const orders: Ref<Order[]> = ref([]);
const newOrder = reactive({
  order_id: '',
  order_date: '',
  order_amount: '' // Added order_amount
});

const fetchOrders = async () => {
  try {
    const response = await fetch(`${BASE_API_URL}/api/orders/`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    orders.value = await response.json();
  } catch (error) {
    console.error("Error fetching orders:", error);
  }
};

const addOrder = async () => {
  if (!newOrder.order_id || !newOrder.order_date) {
    alert('訂單單號和訂單日期為必填欄位！');
    return;
  }

  // Prepare data: convert empty strings to null for optional fields
  const dataToSend = {
    order_id: newOrder.order_id,
    order_date: newOrder.order_date,
    order_amount: newOrder.order_amount === '' ? null : Number(newOrder.order_amount), // Added order_amount
  };

  try {
    const response = await fetch(`${BASE_API_URL}/api/orders/`, {
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

    // Clear form and refetch orders
    newOrder.order_id = '';
    newOrder.order_date = '';
    newOrder.order_amount = ''; // Clear order_amount
    fetchOrders();
  } catch (error: any) {
    alert(`新增訂單失敗: ${error.message}`);
    console.error("Error adding order:", error);
  }
};

const deleteOrder = async (orderId: string) => {
  if (!confirm(`確定要刪除訂單單號為 ${orderId} 的資料嗎？`)) {
    return;
  }

  try {
    const response = await fetch(`${BASE_API_URL}/api/orders/${orderId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    // Refetch orders or remove from local array
    fetchOrders();
  } catch (error: any) {
    alert(`刪除訂單失敗: ${error.message}`);
    console.error("Error deleting order:", error);
  }
};

onMounted(fetchOrders);
</script>

<template>
  <div class="order-management">
    <h1>訂單管理</h1>

    <div class="add-order-form">
      <h2>新增訂單</h2>
      <form @submit.prevent="addOrder">
        <div class="form-group">
          <label for="order_id">訂單單號: *</label>
          <input type="text" id="order_id" v-model="newOrder.order_id" required />
        </div>
        <div class="form-group">
          <label for="order_date">訂單日期: *</label>
          <input type="date" id="order_date" v-model="newOrder.order_date" required />
        </div>
        <div class="form-group">
          <label for="order_amount">訂單金額:</label>
          <input type="number" id="order_amount" v-model="newOrder.order_amount" />
        </div>
        <button type="submit">新增訂單</button>
      </form>
    </div>

    <div class="order-list">
      <h2>現有訂單</h2>
      <p v-if="orders.length === 0">目前沒有訂單資料。</p>
      <table v-else>
        <thead>
          <tr>
            <th>ID</th>
            <th>訂單單號</th>
            <th>訂單日期</th>
            <th>訂單金額</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in orders" :key="order.id">
            <td>{{ order.id }}</td>
            <td>{{ order.order_id }}</td>
            <td>{{ order.order_date }}</td>
            <td>{{ order.order_amount || '無' }}</td>
            <td>
              <button @click="deleteOrder(order.order_id)" class="delete-button">刪除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.order-management {
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

.add-order-form, .order-list {
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
.form-group input[type="date"] {
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