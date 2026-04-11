<template>
  <div class="services-page">
    <div class="page-header">
      <h1 class="page-title">Service</h1>
      <div class="header-actions">
        <el-button @click="handleRefresh"><el-icon><Refresh /></el-icon> 刷新</el-button>
        <el-button type="primary" @click="showCreate"><el-icon><Plus /></el-icon> 创建</el-button>
      </div>
    </div>

    <el-card v-loading="loading">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-input v-model="filters.keyword" placeholder="搜索 Service 名称" style="width: 240px" clearable>
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-select v-model="filters.namespace" placeholder="命名空间" clearable style="width: 160px">
            <el-option v-for="ns in namespaceStore.namespaces" :key="ns.name" :label="ns.name" :value="ns.name" />
          </el-select>
          <el-select v-model="filters.type" placeholder="类型" clearable style="width: 140px">
            <el-option label="ClusterIP" value="ClusterIP" />
            <el-option label="NodePort" value="NodePort" />
            <el-option label="LoadBalancer" value="LoadBalancer" />
            <el-option label="ExternalName" value="ExternalName" />
          </el-select>
        </div>
      </div>

      <el-table :data="services" stripe>
        <el-table-column label="状态" width="80">
          <template #default>
            <el-tag type="success">Active</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" min-width="200">
          <template #default="{ row }">
            <el-link type="primary" @click="viewDetail(row)">{{ row.name }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="namespace" label="命名空间" width="120" />
        <el-table-column prop="type" label="类型" width="130">
          <template #default="{ row }">
            <el-tag size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="clusterIP" label="Cluster IP" width="140" />
        <el-table-column label="端口" width="180">
          <template #default="{ row }">
            <span v-for="(port, idx) in row.ports" :key="idx">
              {{ port.port }}:{{ port.targetPort }}/{{ port.protocol }}
              <br v-if="idx < row.ports.length - 1" />
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Selector" min-width="180">
          <template #default="{ row }">
            <el-tag v-for="(value, key) in row.selector" :key="key" size="small" style="margin-right: 4px">
              {{ key }}={{ value }}
            </el-tag>
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
import { Refresh, Search, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { serviceApi } from '@/api/service'
import { useNamespaceStore } from '@/stores/namespace'

const namespaceStore = useNamespaceStore()
const loading = ref(false)
const services = ref<any[]>([])
const filters = ref({ keyword: '', namespace: '', type: '' })

async function fetchData() {
  loading.value = true
  try {
    const data = await serviceApi.getServices(filters.value.namespace || undefined)
    services.value = (data.services || []).map(svc => ({
      name: svc.name,
      namespace: svc.namespace,
      type: svc.type,
      clusterIP: svc.cluster_ip,
      externalIP: svc.external_ip,
      ports: svc.ports || [],
      selector: svc.selector || {},
      createdAt: svc.created_at,
    }))
  } catch (error) {
    ElMessage.error('获取 Service 列表失败')
  } finally {
    loading.value = false
  }
}

function handleRefresh() { fetchData(); ElMessage.success('刷新成功') }
function viewDetail(row: any) { ElMessage.info(`查看 Service: ${row.name}`) }
function handleDelete(row: any) {
  ElMessageBox.confirm(`确定要删除 ${row.name} 吗？`, { type: 'warning' })
    .then(() => { ElMessage.success('删除成功'); fetchData() })
}
function showCreate() { ElMessage.info('创建 Service 功能开发中') }

onMounted(async () => {
  await namespaceStore.fetchNamespaces()
  fetchData()
})
</script>

<style scoped lang="scss">
.services-page {
  padding: 20px;
  .page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
    .page-title { font-size: 24px; font-weight: 600; color: #1a1f3a; margin: 0; }
    .header-actions { display: flex; gap: 12px; }
  }
  .toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    .toolbar-left { display: flex; align-items: center; gap: 12px; }
  }
}
</style>
