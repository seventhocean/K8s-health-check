<template>
  <el-container class="app-layout">
    <!-- 左侧导航 -->
    <el-aside :width="sidebarCollapse ? '64px' : '240px'" class="sidebar">
      <div class="logo">
        <el-icon class="logo-icon"><Platform /></el-icon>
        <span v-show="!sidebarCollapse" class="logo-text">K8s 集群监控</span>
      </div>

      <el-menu
        :default-active="activeMenu"
        :collapse="sidebarCollapse"
        :collapse-transition="false"
        router
        background-color="transparent"
        text-color="#a0aec0"
        active-text-color="#fff"
        class="sidebar-menu"
      >
        <el-sub-menu index="cluster">
          <template #title>
            <el-icon><DataBoard /></el-icon>
            <span>集群概览</span>
          </template>
          <el-menu-item index="/">Dashboard</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="compute">
          <template #title>
            <el-icon><Cpu /></el-icon>
            <span>计算资源</span>
          </template>
          <el-menu-item index="/nodes">节点管理</el-menu-item>
          <el-menu-item index="/pods">Pod 管理</el-menu-item>
          <el-menu-item index="/deployments">工作负载</el-menu-item>
          <el-menu-item index="/replicasets">ReplicaSet</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="network">
          <template #title>
            <el-icon><Connection /></el-icon>
            <span>网络资源</span>
          </template>
          <el-menu-item index="/services">Service</el-menu-item>
          <el-menu-item index="/ingress">Ingress</el-menu-item>
          <el-menu-item index="/networkpolicies">NetworkPolicy</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="storage">
          <template #title>
            <el-icon><Folder /></el-icon>
            <span>存储资源</span>
          </template>
          <el-menu-item index="/pvs">PersistentVolume</el-menu-item>
          <el-menu-item index="/pvcs">PersistentVolumeClaim</el-menu-item>
          <el-menu-item index="/storageclasses">StorageClass</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="namespace">
          <template #title>
            <el-icon><Grid /></el-icon>
            <span>命名空间</span>
          </template>
          <el-menu-item index="/namespaces">命名空间管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="system">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/users">用户管理</el-menu-item>
          <el-menu-item index="/audit">操作审计</el-menu-item>
          <el-menu-item index="/settings">系统设置</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-container class="main-container">
      <!-- 顶部栏 -->
      <el-header class="header">
        <div class="header-content">
          <div class="header-left">
            <el-button class="collapse-btn" @click="toggleSidebar">
              <el-icon><Expand v-if="sidebarCollapse" /><Fold v-else /></el-icon>
            </el-button>
            <breadcrumb />
          </div>

          <div class="header-right">
            <!-- 集群选择器 -->
            <el-select v-model="currentCluster" placeholder="选择集群" size="default" class="cluster-select">
              <el-option label="production-cluster" value="prod" />
              <el-option label="staging-cluster" value="staging" />
              <el-option label="dev-cluster" value="dev" />
            </el-select>

            <!-- 通知 -->
            <el-badge :value="3" :max="99" class="notification-btn">
              <el-button class="icon-btn" @click="showNotifications">
                <el-icon><Bell /></el-icon>
              </el-button>
            </el-badge>

            <!-- 用户菜单 -->
            <el-dropdown class="user-menu" @command="handleUserCommand">
              <div class="user-info">
                <el-avatar :size="36" :src="user.avatar">
                  {{ user.name.charAt(0) }}
                </el-avatar>
                <span class="user-name">{{ user.name }}</span>
                <el-icon><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>
                    个人中心
                  </el-dropdown-item>
                  <el-dropdown-item command="settings">
                    <el-icon><Setting /></el-icon>
                    个人设置
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>

    <!-- 通知弹窗 -->
    <el-dialog v-model="notificationVisible" title="通知" width="400px" class="notification-dialog">
      <el-tabs>
        <el-tab-pane label="告警 (3)">
          <div class="notification-item warning">
            <el-icon><Warning /></el-icon>
            <div class="notification-content">
              <div class="notification-title">节点 node-1 CPU 使用率超过 90%</div>
              <div class="notification-time">5 分钟前</div>
            </div>
          </div>
          <div class="notification-item warning">
            <el-icon><Warning /></el-icon>
            <div class="notification-content">
              <div class="notification-title">Pod nginx-deployment-xxx 重启次数过多</div>
              <div class="notification-time">10 分钟前</div>
            </div>
          </div>
          <div class="notification-item danger">
            <el-icon><CircleClose /></el-icon>
            <div class="notification-content">
              <div class="notification-title">节点 node-3 磁盘空间不足</div>
              <div class="notification-time">30 分钟前</div>
            </div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="消息 (0)">
          <div class="empty-message">暂无新消息</div>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authApi } from '@/api/auth'
import {
  Platform,
  DataBoard,
  Cpu,
  Connection,
  Folder,
  Grid,
  Setting,
  Expand,
  Fold,
  Bell,
  ArrowDown,
  User,
  SwitchButton,
  Warning,
  CircleClose,
} from '@element-plus/icons-vue'
import Breadcrumb from '../components/Breadcrumb.vue'

const router = useRouter()
const route = useRoute()
const activeMenu = computed(() => route.path)
const sidebarCollapse = ref(false)
const currentCluster = ref('prod')
const notificationVisible = ref(false)

const user = ref({
  name: 'Admin',
  email: 'admin@example.com',
  avatar: '',
})

function toggleSidebar() {
  sidebarCollapse.value = !sidebarCollapse.value
}

function showNotifications() {
  notificationVisible.value = true
}

async function handleUserCommand(command: string) {
  if (command === 'logout') {
    try {
      await authApi.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      ElMessage.success('已退出登录')
      router.push('/login')
    }
  } else if (command === 'profile') {
    ElMessage.info('个人中心功能开发中')
  } else if (command === 'settings') {
    router.push('/settings')
  }
}

onMounted(async () => {
  // 加载用户信息
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      const userData = JSON.parse(userStr)
      user.value = {
        name: userData.username || userData.name,
        email: userData.email,
        avatar: '',
      }
    } catch (e) {
      console.error('Failed to parse user data:', e)
    }
  }

  // 检查登录状态
  const token = localStorage.getItem('token')
  if (!token) {
    router.push('/login')
  }
})
</script>

<style scoped lang="scss">
.app-layout {
  height: 100vh;
}

// 侧边栏
.sidebar {
  background: linear-gradient(180deg, #1a1f3a 0%, #0d1121 100%);
  transition: width 0.3s ease;
  overflow-x: hidden;

  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);

    .logo-icon {
      font-size: 28px;
      color: #409EFF;
    }

    .logo-text {
      color: #fff;
      font-size: 16px;
      font-weight: 600;
      white-space: nowrap;
    }
  }

  .sidebar-menu {
    border-right: none;
    padding-top: 8px;

    :deep(.el-sub-menu__title) {
      color: #a0aec0;
      transition: all 0.2s;

      &:hover {
        background: rgba(255, 255, 255, 0.05);
        color: #fff;
      }

      .el-icon {
        margin-right: 8px;
      }
    }

    .el-menu-item {
      &.is-active {
        background: rgba(64, 158, 255, 0.2) !important;
        color: #fff !important;
      }

      &:hover {
        background: rgba(255, 255, 255, 0.05);
      }
    }
  }
}

// 主内容区
.main-container {
  background: #f5f7fa;
}

// 顶部栏
.header {
  background: #fff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  padding: 0 20px;

  .header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 100%;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;

    .collapse-btn {
      border: none;
      background: transparent;

      &:hover {
        background: #f5f5f5;
      }
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 16px;

    .cluster-select {
      width: 160px;
    }

    .icon-btn {
      border: none;
      background: transparent;
      position: relative;

      &:hover {
        background: #f5f5f5;
      }
    }

    .notification-btn {
      cursor: pointer;
    }

    .user-menu {
      cursor: pointer;

      .user-info {
        display: flex;
        align-items: center;
        gap: 8px;

        .user-name {
          color: #333;
          font-size: 14px;
        }
      }
    }
  }
}

// 内容区
.main-content {
  padding: 0;
  overflow-y: auto;
}

// 通知弹窗
.notification-dialog {
  .notification-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 8px;

    &.warning {
      background: #fdf6ec;

      .el-icon {
        color: #e6a23c;
      }
    }

    &.danger {
      background: #fef0f0;

      .el-icon {
        color: #f56c6c;
      }
    }

    .notification-content {
      flex: 1;

      .notification-title {
        font-size: 14px;
        color: #333;
      }

      .notification-time {
        font-size: 12px;
        color: #999;
        margin-top: 4px;
      }
    }
  }

  .empty-message {
    text-align: center;
    padding: 40px;
    color: #999;
  }
}
</style>
