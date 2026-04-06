<template>
  <div class="namespaces-page">
    <div class="page-header">
      <h1 class="page-title">命名空间管理</h1>
      <div class="header-actions">
        <el-button @click="handleRefresh"><el-icon><Refresh /></el-icon> 刷新</el-button>
        <el-button type="primary" @click="showCreate"><el-icon><Plus /></el-icon> 创建命名空间</el-button>
      </div>
    </div>

    <el-card v-loading="loading">
      <el-table :data="namespaces" stripe>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Active' ? 'success' : 'info'">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" min-width="200">
          <template #default="{ row }">
            <el-link type="primary" @click="viewDetail(row)">{{ row.name }}</el-link>
          </template>
        </el-table-column>
        <el-table-column label="资源配额" min-width="250">
          <template #default="{ row }">
            <div v-if="row.quota">CPU: {{ row.quota.cpu }} | 内存：{{ row.quota.memory }}</div>
            <div v-else class="sub-text">未设置配额</div>
          </template>
        </el-table-column>
        <el-table-column label="资源使用" width="200">
          <template #default="{ row }">
            <div>CPU: {{ row.cpuUsage || 0 }} / {{ row.quota?.cpu || '-' }}</div>
            <div>内存：{{ row.memoryUsage || 0 }} / {{ row.quota?.memory || '-' }}</div>
          </template>
        </el-table-column>
        <el-table-column label="Pod 数量" width="100">
          <template #default="{ row }">{{ row.podCount || 0 }}</template>
        </el-table-column>
        <el-table-column label="创建时间" width="160">
          <template #default="{ row }">{{ row.createdAt }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">详情</el-button>
            <el-button link type="warning" @click="editQuota(row)">配额</el-button>
            <el-button link type="danger" :disabled="row.name === 'default' || row.name === 'kube-system'" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建命名空间对话框 -->
    <el-dialog v-model="createVisible" title="创建命名空间" width="400px">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="名称" required>
          <el-input v-model="createForm.name" placeholder="请输入命名空间名称" />
        </el-form-item>
        <el-form-item label="资源配额">
          <el-checkbox-group v-model="createForm.quotas">
            <el-checkbox label="cpu">CPU</el-checkbox>
            <el-checkbox label="memory">内存</el-checkbox>
            <el-checkbox label="pods">Pod 数量</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Refresh, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const createVisible = ref(false)
const createForm = ref({ name: '', quotas: [] })
const namespaces = ref<any[]>([])

async function fetchData() {
  loading.value = true
  try {
    namespaces.value = [
      { name: 'default', status: 'Active', quota: null, cpuUsage: '500m', memoryUsage: '512Mi', podCount: 12, createdAt: '2024-01-01' },
      { name: 'kube-system', status: 'Active', quota: null, cpuUsage: '1000m', memoryUsage: '1Gi', podCount: 25, createdAt: '2024-01-01' },
      { name: 'monitoring', status: 'Active', quota: { cpu: '4', memory: '8Gi' }, cpuUsage: '2', memoryUsage: '4Gi', podCount: 8, createdAt: '2024-01-02' },
      { name: 'production', status: 'Active', quota: { cpu: '16', memory: '32Gi' }, cpuUsage: '12', memoryUsage: '24Gi', podCount: 45, createdAt: '2024-01-03' },
    ]
  } finally {
    loading.value = false
  }
}

function handleRefresh() { fetchData(); ElMessage.success('刷新成功') }
function viewDetail(row: any) { ElMessage.info(`查看命名空间：${row.name}`) }
function editQuota(row: any) { ElMessage.info(`编辑 ${row.name} 配额`) }
function showCreate() { createVisible.value = true }
function handleCreate() {
  if (!createForm.value.name) { ElMessage.warning('请输入命名空间名称'); return }
  ElMessage.success(`创建命名空间 ${createForm.value.name} 成功`)
  createVisible.value = false
  fetchData()
}
function handleDelete(row: any) {
  ElMessageBox.confirm(`确定要删除命名空间 ${row.name} 吗？`, { type: 'error' })
    .then(() => { ElMessage.success('删除成功'); fetchData() })
}

onMounted(() => { fetchData() })
</script>

<style scoped lang="scss">
.namespaces-page { padding: 20px;
  .page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;
    .page-title { font-size: 24px; font-weight: 600; color: #1a1f3a; margin: 0; }
    .header-actions { display: flex; gap: 12px; }
  }
}
.sub-text { font-size: 12px; color: #999; }
</style>
