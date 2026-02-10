<script setup lang="ts">
import { RouterLink } from 'vue-router'
import QnAChatWidget from '../components/QnAChatWidget.vue'; // Import the QnA component
// Removed isQnAChatOpen, toggleQnAChat, fabRef, onMounted as FAB is removed
</script>

<template>
  <main class="home-page">
    <div class="home-content-wrapper">
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
      </nav>

      <!-- QnA Chat Widget - always visible now, fixed position -->
      <div class="qna-chat-wrapper">
        <QnAChatWidget />
      </div>
    </div>
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

.home-content-wrapper {
  display: flex;
  align-items: flex-start; /* Align items at the top of the cross axis */
  gap: 30px; /* Space between menu and chat widget */
  max-width: 1200px; /* Constrain width for centering */
  margin: 0 auto; /* Center the wrapper */
  position: relative; /* Ensure fixed positioning of QnA wrapper refers to viewport */
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


span {
  margin-top: 5px;
}

/* QnA Chat Widget Wrapper - Fixed Position */
.qna-chat-wrapper {
  position: fixed; /* Fixed to viewport */
  bottom: 2rem;
  right: 2rem;
  width: 350px; /* Fixed width for the chat window */
  height: 500px; /* Fixed height for the chat window */
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 999;
  display: flex;
  flex-direction: column;
}

@media (max-width: 768px) {
  .qna-chat-wrapper {
    bottom: 1rem;
    right: 1rem;
    width: calc(100% - 2rem); /* Adjust width for small screens */
    height: 400px;
  }
}

</style>