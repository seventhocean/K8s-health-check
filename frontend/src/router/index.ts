import { createRouter, createWebHistory } from 'vue-router'

// 布局组件
import MainLayout from '@/views/MainLayout.vue'
import Login from '@/views/Login.vue'

// 页面组件
import Dashboard from '@/views/Dashboard.vue'
import Nodes from '@/views/Nodes.vue'
import Pods from '@/views/Pods.vue'
import Deployments from '@/views/Deployments.vue'
import Settings from '@/views/Settings.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: Dashboard,
        meta: { title: 'Dashboard', icon: 'DataBoard' },
      },
      {
        path: 'nodes',
        name: 'Nodes',
        component: Nodes,
        meta: { title: '节点管理', icon: 'Cpu' },
      },
      {
        path: 'pods',
        name: 'Pods',
        component: Pods,
        meta: { title: 'Pod 管理', icon: 'Box' },
      },
      {
        path: 'deployments',
        name: 'Deployments',
        component: Deployments,
        meta: { title: '工作负载', icon: 'SetUp' },
      },
      {
        path: 'replicasets',
        name: 'ReplicaSets',
        component: () => import('@/views/ReplicaSets.vue'),
        meta: { title: 'ReplicaSet', icon: 'CopyDocument' },
      },
      {
        path: 'services',
        name: 'Services',
        component: () => import('@/views/Services.vue'),
        meta: { title: 'Service', icon: 'Connection' },
      },
      {
        path: 'ingress',
        name: 'Ingress',
        component: () => import('@/views/Ingress.vue'),
        meta: { title: 'Ingress', icon: 'Link' },
      },
      {
        path: 'networkpolicies',
        name: 'NetworkPolicies',
        component: () => import('@/views/NetworkPolicies.vue'),
        meta: { title: 'NetworkPolicy', icon: 'Shield' },
      },
      {
        path: 'pvs',
        name: 'PersistentVolumes',
        component: () => import('@/views/PersistentVolumes.vue'),
        meta: { title: 'PersistentVolume', icon: 'Folder' },
      },
      {
        path: 'pvcs',
        name: 'PersistentVolumeClaims',
        component: () => import('@/views/PersistentVolumeClaims.vue'),
        meta: { title: 'PersistentVolumeClaim', icon: 'FolderOpened' },
      },
      {
        path: 'storageclasses',
        name: 'StorageClasses',
        component: () => import('@/views/StorageClasses.vue'),
        meta: { title: 'StorageClass', icon: 'Files' },
      },
      {
        path: 'namespaces',
        name: 'Namespaces',
        component: () => import('@/views/Namespaces.vue'),
        meta: { title: '命名空间管理', icon: 'Grid' },
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/Users.vue'),
        meta: { title: '用户管理', icon: 'User' },
      },
      {
        path: 'audit',
        name: 'Audit',
        component: () => import('@/views/Audit.vue'),
        meta: { title: '操作审计', icon: 'Document' },
      },
      {
        path: 'settings',
        name: 'Settings',
        component: Settings,
        meta: { title: '系统设置', icon: 'Setting' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')

  if (to.path === '/login') {
    if (token) {
      next('/')
    } else {
      next()
    }
  } else {
    if (!token) {
      next('/login')
    } else {
      next()
    }
  }
})

export default router
