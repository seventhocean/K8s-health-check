<template>
  <div class="common-page">
    <div class="page-header">
      <h1 class="page-title">{{ pageTitle }}</h1>
      <div class="header-actions">
        <el-button @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <el-card v-loading="loading">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-input
            v-model="filters.keyword"
            :placeholder="searchPlaceholder"
            style="width: 240px"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>

          <el-select
            v-model="filters.namespace"
            placeholder="命名空间"
            clearable
            style="width: 160px"
          >
            <el-option v-for="ns in namespaces" :key="ns" :label="ns" :value="ns" />
          </el-select>
        </div>
      </div>

      <el-table :data="tableData" style="width: 100%" stripe>
        <el-table-column label="名称" min-width="200">
          <template #default="{ row }">
            <el-link type="primary" @click="viewDetail(row)">{{ row.name }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="namespace" label="命名空间" width="150" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Active' ? 'success' : 'warning'">{{ row.status || 'Active' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="160" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">详情</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Refresh, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const props = defineProps<{
  pageTitle: string
  searchPlaceholder: string
  resourceType: string
}>()

const loading = ref(false)
const namespaces = ref(['default', 'kube-system', 'monitoring', 'production'])

const filters = ref({
  keyword: '',
  namespace: '',
})

const pagination = ref({
  page: 1,
  pageSize: 10,
  total: 0,
})

const tableData = ref<any[]>([])

function handleRefresh() {
  fetchData()
  ElMessage.success('刷新成功')
}

async function fetchData() {
  loading.value = true
  try {
    // TODO: 调用 API 获取数据
    // 模拟数据
    tableData.value = [
      { name: `${props.resourceType}-1`, namespace: 'default', status: 'Active', createdAt: '2024-01-01 10:00:00' },
      { name: `${props.resourceType}-2`, namespace: 'production', status: 'Active', createdAt: '2024-01-02 11:00:00' },
    ]
  } finally {
    loading.value = false
  }
}

function viewDetail(row: any) {
  ElMessage.info(`查看 ${props.resourceType}: ${row.name}`)
}

function handleDelete(row: any) {
  ElMessageBox.confirm(`确定要删除 ${row.name} 吗？`, '确认删除', { type: 'warning' })
    .then(() => {
      ElMessage.success('删除成功')
      fetchData()
    })
    .catch(() => {})
}
</script>

<style scoped lang="scss">
.common-page {
  padding: 20px;

  .page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;

    .page-title {
      font-size: 24px;
      font-weight: 600;
      color: #1a1f3a;
      margin: 0;
    }

    .header-actions {
      display: flex;
      gap: 12px;
    }
  }
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;

  .toolbar-left {
    display: flex;
    align-items: center;
    gap: 12px;
  }
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
