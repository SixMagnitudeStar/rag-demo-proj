<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <main class="home-page">
    <h1 class="welcome-heading">歡迎來到管理系統</h1>
    <nav class="main-menu">
      <RouterLink to="/employees" class="menu-item">
        <i class="icon employee-icon"></i>
        <span>員工管理</span>
      </RouterLink>
      <RouterLink to="/orders" class="menu-item">
        <i class="icon order-icon"></i>
        <span>訂單管理</span>
      </RouterLink>
      <RouterLink to="/system_info" class="menu-item">
        <i class="icon info-icon"></i>
        <span>系統資訊檢索</span>
      </RouterLink>
      <RouterLink to="/qna" class="menu-item">
        <i class="icon qna-icon"></i>
        <span>系統問答</span>
      </RouterLink>

    </nav>
  </main>
</template>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 80vh;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f0f2f5;
  color: #333;
}

.welcome-heading {
  font-size: 3em;
  color: #2c3e50;
  margin-bottom: 40px;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
}

.main-menu {
  display: flex;
  gap: 30px;
}

.menu-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 180px;
  height: 180px;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  text-decoration: none;
  color: #34495e;
  font-size: 1.3em;
  font-weight: bold;
  transition: all 0.3s ease;
  padding: 15px;
  text-align: center;
}

.menu-item:hover {
  background-color: #e8f5e9; /* Light green hover */
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
  color: #42b983;
}

.icon {
  width: 60px;
  height: 60px;
  margin-bottom: 10px;
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
}

.employee-icon {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="%2342b983" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-users"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>');
}

.order-icon {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="%2342b983" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-clipboard"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>');
}

.info-icon {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="%2342b983" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-info"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>');
}

.qna-icon {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="%2342b983" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-help-circle"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>');
}

span {
  margin-top: 5px;
}
</style>
