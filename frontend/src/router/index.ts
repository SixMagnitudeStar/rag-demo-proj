import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },

    {
      path: '/employees',
      name: 'employees',
      component: () => import('../views/EmployeeView.vue')
    },
    {
      path: '/orders',
      name: 'orders',
      component: () => import('../views/OrderView.vue')
    },
    {
      path: '/system_info',
      name: 'system_info',
      component: () => import('../views/SystemInfoView.vue')
    },
    {
      path: '/qna',
      name: 'qna',
      component: () => import('../views/SystemQnAView.vue')
    }
  ]
})

export default router
