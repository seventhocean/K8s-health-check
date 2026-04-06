<template>
  <div class="pvc-page">
    <div class="page-header">
      <h1 class="page-title">PersistentVolumeClaim</h1>
      <div class="header-actions">
        <el-button @click="handleRefresh"><el-icon><Refresh /></el-icon> 刷新</el-button>
      </div>
    </div>

    <el-card v-loading="loading">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-input v-model="filters.keyword" placeholder="搜索 PVC 名称" style="width: 240px" clearable>
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-select v-model="filters.namespace" placeholder="命名空间" clearable style="width: 160px">
            <el-option v-for="ns in namespaces" :key="ns" :label="ns" :value="ns" />
          </el-select>
        </div>
      </div>

      <el-table :data="pvcs" stripe>
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
        <el-table-column prop="namespace" label="命名空间" width="120" />
        <el-table-column label="容量" width="100">
          <template #default="{ row }">{{ row.capacity }}</template>
        </el-table-column>
        <el-table-column prop="storageClass" label="StorageClass" width="150" />
        <el-table-column prop="volume" label="Volume" min-width="180">
          <template #default="{ row }">
            <el-link v-if="row.volume" type="primary">{{ row.volume }}</el-link>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="accessModes" label="访问模式" width="150">
          <template #default="{ row }">
            <el-tag v-for="mode in row.accessModes" :key="mode" size="small" style="margin-right: 4px">{{ mode }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">详情</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Refresh, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const namespaces = ref(['default', 'kube-system', 'monitoring', 'production'])
const pvcs = ref<any[]>([])
const filters = ref({ keyword: '', namespace: '' })

async function fetchData() {
  loading.value = true
  try {
    pvcs.value = [
      { name: 'data-pvc', namespace: 'default', capacity: '10Gi', storageClass: 'nfs', status: 'Bound', volume: 'pv-data-001', accessModes: ['RWO'] },
      { name: 'logs-pvc', namespace: 'default', capacity: '5Gi', storageClass: 'nfs', status: 'Pending', volume: null, accessModes: ['RWX'] },
    ]
  } finally {
    loading.value = false
  }
}

function handleRefresh() { fetchData(); ElMessage.success('刷新成功') }
function viewDetail(row: any) { ElMessage.info(`查看 PVC: ${row.name}`) }
function handleDelete(row: any) {
  ElMessageBox.confirm(`确定要删除 ${row.name} 吗？`, { type: 'warning' })
    .then(() => { ElMessage.success('删除成功'); fetchData() })
}

onMounted(() => { fetchData() })
</script>

<style scoped lang="scss">
.pvc-page { padding: 20px;
  .page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;
    .page-title { font-size: 24px; font-weight: 600; color: #1a1f3a; margin: 0; }
    .header-actions { display: flex; gap: 12px; }
  }
  .toolbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;
    .toolbar-left { display: flex; align-items: center; gap: 12px; }
  }
}
</style>
