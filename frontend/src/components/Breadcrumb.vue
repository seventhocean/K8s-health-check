<template>
  <el-breadcrumb separator="/">
    <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
    <el-breadcrumb-item v-for="(item, index) in breadcrumbs" :key="index">
      <span v-if="item.path">{{ item.name }}</span>
      <span v-else>{{ item.name }}</span>
    </el-breadcrumb-item>
  </el-breadcrumb>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const breadcrumbs = computed(() => {
  const parts = route.path.split('/').filter(Boolean)
  return parts.map((part, index) => ({
    name: part.charAt(0).toUpperCase() + part.slice(1),
    path: index < parts.length - 1 ? '/' + parts.slice(0, index + 1).join('/') : null,
  }))
})
</script>

<style scoped>
.el-breadcrumb {
  padding: 10px 0;
}
</style>
