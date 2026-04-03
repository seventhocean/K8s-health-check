import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Nodes from '../views/Nodes.vue'
import Pods from '../views/Pods.vue'
import Deployments from '../views/Deployments.vue'
import Settings from '../views/Settings.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Dashboard',
      component: Dashboard,
    },
    {
      path: '/nodes',
      name: 'Nodes',
      component: Nodes,
    },
    {
      path: '/pods',
      name: 'Pods',
      component: Pods,
    },
    {
      path: '/deployments',
      name: 'Deployments',
      component: Deployments,
    },
    {
      path: '/settings',
      name: 'Settings',
      component: Settings,
    },
  ],
})

export default router
