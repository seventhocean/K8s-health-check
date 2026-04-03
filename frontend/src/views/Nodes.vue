<template>
  <div class="nodes-page">
    <h1 class="page-title">节点列表</h1>

    <el-card v-loading="loading">
      <div class="toolbar">
        <el-button type="primary" @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>

      <el-table :data="nodes" style="width: 100%; margin-top: 15px">
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_ready ? 'success' : 'danger'">
              {{ row.is_ready ? 'Ready' : 'NotReady' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="name" label="名称" min-width="200" />

        <el-table-column prop="kubelet_version" label="Kubelet 版本" width="180" />

        <el-table-column prop="os_image" label="操作系统" width="180" />

        <el-table-column label="CPU" width="150">
          <template #default="{ row }">
            <div>{{ formatCPU(row.allocatable.cpu) }}</div>
            <div class="sub-text">容量：{{ formatCPU(row.capacity.cpu) }}</div>
          </template>
        </el-table-column>

        <el-table-column label="内存" width="150">
          <template #default="{ row }">
            <div>{{ formatBytes(row.allocatable.memory_bytes) }}</div>
            <div class="sub-text">容量：{{ formatBytes(row.capacity.memory_bytes) }}</div>
          </template>
        </el-table-column>

        <el-table-column label="Pod 容量" width="100">
          <template #default="{ row }">
            {{ row.allocatable.pods }}
          </template>
        </el-table-column>

        <el-table-column label="Internal IP" width="150">
          <template #default="{ row }">
            {{ row.addresses?.InternalIP || '-' }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewNode(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { useNodeStore } from '@/stores/node'
import { formatCPU, formatBytes } from '@/utils'

const nodeStore = useNodeStore()
const nodes = computed(() => nodeStore.nodes)
const loading = computed(() => nodeStore.loading)

async function handleRefresh() {
  await nodeStore.fetchNodes()
}

function viewNode(row: any) {
  // TODO: 实现节点详情页面
  console.log('View node:', row)
}

onMounted(async () => {
  await nodeStore.fetchNodes()
})
</script>

<style scoped>
.nodes-page {
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
  justify-content: flex-end;
}

.sub-text {
  font-size: 12px;
  color: #999;
}
</style>
