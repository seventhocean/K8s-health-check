<template>
  <el-container class="layout-container">
    <el-aside width="200px">
      <div class="logo">
        <h2>K8s Monitor</h2>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/">
          <el-icon><DataBoard /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/nodes">
          <el-icon><Cpu /></el-icon>
          <span>节点</span>
        </el-menu-item>
        <el-menu-item index="/pods">
          <el-icon><Box /></el-icon>
          <span>Pods</span>
        </el-menu-item>
        <el-menu-item index="/deployments">
          <el-icon><SetUp /></el-icon>
          <span>Deployments</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header>
        <div class="header-content">
          <breadcrumb />
          <div class="header-right">
            <el-tag v-if="connected" type="success" size="small">
              <el-icon><Connection /></el-icon>
              已连接
            </el-tag>
            <el-tag v-else type="danger" size="small">
              未连接
            </el-tag>
          </div>
        </div>
      </el-header>

      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  DataBoard,
  Cpu,
  Box,
  SetUp,
  Setting,
  Connection,
} from '@element-plus/icons-vue'
import Breadcrumb from '../components/Breadcrumb.vue'

const route = useRoute()
const activeMenu = computed(() => route.path)
const connected = ref(true)

// WebSocket 连接
let ws: WebSocket | null = null

function connectWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  ws = new WebSocket(`${protocol}//${window.location.host}/ws/metrics`)

  ws.onopen = () => {
    connected.value = true
    console.log('WebSocket connected')
  }

  ws.onclose = () => {
    connected.value = false
    console.log('WebSocket disconnected, reconnecting...')
    setTimeout(connectWebSocket, 5000)
  }

  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
  }

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      console.log('Received metrics:', data)
      // 可以在这里更新 store
    } catch (e) {
      console.error('Failed to parse WebSocket message:', e)
    }
  }
}

onMounted(() => {
  connectWebSocket()
})

onUnmounted(() => {
  if (ws) {
    ws.close()
  }
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.el-aside {
  background-color: #304156;
  color: #fff;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo h2 {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
}

.el-menu {
  border-right: none;
}

.el-header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  padding: 0 20px;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>
