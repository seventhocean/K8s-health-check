<template>
  <div class="sc-page">
    <div class="page-header">
      <h1 class="page-title">StorageClass</h1>
      <div class="header-actions">
        <el-button @click="handleRefresh"><el-icon><Refresh /></el-icon> 刷新</el-button>
      </div>
    </div>

    <el-card v-loading="loading">
      <el-table :data="scs" stripe>
        <el-table-column prop="name" label="名称" min-width="200">
          <template #default="{ row }">
            <el-link type="primary" @click="viewDetail(row)">{{ row.name }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="provisioner" label="Provisioner" min-width="200" />
        <el-table-column label="回收策略" width="120">
          <template #default="{ row }">{{ row.reclaimPolicy }}</template>
        </el-table-column>
        <el-table-column label="卷绑定模式" width="120">
          <template #default="{ row }">{{ row.volumeBindingMode }}</template>
        </el-table-column>
        <el-table-column label="默认" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.default" type="success">是</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
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
const scs = ref<any[]>([])

async function fetchData() {
  loading.value = true
  try {
    scs.value = [
      { name: 'nfs', provisioner: 'nfs.csi.k8s.io', reclaimPolicy: 'Delete', volumeBindingMode: 'Immediate', default: true },
      { name: 'local-path', provisioner: 'rancher.io/local-path', reclaimPolicy: 'Delete', volumeBindingMode: 'WaitForFirstConsumer', default: false },
    ]
  } finally {
    loading.value = false
  }
}

function handleRefresh() { fetchData(); ElMessage.success('刷新成功') }
function viewDetail(row: any) { ElMessage.info(`查看 StorageClass: ${row.name}`) }

onMounted(() => { fetchData() })
</script>

<style scoped lang="scss">
.sc-page { padding: 20px;
  .page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;
    .page-title { font-size: 24px; font-weight: 600; color: #1a1f3a; margin: 0; }
    .header-actions { display: flex; gap: 12px; }
  }
}
</style>
