<template>
  <div class="pods-page">
    <h1 class="page-title">Pods 列表</h1>

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

      <el-table :data="pods" style="width: 100%; margin-top: 15px">
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.phase)">
              {{ row.phase }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="name" label="名称" min-width="200" />

        <el-table-column prop="namespace" label="命名空间" width="150" />

        <el-table-column prop="node_name" label="节点" width="180" />

        <el-table-column prop="host_ip" label="主机 IP" width="140" />

        <el-table-column prop="pod_ip" label="Pod IP" width="140" />

        <el-table-column label="容器" width="100">
          <template #default="{ row }">
            {{ row.containers?.ready || 0 }}/{{ row.containers?.count || 0 }}
          </template>
        </el-table-column>

        <el-table-column label="重启次数" width="100">
          <template #default="{ row }">
            {{ getTotalRestarts(row) }}
          </template>
        </el-table-column>

        <el-table-column label="运行时间" width="120">
          <template #default="{ row }">
            {{ formatRelativeTime(row.start_time || row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { podApi, type Pod } from '@/api/pod'
import { clusterApi } from '@/api/cluster'
import { formatRelativeTime } from '@/utils'

const loading = ref(false)
const pods = ref<Pod[]>([])
const namespaces = ref<string[]>([])
const selectedNamespace = ref<string>()

async function fetchPods() {
  loading.value = true
  try {
    const data = await podApi.getPods(selectedNamespace.value)
    pods.value = data.pods || []
  } catch (error) {
    console.error('Failed to fetch pods:', error)
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
  fetchPods()
}

function getStatusType(phase: string): string {
  const typeMap: Record<string, string> = {
    'Running': 'success',
    'Pending': 'warning',
    'Failed': 'danger',
    'Succeeded': 'info',
    'Unknown': 'info',
  }
  return typeMap[phase] || 'info'
}

function getTotalRestarts(pod: Pod): number {
  return pod.containers?.statuses?.reduce((sum, cs) => sum + (cs.restart_count || 0), 0) || 0
}

onMounted(async () => {
  await fetchNamespaces()
  await fetchPods()
})
</script>

<style scoped>
.pods-page {
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
</style>
