<template>
  <div class="nodes-page">
    <div class="page-header">
      <h1 class="page-title">节点管理</h1>
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
            placeholder="搜索节点名称、IP"
            style="width: 240px"
            clearable
            @clear="handleFilter"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>

          <el-select
            v-model="filters.status"
            placeholder="节点状态"
            clearable
            style="width: 140px"
            @change="handleFilter"
          >
            <el-option label="就绪" value="Ready" />
            <el-option label="未就绪" value="NotReady" />
          </el-select>

          <el-select
            v-model="filters.namespace"
            placeholder="命名空间"
            clearable
            style="width: 140px"
            @change="handleFilter"
          >
            <el-option v-for="ns in namespaces" :key="ns" :label="ns" :value="ns" />
          </el-select>
        </div>

        <div class="toolbar-right">
          <el-button-group>
            <el-button :class="{ active: viewMode === 'table' }" @click="viewMode = 'table'">
              <el-icon><Menu /></el-icon>
            </el-button>
            <el-button :class="{ active: viewMode === 'card' }" @click="viewMode = 'card'">
              <el-icon><Grid /></el-icon>
            </el-button>
          </el-button-group>

          <el-dropdown @command="handleBatchAction">
            <el-button>
              批量操作
              <el-icon><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="cordon">Cordon</el-dropdown-item>
                <el-dropdown-item command="uncordon">Uncordon</el-dropdown-item>
                <el-dropdown-item command="drain" divided>Drain</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- 表格视图 -->
      <div v-show="viewMode === 'table'" class="table-container">
        <el-table
          :data="filteredNodes"
          style="width: 100%"
          stripe
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />

          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.is_ready ? 'success' : 'danger'">
                {{ row.is_ready ? 'Ready' : 'NotReady' }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="name" label="名称" min-width="200" sortable>
            <template #default="{ row }">
              <el-link type="primary" @click="viewNodeDetail(row.name)">
                {{ row.name }}
              </el-link>
            </template>
          </el-table-column>

          <el-table-column prop="kubelet_version" label="Kubelet 版本" width="180" />

          <el-table-column prop="os_image" label="操作系统" width="180" />

          <el-table-column label="CPU" width="150" sortable>
            <template #default="{ row }">
              <div class="resource-text">
                <span>{{ formatCPU(row.allocatable?.cpu) }}</span>
              </div>
              <div class="sub-text">容量：{{ formatCPU(row.capacity?.cpu) }}</div>
            </template>
          </el-table-column>

          <el-table-column label="内存" width="150" sortable>
            <template #default="{ row }">
              <div class="resource-text">{{ formatBytes(row.allocatable?.memory_bytes) }}</div>
              <div class="sub-text">容量：{{ formatBytes(row.capacity?.memory_bytes) }}</div>
            </template>
          </el-table-column>

          <el-table-column label="Pod 容量" width="100" prop="allocatable.pods" sortable>
            <template #default="{ row }">
              {{ row.allocatable?.pods || 0 }}
            </template>
          </el-table-column>

          <el-table-column label="Internal IP" width="150">
            <template #default="{ row }">
              {{ row.addresses?.InternalIP || '-' }}
            </template>
          </el-table-column>

          <el-table-column label="创建时间" width="160" sortable>
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>

          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="viewNodeDetail(row.name)">
                详情
              </el-button>
              <el-dropdown trigger="click" @command="(cmd) => handleNodeAction(cmd, row)">
                <el-button link type="primary">
                  更多
                  <el-icon><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="cordon">
                      {{ row.is_ready ? 'Cordon' : 'Uncordon' }}
                    </el-dropdown-item>
                    <el-dropdown-item command="drain" divided>Drain</el-dropdown-item>
                    <el-dropdown-item command="logs" divided>查看事件</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 卡片视图 -->
      <div v-show="viewMode === 'card'" class="card-container">
        <el-row :gutter="20">
          <el-col :span="8" v-for="node in filteredNodes" :key="node.name">
            <div class="node-card" :class="{ 'not-ready': !node.is_ready }">
              <div class="node-card-header">
                <div class="node-name">{{ node.name }}</div>
                <el-tag :type="node.is_ready ? 'success' : 'danger'" size="small">
                  {{ node.is_ready ? 'Ready' : 'NotReady' }}
                </el-tag>
              </div>
              <div class="node-card-body">
                <div class="node-info-row">
                  <span class="label">版本:</span>
                  <span class="value">{{ node.kubelet_version }}</span>
                </div>
                <div class="node-info-row">
                  <span class="label">系统:</span>
                  <span class="value">{{ node.os_image }}</span>
                </div>
                <div class="node-info-row">
                  <span class="label">IP:</span>
                  <span class="value">{{ node.addresses?.InternalIP || '-' }}</span>
                </div>
                <div class="resource-bars">
                  <div class="resource-row">
                    <span class="label">CPU:</span>
                    <div class="progress-wrapper">
                      <el-progress
                        :percentage="getCPUUsagePercent(node)"
                        :stroke-width="8"
                        :show-text="false"
                      />
                      <span class="resource-value">{{ formatCPU(node.allocatable?.cpu) }}</span>
                    </div>
                  </div>
                  <div class="resource-row">
                    <span class="label">内存:</span>
                    <div class="progress-wrapper">
                      <el-progress
                        :percentage="getMemoryUsagePercent(node)"
                        :stroke-width="8"
                        :show-text="false"
                      />
                      <span class="resource-value">{{ formatBytes(node.allocatable?.memory_bytes) }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div class="node-card-footer">
                <el-button link type="primary" @click="viewNodeDetail(node.name)">
                  查看详情
                </el-button>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handlePageChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 节点详情抽屉 -->
    <el-drawer
      v-model="detailVisible"
      title="节点详情"
      size="60%"
      :before-close="handleCloseDetail"
    >
      <node-detail :node-name="selectedNodeName" v-if="detailVisible" />
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Refresh,
  Search,
  Menu,
  Grid,
  ArrowDown,
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useNodeStore } from '@/stores/node'
import { formatCPU, formatBytes } from '@/utils'
import NodeDetail from '@/components/NodeDetail.vue'

const router = useRouter()
const nodeStore = useNodeStore()

const loading = ref(false)
const viewMode = ref<'table' | 'card'>('table')
const detailVisible = ref(false)
const selectedNodeName = ref('')

const filters = ref({
  keyword: '',
  status: '',
  namespace: '',
})

const namespaces = ref(['default', 'kube-system', 'monitoring', 'production'])

const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0,
})

const nodes = computed(() => nodeStore.nodes)
const selectedNodes = ref<any[]>([])

const filteredNodes = computed(() => {
  let result = nodes.value

  if (filters.value.keyword) {
    const keyword = filters.value.keyword.toLowerCase()
    result = result.filter(
      (node) =>
        node.name.toLowerCase().includes(keyword) ||
        node.addresses?.InternalIP?.toLowerCase().includes(keyword)
    )
  }

  if (filters.value.status === 'Ready') {
    result = result.filter((node) => node.is_ready)
  } else if (filters.value.status === 'NotReady') {
    result = result.filter((node) => !node.is_ready)
  }

  pagination.value.total = result.length
  return result
})

function getCPUUsagePercent(node: any): number {
  const capacity = parseFloat(node.capacity?.cpu) || 0
  const allocatable = parseFloat(node.allocatable?.cpu) || 0
  return capacity > 0 ? Math.round((allocatable / capacity) * 100) : 0
}

function getMemoryUsagePercent(node: any): number {
  const capacity = node.capacity?.memory_bytes || 0
  const allocatable = node.allocatable?.memory_bytes || 0
  return capacity > 0 ? Math.round((allocatable / capacity) * 100) : 0
}

function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

async function handleRefresh() {
  loading.value = true
  try {
    await nodeStore.fetchNodes()
    ElMessage.success('刷新成功')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    loading.value = false
  }
}

function handleFilter() {
  pagination.value.page = 1
}

function handleSelectionChange(selection: any[]) {
  selectedNodes.value = selection
}

function handlePageChange() {
  // 处理分页
}

function viewNodeDetail(name: string) {
  selectedNodeName.value = name
  detailVisible.value = true
}

function handleCloseDetail(done: () => void) {
  done()
}

async function handleNodeAction(command: string, node: any) {
  try {
    if (command === 'cordon' || command === 'uncordon') {
      await ElMessageBox.confirm(
        `确定要${node.is_ready ? 'Cordon' : 'Uncordon'}节点 ${node.name} 吗？`,
        '确认操作',
        { type: 'warning' }
      )
      ElMessage.success(`操作成功：${node.name}`)
    } else if (command === 'drain') {
      await ElMessageBox.confirm(
        `确定要 Drain 节点 ${node.name} 吗？此操作将驱逐该节点上的所有 Pod`,
        '警告',
        { type: 'error', confirmButtonText: '确认', cancelButtonText: '取消' }
      )
      ElMessage.success(`开始 Drain 节点：${node.name}`)
    } else if (command === 'logs') {
      // 查看事件
      ElMessage.info('查看节点事件功能开发中')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

async function handleBatchAction(command: string) {
  if (selectedNodes.value.length === 0) {
    ElMessage.warning('请先选择节点')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要对选中的 ${selectedNodes.value.length} 个节点执行 ${command} 操作吗？`,
      '批量操作确认',
      { type: 'warning' }
    )
    ElMessage.success(`批量${command}操作已提交`)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

onMounted(async () => {
  loading.value = true
  try {
    await nodeStore.fetchNodes()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped lang="scss">
.nodes-page {
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

  .el-button-group {
    .el-button {
      &.active {
        background: #ecf5ff;
        color: #409EFF;
        border-color: #b3d8ff;
      }
    }
  }
}

.table-container {
  margin-top: 16px;
}

.card-container {
  margin-top: 16px;

  .node-card {
    background: #fff;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
    margin-bottom: 20px;
    transition: all 0.3s ease;

    &:hover {
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
    }

    &.not-ready {
      border-left: 3px solid #F56C6C;
    }

    .node-card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
      padding-bottom: 12px;
      border-bottom: 1px solid #f0f0f0;

      .node-name {
        font-size: 16px;
        font-weight: 600;
        color: #333;
      }
    }

    .node-card-body {
      .node-info-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
        font-size: 14px;

        .label {
          color: #888;
        }

        .value {
          color: #333;
        }
      }

      .resource-bars {
        margin-top: 12px;

        .resource-row {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 8px;

          .label {
            width: 50px;
            color: #888;
            font-size: 13px;
          }

          .progress-wrapper {
            flex: 1;
            display: flex;
            align-items: center;
            gap: 12px;

            .resource-value {
              font-size: 13px;
              color: #666;
              white-space: nowrap;
            }
          }
        }
      }
    }

    .node-card-footer {
      margin-top: 12px;
      padding-top: 12px;
      border-top: 1px solid #f0f0f0;
      text-align: right;
    }
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

.resource-text {
  font-size: 14px;
  color: #333;
}
</style>
