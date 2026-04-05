<template>
  <div class="networkpolicies-page">
    <div class="page-header">
      <h1 class="page-title">NetworkPolicy</h1>
      <div class="header-actions">
        <el-button @click="handleRefresh"><el-icon><Refresh /></el-icon> 刷新</el-button>
      </div>
    </div>

    <el-card v-loading="loading">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-input v-model="filters.keyword" placeholder="搜索 NetworkPolicy 名称" style="width: 240px" clearable>
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-select v-model="filters.namespace" placeholder="命名空间" clearable style="width: 160px">
            <el-option v-for="ns in namespaces" :key="ns" :label="ns" :value="ns" />
          </el-select>
        </div>
      </div>

      <el-table :data="policies" stripe>
        <el-table-column prop="name" label="名称" min-width="200">
          <template #default="{ row }">
            <el-link type="primary" @click="viewDetail(row)">{{ row.name }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="namespace" label="命名空间" width="120" />
        <el-table-column label="Pod Selector" min-width="200">
          <template #default="{ row }">
            <el-tag v-for="(value, key) in row.podSelector" :key="key" size="small" style="margin-right: 4px">
              {{ key }}={{ value || '' }}
            </el-tag>
            <span v-if="!row.podSelector || Object.keys(row.podSelector).length === 0">All Pods</span>
          </template>
        </el-table-column>
        <el-table-column label="策略类型" width="180">
          <template #default="{ row }">
            <el-tag v-for="type in row.policyTypes" :key="type" size="small" style="margin-right: 4px">{{ type }}</el-tag>
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
const policies = ref<any[]>([])
const filters = ref({ keyword: '', namespace: '' })

async function fetchData() {
  loading.value = true
  try {
    policies.value = [
      { name: 'default-deny-all', namespace: 'default', podSelector: {}, policyTypes: ['Ingress', 'Egress'] },
      { name: 'allow-nginx', namespace: 'default', podSelector: { app: 'nginx' }, policyTypes: ['Ingress'] },
    ]
  } finally {
    loading.value = false
  }
}

function handleRefresh() { fetchData(); ElMessage.success('刷新成功') }
function viewDetail(row: any) { ElMessage.info(`查看 NetworkPolicy: ${row.name}`) }
function handleDelete(row: any) {
  ElMessageBox.confirm(`确定要删除 ${row.name} 吗？`, { type: 'warning' })
    .then(() => { ElMessage.success('删除成功'); fetchData() })
}

onMounted(() => { fetchData() })
</script>

<style scoped lang="scss">
.networkpolicies-page { padding: 20px;
  .page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;
    .page-title { font-size: 24px; font-weight: 600; color: #1a1f3a; margin: 0; }
    .header-actions { display: flex; gap: 12px; }
  }
  .toolbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;
    .toolbar-left { display: flex; align-items: center; gap: 12px; }
  }
}
</style>
