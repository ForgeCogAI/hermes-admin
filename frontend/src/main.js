import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './style.css'

import DashboardView from './views/DashboardView.vue'
import TemplateView from './views/TemplateView.vue'
import UserConfigView from './views/UserConfigView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: DashboardView },
    { path: '/template', component: TemplateView },
    { path: '/users/:id/config', component: UserConfigView },
  ],
})

createApp(App).use(router).mount('#app')
