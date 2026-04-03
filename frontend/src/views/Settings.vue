<template>
  <div class="settings-page">
    <h1 class="page-title">设置</h1>

    <el-card>
      <el-form :model="settings" label-width="150px">
        <el-form-item label="刷新间隔">
          <el-select v-model="settings.refreshInterval">
            <el-option label="15 秒" :value="15" />
            <el-option label="30 秒" :value="30" />
            <el-option label="1 分钟" :value="60" />
            <el-option label="5 分钟" :value="300" />
          </el-select>
        </el-form-item>

        <el-form-item label="主题">
          <el-radio-group v-model="settings.theme">
            <el-radio label="light">浅色</el-radio>
            <el-radio label="dark">深色</el-radio>
            <el-radio label="auto">自动</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="WebSocket">
          <el-switch v-model="settings.enableWebSocket" />
          <span class="sub-text" style="margin-left: 10px">启用实时数据推送</span>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="saveSettings">保存设置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card style="margin-top: 20px">
      <template #header>
        <span>系统信息</span>
      </template>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="应用名称">K8s Health Check</el-descriptions-item>
        <el-descriptions-item label="版本">v0.1.0</el-descriptions-item>
        <el-descriptions-item label="后端框架">FastAPI + Python</el-descriptions-item>
        <el-descriptions-item label="前端框架">Vue 3 + TypeScript</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const settings = ref({
  refreshInterval: 15,
  theme: 'light',
  enableWebSocket: true,
})

function saveSettings() {
  localStorage.setItem('k8s-monitor-settings', JSON.stringify(settings.value))
  ElMessage.success('设置已保存')
}

onMounted(() => {
  const saved = localStorage.getItem('k8s-monitor-settings')
  if (saved) {
    settings.value = JSON.parse(saved)
  }
})
</script>

<style scoped>
.settings-page {
  padding: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #333;
}

.sub-text {
  font-size: 12px;
  color: #999;
}
</style>
