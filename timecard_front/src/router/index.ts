import { createRouter, createWebHistory } from 'vue-router'

import HomeView from './HomeView.vue';
import AboutView from './AboutView.vue';
import RegisterView from './RegisterView.vue';
import LoginView from './LoginView.vue';
import ReportView from './ReportView.vue';
import RecordAttributeView from './RecordAttributeView.vue';
import RecordView from './RecordView.vue';
import RecordEditView from './RecordEditView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: HomeView},
    { path: '/about', component: AboutView},
    { path: '/register', component: RegisterView},
    { path: '/login', component: LoginView},
    { path: '/report', component: ReportView},
    { path: '/info/:id', component: RecordAttributeView},
    { path: '/record/:id', component: RecordView},
    { path: '/record/edit/:id', component: RecordEditView},
  ],
})

export default router
