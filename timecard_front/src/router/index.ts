import { createRouter, createWebHistory } from 'vue-router'

import HomeView from './HomeView.vue'
import AboutView from './AboutView.vue'
import RegisterView from './RegisterView.vue'
import LoginView from './LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: HomeView},
    { path: '/about', component: AboutView},
    { path: '/register', component: RegisterView},
    { path: '/login', component: LoginView},
  ],
})

export default router
