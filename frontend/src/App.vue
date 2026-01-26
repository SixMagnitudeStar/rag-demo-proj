<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="app-container">
    <header class="app-header">
      <RouterLink to="/" class="home-link">
        <i class="home-icon"></i>
        <span class="home-text">Home</span>
      </RouterLink>
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
  justify-content: flex-start; /* Align to the left */
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
  width: 24px; /* Icon size */
  height: 24px;
  margin-right: 8px;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="%23ecf0f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-home"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>');
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
  transition: background-image 0.3s ease;
}

.home-link:hover .home-icon {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="%2342b983" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-home"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>');
}

.home-text {
  display: none; /* Hide text on small screens */
}

@media (min-width: 768px) {
  .home-text {
    display: inline; /* Show text on larger screens */
  }
}
</style>
