<template>
  <div class="audit-page">
    <div class="page-header">
      <h1 class="page-title">操作审计</h1>
      <div class="header-actions">
        <el-button @click="handleRefresh"><el-icon><Refresh /></el-icon> 刷新</el-button>
        <el-button @click="handleExport"><el-icon><Download /></el-icon> 导出</el-button>
      </div>
    </div>

    <el-card v-loading="loading">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-input v-model="filters.keyword" placeholder="搜索操作内容" style="width: 240px" clearable>
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-select v-model="filters.user" placeholder="操作人" clearable style="width: 140px">
            <el-option v-for="user in users" :key="user" :label="user" :value="user" />
          </el-select>
          <el-select v-model="filters.action" placeholder="操作类型" clearable style="width: 140px">
            <el-option label="创建" value="create" />
            <el-option label="更新" value="update" />
            <el-option label="删除" value="delete" />
          </el-select>
          <el-date-picker v-model="filters.dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" style="width: 240px" />
        </div>
      </div>

      <el-table :data="auditLogs" stripe>
        <el-table-column prop="timestamp" label="时间" width="160" sortable />
        <el-table-column prop="user" label="操作人" width="120" />
        <el-table-column label="操作类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getActionType(row.action)">{{ row.actionName }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resource" label="资源类型" width="120" />
        <el-table-column prop="resourceName" label="资源名称" min-width="180" />
        <el-table-column prop="namespace" label="命名空间" width="120" />
        <el-table-column label="操作详情" min-width="250" show-overflow-tooltip>
          <template #default="{ row }">{{ row.details }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'">{{ row.status === 'success' ? '成功' : '失败' }}</el-tag>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.pageSize"
          :page-sizes="[20, 50, 100]" :total="pagination.total" layout="total, sizes, prev, pager, next, jumper" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Refresh, Search, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const users = ref(['admin', 'developer', 'viewer'])
const auditLogs = ref<any[]>([])
const filters = ref({ keyword: '', user: '', action: '', dateRange: [] })
const pagination = ref({ page: 1, pageSize: 20, total: 100 })

async function fetchData() {
  loading.value = true
  try {
    auditLogs.value = [
      { timestamp: '2024-01-15 10:30:00', user: 'admin', action: 'create', actionName: '创建', resource: 'Deployment', resourceName: 'nginx-deployment', namespace: 'default', status: 'success', details: '创建 Deployment nginx-deployment' },
      { timestamp: '2024-01-15 10:25:00', user: 'admin', action: 'update', actionName: '更新', resource: 'Service', resourceName: 'nginx-service', namespace: 'default', status: 'success', details: '更新 Service 端口配置' },
      { timestamp: '2024-01-15 09:00:00', user: 'developer', action: 'delete', actionName: '删除', resource: 'Pod', resourceName: 'test-pod', namespace: 'default', status: 'success', details: '删除测试 Pod' },
    ]
  } finally {
    loading.value = false
  }
}

function getActionType(action: string): 'success' | 'warning' | 'danger' {
  const types: Record<string, any> = { create: 'success', update: 'warning', delete: 'danger' }
  return types[action] || 'info'
}

function handleRefresh() { fetchData(); ElMessage.success('刷新成功') }
function handleExport() { ElMessage.success('导出审计日志功能开发中') }

onMounted(() => { fetchData() })
</script>

<style scoped lang="scss">
.audit-page { padding: 20px;
  .page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;
    .page-title { font-size: 24px; font-weight: 600; color: #1a1f3a; margin: 0; }
    .header-actions { display: flex; gap: 12px; }
  }
  .toolbar { display: flex; margin-bottom: 16px;
    .toolbar-left { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
  }
  .pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }
}
</style>
