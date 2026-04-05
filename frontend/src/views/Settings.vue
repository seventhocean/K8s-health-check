<template>
  <div class="settings-page">
    <div class="page-header">
      <h1 class="page-title">系统设置</h1>
    </div>

    <el-row :gutter="20">
      <el-col :span="16">
        <!-- 通用设置 -->
        <el-card>
          <template #header>
            <span><el-icon><Setting /></el-icon> 通用设置</span>
          </template>
          <el-form :model="settings" label-width="140px" label-position="left">
            <el-form-item label="数据刷新间隔">
              <el-select v-model="settings.refreshInterval" style="width: 200px">
                <el-option label="15 秒" :value="15" />
                <el-option label="30 秒" :value="30" />
                <el-option label="1 分钟" :value="60" />
                <el-option label="5 分钟" :value="300" />
              </el-select>
            </el-form-item>

            <el-form-item label="默认集群">
              <el-select v-model="settings.defaultCluster" style="width: 200px">
                <el-option label="production-cluster" value="prod" />
                <el-option label="staging-cluster" value="staging" />
                <el-option label="dev-cluster" value="dev" />
              </el-select>
            </el-form-item>

            <el-form-item label="每页显示数量">
              <el-select v-model="settings.pageSize" style="width: 200px">
                <el-option label="10 条" :value="10" />
                <el-option label="20 条" :value="20" />
                <el-option label="50 条" :value="50" />
                <el-option label="100 条" :value="100" />
              </el-select>
            </el-form-item>

            <el-form-item label="WebSocket">
              <el-switch v-model="settings.enableWebSocket" />
              <span class="sub-text" style="margin-left: 10px">启用实时数据推送</span>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 通知设置 -->
        <el-card style="margin-top: 20px">
          <template #header>
            <span><el-icon><Bell /></el-icon> 通知设置</span>
          </template>
          <el-form :model="settings" label-width="140px" label-position="left">
            <el-form-item label="告警通知">
              <el-switch v-model="settings.enableAlerts" />
            </el-form-item>
            <el-form-item label="邮件通知">
              <el-switch v-model="settings.emailNotify" :disabled="!settings.enableAlerts" />
            </el-form-item>
            <el-form-item label="通知邮箱">
              <el-input v-model="settings.alertEmail" placeholder="接收告警的邮箱地址" style="width: 300px" />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 保存按钮 -->
        <div class="save-actions" style="margin-top: 20px">
          <el-button type="primary" @click="saveSettings">保存设置</el-button>
          <el-button @click="resetSettings">恢复默认</el-button>
        </div>
      </el-col>

      <el-col :span="8">
        <!-- 系统信息 -->
        <el-card>
          <template #header>
            <span><el-icon><Monitor /></el-icon> 系统信息</span>
          </template>
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="应用名称">K8s 集群监控平台</el-descriptions-item>
            <el-descriptions-item label="版本">v1.0.0</el-descriptions-item>
            <el-descriptions-item label="后端框架">FastAPI + Python</el-descriptions-item>
            <el-descriptions-item label="前端框架">Vue 3 + TypeScript</el-descriptions-item>
            <el-descriptions-item label="UI 组件">Element Plus</el-descriptions-item>
            <el-descriptions-item label="图表库">ECharts</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 集群状态 -->
        <el-card style="margin-top: 20px">
          <template #header>
            <span><el-icon><Connection /></el-icon> 集群连接状态</span>
          </template>
          <div class="cluster-status">
            <div class="status-item">
              <span class="status-label">API Server</span>
              <el-tag type="success" size="small">已连接</el-tag>
            </div>
            <div class="status-item">
              <span class="status-label">MySQL</span>
              <el-tag type="success" size="small">正常</el-tag>
            </div>
            <div class="status-item">
              <span class="status-label">Redis</span>
              <el-tag type="success" size="small">正常</el-tag>
            </div>
          </div>
        </el-card>

        <!-- 快捷操作 -->
        <el-card style="margin-top: 20px">
          <template #header>
            <span>快捷操作</span>
          </template>
          <div class="quick-actions">
            <el-button type="danger" plain @click="handleClearCache" style="width: 100%; margin-bottom: 10px">
              <el-icon><Delete /></el-icon>
              清除缓存
            </el-button>
            <el-button type="warning" plain @click="handleExportConfig" style="width: 100%">
              <el-icon><Download /></el-icon>
              导出配置
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Setting, Bell, Monitor, Connection, Delete, Download } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const defaultSettings = {
  refreshInterval: 30,
  theme: 'light',
  enableWebSocket: true,
  defaultCluster: 'prod',
  pageSize: 20,
  enableAlerts: true,
  emailNotify: true,
  alertEmail: 'admin@example.com',
}

const settings = ref({ ...defaultSettings })

function saveSettings() {
  localStorage.setItem('k8s-monitor-settings', JSON.stringify(settings.value))
  ElMessage.success('设置已保存')
}

function resetSettings() {
  ElMessageBox.confirm('确定要恢复默认设置吗？', '提示', { type: 'warning' })
    .then(() => {
      settings.value = { ...defaultSettings }
      ElMessage.success('已恢复默认设置')
    })
}

function handleClearCache() {
  ElMessageBox.confirm('确定要清除缓存吗？', '提示', { type: 'warning' })
    .then(() => {
      localStorage.clear()
      ElMessage.success('缓存已清除')
    })
}

function handleExportConfig() {
  ElMessage.success('导出配置功能开发中')
}

onMounted(() => {
  const saved = localStorage.getItem('k8s-monitor-settings')
  if (saved) {
    settings.value = { ...defaultSettings, ...JSON.parse(saved) }
  }
})
</script>

<style scoped lang="scss">
.settings-page {
  padding: 20px;

  .page-header {
    margin-bottom: 20px;

    .page-title {
      font-size: 24px;
      font-weight: 600;
      color: #1a1f3a;
      margin: 0;
    }
  }
}

.sub-text {
  font-size: 12px;
  color: #999;
}

.cluster-status {
  .status-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid #f0f0f0;

    &:last-child {
      border-bottom: none;
    }

    .status-label {
      font-size: 14px;
      color: #666;
    }
  }
}

.quick-actions {
  display: flex;
  flex-direction: column;
}
</style>
