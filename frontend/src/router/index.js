// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Controle from '../views/Controle.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'  // Corrigido aqui também
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/controle',
    name: 'Controle',
    component: Controle,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('usuario')
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router
