<template>
  <el-breadcrumb separator="/">
    <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
    <el-breadcrumb-item v-for="(item, index) in breadcrumbs" :key="index" :to="item.path">
      {{ item.name }}
    </el-breadcrumb-item>
  </el-breadcrumb>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const breadcrumbs = computed(() => {
  const path = route.path
  if (path === '/') {
    return []
  }

  const parts = path.split('/').filter(Boolean)
  const names: Record<string, string> = {
    'nodes': '节点管理',
    'pods': 'Pod 管理',
    'deployments': '工作负载',
    'replicasets': 'ReplicaSet',
    'services': 'Service',
    'ingress': 'Ingress',
    'networkpolicies': 'NetworkPolicy',
    'pvs': 'PersistentVolume',
    'pvcs': 'PersistentVolumeClaim',
    'storageclasses': 'StorageClass',
    'namespaces': '命名空间管理',
    'users': '用户管理',
    'audit': '操作审计',
    'settings': '系统设置',
  }

  return parts.map((part, index) => {
    const fullPath = '/' + parts.slice(0, index + 1).join('/')
    return {
      name: names[part] || part.charAt(0).toUpperCase() + part.slice(1),
      path: index < parts.length - 1 ? fullPath : undefined,
    }
  })
})
</script>

<style scoped>
.el-breadcrumb {
  padding: 0;
}
</style>
