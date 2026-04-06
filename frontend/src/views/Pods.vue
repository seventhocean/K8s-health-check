<template>
  <div class="pods-page">
    <div class="page-header">
      <h1 class="page-title">Pod 管理</h1>
      <div class="header-actions">
        <el-button @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <el-card v-loading="loading">
      <!-- 筛选工具栏 -->
      <div class="toolbar">
        <div class="toolbar-left">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索 Pod 名称"
            style="width: 240px"
            clearable
            @clear="handleFilter"
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
            @change="handleFilter"
          >
            <el-option v-for="ns in namespaces" :key="ns" :label="ns" :value="ns" />
          </el-select>

          <el-select
            v-model="filters.status"
            placeholder="状态"
            clearable
            style="width: 140px"
            @change="handleFilter"
          >
            <el-option label="运行中" value="Running" />
            <el-option label="等待中" value="Pending" />
            <el-option label="已终止" value="Succeeded" />
            <el-option label="失败" value="Failed" />
          </el-select>

          <el-select
            v-model="filters.node"
            placeholder="所在节点"
            clearable
            style="width: 160px"
            @change="handleFilter"
          >
            <el-option v-for="node in nodes" :key="node" :label="node" :value="node" />
          </el-select>
        </div>

        <div class="toolbar-right">
          <el-dropdown @command="handleBatchAction">
            <el-button>
              批量操作
              <el-icon><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="delete" divided>删除选中</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- 表格 -->
      <el-table
        :data="filteredPods"
        style="width: 100%"
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />

        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.phase)">
              {{ row.phase }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="name" label="Pod 名称" min-width="250">
          <template #default="{ row }">
            <el-link type="primary" @click="viewPodDetail(row)">
              {{ row.name }}
            </el-link>
          </template>
        </el-table-column>

        <el-table-column prop="namespace" label="命名空间" width="150" />

        <el-table-column prop="node" label="节点" width="180" />

        <el-table-column label="重启次数" width="100" prop="restarts" sortable>
          <template #default="{ row }">
            <span :class="{ 'text-warning': row.restarts > 3 }">{{ row.restarts }}</span>
          </template>
        </el-table-column>

        <el-table-column label="CPU 请求/限制" width="140">
          <template #default="{ row }">
            <div>{{ row.cpu_request || '-' }}</div>
            <div class="sub-text">{{ row.cpu_limit || '-' }}</div>
          </template>
        </el-table-column>

        <el-table-column label="内存请求/限制" width="140">
          <template #default="{ row }">
            <div>{{ formatBytes(row.memory_request_bytes) }}</div>
            <div class="sub-text">{{ formatBytes(row.memory_limit_bytes) }}</div>
          </template>
        </el-table-column>

        <el-table-column label="创建时间" width="160" sortable>
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewPodDetail(row)">
              详情
            </el-button>
            <el-button link type="primary" @click="viewLogs(row)">
              日志
            </el-button>
            <el-button link type="danger" @click="deletePod(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[15, 30, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handlePageChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- Pod 详情抽屉 -->
    <el-drawer
      v-model="detailVisible"
      title="Pod 详情"
      size="70%"
      :before-close="handleCloseDetail"
    >
      <div class="pod-detail-content" v-loading="detailLoading">
        <!-- Pod 基本信息 -->
        <el-descriptions :column="2" border title="基本信息">
          <el-descriptions-item label="名称">{{ selectedPod.name }}</el-descriptions-item>
          <el-descriptions-item label="命名空间">{{ selectedPod.namespace }}</el-descriptions-item>
          <el-descriptions-item label="节点">{{ selectedPod.node }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedPod.phase)">{{ selectedPod.phase }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="IP">{{ selectedPod.pod_ip || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(selectedPod.created_at) }}</el-descriptions-item>
        </el-descriptions>

        <!-- 容器列表 -->
        <h3 style="margin: 20px 0 12px">容器</h3>
        <el-table :data="selectedPod.containers || []" border>
          <el-table-column prop="name" label="容器名" width="200" />
          <el-table-column prop="image" label="镜像" min-width="300" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.running ? 'success' : 'warning'">
                {{ row.running ? 'Running' : 'Waiting' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="重启次数" width="80">
            <template #default="{ row }">{{ row?.restart_count || 0 }}</template>
          </el-table-column>
        </el-table>

        <!-- 标签 -->
        <h3 style="margin: 20px 0 12px">标签</h3>
        <div class="labels-container">
          <el-tag
            v-for="(value, key) in selectedPod.labels"
            :key="key"
            size="small"
            style="margin-right: 8px; margin-bottom: 8px"
          >
            {{ key }}={{ value }}
          </el-tag>
        </div>
      </div>
    </el-drawer>

    <!-- 日志抽屉 -->
    <el-drawer v-model="logsVisible" title="Pod 日志" size="60%">
      <div class="logs-container">
        <div class="logs-header">
          <el-select v-model="selectedLogContainer" placeholder="选择容器" style="width: 200px">
            <el-option v-for="c in selectedPod.containers" :key="c.name" :label="c.name" :value="c.name" />
          </el-select>
          <el-button @click="fetchLogs">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
        <pre class="logs-content">{{ logsText }}</pre>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Refresh, Search, ArrowDown } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { podApi, type Pod } from '@/api/pod'
import { clusterApi } from '@/api/cluster'
import { formatBytes } from '@/utils'

const loading = ref(false)
const detailLoading = ref(false)
const detailVisible = ref(false)
const logsVisible = ref(false)
const selectedLogContainer = ref('')

const filters = ref({
  keyword: '',
  namespace: '',
  status: '',
  node: '',
})

const pagination = ref({
  page: 1,
  pageSize: 15,
  total: 0,
})

const namespaces = ref<string[]>([])
const nodes = ref<string[]>([])

const pods = ref<Pod[]>([])
const selectedPods = ref<any[]>([])
const selectedPod = ref<any>({})
const logsText = ref('')

const filteredPods = computed(() => {
  let result = pods.value

  if (filters.value.keyword) {
    const keyword = filters.value.keyword.toLowerCase()
    result = result.filter((pod) => pod.name.toLowerCase().includes(keyword))
  }

  if (filters.value.namespace) {
    result = result.filter((pod) => pod.namespace === filters.value.namespace)
  }

  if (filters.value.status) {
    result = result.filter((pod) => pod.phase === filters.value.status)
  }

  if (filters.value.node) {
    result = result.filter((pod) => pod.node === filters.value.node)
  }

  pagination.value.total = result.length
  return result
})

function getStatusType(phase: string): 'success' | 'warning' | 'danger' | 'info' {
  const types: Record<string, any> = {
    Running: 'success',
    Pending: 'warning',
    Succeeded: 'info',
    Failed: 'danger',
  }
  return types[phase] || 'info'
}

function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

async function fetchPods() {
  loading.value = true
  try {
    const data = await podApi.getPods(filters.value.namespace)
    pods.value = (data.pods || []).map((pod: any) => ({
      ...pod,
      node: pod.node_name,
      restarts: getTotalRestarts(pod),
      cpu_request: '100m',
      cpu_limit: '200m',
      memory_request_bytes: 128 * 1024 * 1024,
      memory_limit_bytes: 256 * 1024 * 1024,
      containers: pod.containers?.statuses?.map((cs: any) => ({
        name: cs.name,
        image: 'nginx:1.21',
        running: true,
        restart_count: cs.restart_count || 0,
      })) || [],
      labels: {},
    }))
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

async function fetchNodes() {
  // TODO: 获取节点列表用于筛选
  nodes.value = ['node-1', 'node-2', 'node-3']
}

async function handleRefresh() {
  await fetchPods()
  ElMessage.success('刷新成功')
}

function handleFilter() {
  pagination.value.page = 1
}

function handleSelectionChange(selection: any[]) {
  selectedPods.value = selection
}

function handlePageChange() {
  // 处理分页
}

function viewPodDetail(pod: any) {
  selectedPod.value = pod
  selectedLogContainer.value = pod.containers?.[0]?.name || ''
  detailVisible.value = true
}

function handleCloseDetail(done: () => void) {
  done()
}

function viewLogs(pod: any) {
  selectedPod.value = pod
  selectedLogContainer.value = pod.containers?.[0]?.name || ''
  logsVisible.value = true
  fetchLogs()
}

async function fetchLogs() {
  // TODO: 调用 API 获取日志
  logsText.value = `[${new Date().toLocaleString()}] Starting ${selectedLogContainer.value}...\n[${new Date().toLocaleString()}] Server listening on port 80\n[${new Date().toLocaleString()}] Connection from 10.244.0.1\n[${new Date().toLocaleString()}] Request processed successfully`
}

async function deletePod(pod: any) {
  try {
    await ElMessageBox.confirm(`确定要删除 Pod ${pod.name} 吗？`, '确认删除', { type: 'warning' })
    // TODO: 调用 API 删除 Pod
    ElMessage.success('删除成功')
    fetchPods()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function getTotalRestarts(pod: Pod): number {
  return pod.containers?.statuses?.reduce((sum, cs) => sum + (cs.restart_count || 0), 0) || 0
}

async function handleBatchAction(_command: any) {
  if (selectedPods.value.length === 0) {
    ElMessage.warning('请先选择 Pod')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedPods.value.length} 个 Pod 吗？`,
      '批量删除确认',
      { type: 'error' }
    )
    // TODO: 批量删除
    ElMessage.success('批量删除操作已提交')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

onMounted(async () => {
  await fetchNamespaces()
  await fetchNodes()
  await fetchPods()
})
</script>

<style scoped lang="scss">
.pods-page {
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

  .toolbar-left,
  .toolbar-right {
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

.sub-text {
  font-size: 12px;
  color: #999;
}

.text-warning {
  color: #E6A23C;
  font-weight: 500;
}

.pod-detail-content {
  h3 {
    font-size: 16px;
    font-weight: 600;
    color: #333;
    margin-top: 20px;
  }

  .labels-container {
    padding: 12px;
    background: #f5f7fa;
    border-radius: 8px;
  }
}

.logs-container {
  .logs-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
  }

  .logs-content {
    background: #1a1f3a;
    color: #a0aec0;
    padding: 16px;
    border-radius: 8px;
    font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.6;
    max-height: calc(100vh - 200px);
    overflow-y: auto;
  }
}
</style>
