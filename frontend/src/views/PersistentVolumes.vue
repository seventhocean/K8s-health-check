<template>
  <div class="pv-page">
    <div class="page-header">
      <h1 class="page-title">PersistentVolume</h1>
      <div class="header-actions">
        <el-button @click="handleRefresh"><el-icon><Refresh /></el-icon> 刷新</el-button>
      </div>
    </div>

    <el-card v-loading="loading">
      <el-table :data="pvs" stripe>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Bound' ? 'success' : 'warning'">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" min-width="200">
          <template #default="{ row }">
            <el-link type="primary" @click="viewDetail(row)">{{ row.name }}</el-link>
          </template>
        </el-table-column>
        <el-table-column label="容量" width="100">
          <template #default="{ row }">{{ row.capacity }}</template>
        </el-table-column>
        <el-table-column prop="storageClass" label="StorageClass" width="150" />
        <el-table-column prop="claim" label="Claim" min-width="200">
          <template #default="{ row }">
            <el-link v-if="row.claim" type="primary">{{ row.claim }}</el-link>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="accessModes" label="访问模式" width="150">
          <template #default="{ row }">
            <el-tag v-for="mode in row.accessModes" :key="mode" size="small" style="margin-right: 4px">{{ mode }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="volumeMode" label="卷模式" width="100" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const pvs = ref<any[]>([])

async function fetchData() {
  loading.value = true
  try {
    pvs.value = [
      { name: 'pv-data-001', capacity: '100Gi', storageClass: 'nfs', status: 'Bound', claim: 'default/data-pvc', accessModes: ['RWO'], volumeMode: 'Filesystem' },
      { name: 'pv-logs-002', capacity: '50Gi', storageClass: 'nfs', status: 'Available', claim: null, accessModes: ['RWX'], volumeMode: 'Filesystem' },
    ]
  } finally {
    loading.value = false
  }
}

function handleRefresh() { fetchData(); ElMessage.success('刷新成功') }
function viewDetail(row: any) { ElMessage.info(`查看 PV: ${row.name}`) }

onMounted(() => { fetchData() })
</script>

<style scoped lang="scss">
.pv-page { padding: 20px;
  .page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;
    .page-title { font-size: 24px; font-weight: 600; color: #1a1f3a; margin: 0; }
    .header-actions { display: flex; gap: 12px; }
  }
}
</style>
