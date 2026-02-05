<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="app-container">
    <header class="app-header">
      <RouterLink to="/" class="home-link">
        <i>Home</i> <!-- Simplified to text -->
        <span class="home-text"></span>
      </RouterLink>
      <!-- Navigation links for demo -->
      <nav class="main-nav">
        <RouterLink to="/employees" class="nav-link">員工</RouterLink>
        <RouterLink to="/orders" class="nav-link">訂單</RouterLink>
        <RouterLink to="/system_info" class="nav-link">系統資訊</RouterLink>
      </nav>
    </header>

    <RouterView />
  </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  width: 100%;
  padding: 1rem 2rem;
  background-color: #2c3e50; /* Darker background for header */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between; /* Align to the left */
  gap: 1rem;
}

.home-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: #ecf0f1; /* Light text color */
  font-weight: bold;
  font-size: 1.2em;
  transition: color 0.3s ease;
}

.home-link:hover {
  color: #42b983; /* Vue green on hover */
}

.home-icon {
  margin-right: 8px;
}

.home-text {
  display: none; /* Hide text on small screens */
}

@media (min-width: 768px) {
  .home-text {
    display: inline; /* Show text on larger screens */
  }
}

.main-nav {
  display: flex;
  gap: 1rem;
}

.nav-link {
  color: #ecf0f1;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.nav-link:hover {
  background-color: #42b983;
  color: #fff;
}
</style>