<template>
  <div class="deployments-page">
    <h1 class="page-title">Deployments 列表</h1>

    <el-card v-loading="loading">
      <div class="toolbar">
        <el-select v-model="selectedNamespace" placeholder="选择命名空间" clearable @change="handleRefresh">
          <el-option
            v-for="ns in namespaces"
            :key="ns"
            :label="ns"
            :value="ns"
          />
        </el-select>
        <el-button type="primary" @click="handleRefresh" style="margin-left: 10px">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>

      <el-table :data="deployments" style="width: 100%; margin-top: 15px">
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_ready ? 'success' : 'warning'">
              {{ row.is_ready ? '就绪' : '未就绪' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="name" label="名称" min-width="200" />

        <el-table-column prop="namespace" label="命名空间" width="150" />

        <el-table-column label="副本数" width="150">
          <template #default="{ row }">
            <span :class="{ 'text-danger': row.replicas.ready !== row.replicas.desired }">
              {{ row.replicas.ready }}/{{ row.replicas.desired }}
            </span>
            <span class="sub-text"> (期望/就绪)</span>
          </template>
        </el-table-column>

        <el-table-column label="可用副本" width="100">
          <template #default="{ row }">
            {{ row.replicas.available }}
          </template>
        </el-table-column>

        <el-table-column label="更新中" width="100">
          <template #default="{ row }">
            {{ row.replicas.updated }}
          </template>
        </el-table-column>

        <el-table-column label="策略" width="120">
          <template #default="{ row }">
            {{ row.strategy?.type || '-' }}
          </template>
        </el-table-column>

        <el-table-column label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { deploymentApi, type Deployment } from '@/api/deployment'
import { clusterApi } from '@/api/cluster'
import { formatTime } from '@/utils'

const loading = ref(false)
const deployments = ref<Deployment[]>([])
const namespaces = ref<string[]>([])
const selectedNamespace = ref<string>()

async function fetchDeployments() {
  loading.value = true
  try {
    const data = await deploymentApi.getDeployments(selectedNamespace.value)
    deployments.value = data.deployments || []
  } catch (error) {
    console.error('Failed to fetch deployments:', error)
  } finally {
    loading.value = false
  }
}

async function fetchNamespaces() {
  try {
    const data = await clusterApi.getNamespaces()
    namespaces.value = data.namespaces || []
  } catch (error) {
    console.error('Failed to fetch namespaces:', error)
  }
}

function handleRefresh() {
  fetchDeployments()
}

onMounted(async () => {
  await fetchNamespaces()
  await fetchDeployments()
})
</script>

<style scoped>
.deployments-page {
  padding: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #333;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sub-text {
  font-size: 12px;
  color: #999;
}

.text-danger {
  color: #f56c6c;
  font-weight: 600;
}
</style>
