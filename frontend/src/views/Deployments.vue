<template>
  <div class="deployments-page">
    <div class="page-header">
      <h1 class="page-title">工作负载 (Deployments)</h1>
      <div class="header-actions">
        <el-button @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          创建
        </el-button>
      </div>
    </div>

    <el-card v-loading="loading">
      <!-- 筛选工具栏 -->
      <div class="toolbar">
        <div class="toolbar-left">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索 Deployment 名称"
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
        </div>

        <div class="toolbar-right">
          <el-dropdown @command="handleBatchAction">
            <el-button>
              批量操作
              <el-icon><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="restart">批量重启</el-dropdown-item>
                <el-dropdown-item command="delete" divided>批量删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- 表格 -->
      <el-table
        :data="filteredDeployments"
        style="width: 100%"
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />

        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_ready ? 'success' : 'warning'">
              {{ row.is_ready ? '就绪' : '未就绪' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="name" label="名称" min-width="250">
          <template #default="{ row }">
            <el-link type="primary" @click="viewDeployment(row)">
              {{ row.name }}
            </el-link>
          </template>
        </el-table-column>

        <el-table-column prop="namespace" label="命名空间" width="150" />

        <el-table-column label="副本数" width="180">
          <template #default="{ row }">
            <div class="replicas-info">
              <span :class="{ 'text-danger': row.replicas.ready !== row.replicas.desired }">
                {{ row.replicas.ready }}/{{ row.replicas.desired }}
              </span>
            </div>
            <div class="sub-text">就绪/期望</div>
          </template>
        </el-table-column>

        <el-table-column label="可用/更新中" width="150">
          <template #default="{ row }">
            <div>可用：{{ row.replicas.available }}</div>
            <div class="sub-text">更新中：{{ row.replicas.updated }}</div>
          </template>
        </el-table-column>

        <el-table-column label="镜像" min-width="200">
          <template #default="{ row }">
            <div v-for="(container, idx) in row.containers" :key="idx" class="container-image">
              {{ container.image }}
            </div>
          </template>
        </el-table-column>

        <el-table-column label="策略" width="120">
          <template #default="{ row }">
            {{ row.strategy?.type || '-' }}
          </template>
        </el-table-column>

        <el-table-column label="创建时间" width="160" sortable>
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDeployment(row)">
              详情
            </el-button>
            <el-button link type="primary" @click="showScaleDialog(row)">
              扩缩容
            </el-button>
            <el-dropdown trigger="click" @command="(cmd) => handleDeploymentAction(cmd, row)">
              <el-button link type="primary">
                更多
                <el-icon><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="restart">重启</el-dropdown-item>
                  <el-dropdown-item command="rollback">回滚</el-dropdown-item>
                  <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

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

    <!-- Deployment 详情抽屉 -->
    <el-drawer
      v-model="detailVisible"
      title="Deployment 详情"
      size="70%"
      :before-close="handleCloseDetail"
    >
      <div class="deployment-detail" v-loading="detailLoading">
        <el-descriptions :column="2" border title="基本信息">
          <el-descriptions-item label="名称">{{ selectedDeployment.name }}</el-descriptions-item>
          <el-descriptions-item label="命名空间">{{ selectedDeployment.namespace }}</el-descriptions-item>
          <el-descriptions-item label="策略">{{ selectedDeployment.strategy?.type || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(selectedDeployment.created_at) }}</el-descriptions-item>
        </el-descriptions>

        <h3 style="margin: 20px 0 12px">副本状态</h3>
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="stat-box">
              <div class="stat-label">期望副本</div>
              <div class="stat-value">{{ selectedDeployment.replicas?.desired || 0 }}</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-box">
              <div class="stat-label">就绪副本</div>
              <div class="stat-value success">{{ selectedDeployment.replicas?.ready || 0 }}</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-box">
              <div class="stat-label">可用副本</div>
              <div class="stat-value">{{ selectedDeployment.replicas?.available || 0 }}</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-box">
              <div class="stat-label">更新中</div>
              <div class="stat-value warning">{{ selectedDeployment.replicas?.updated || 0 }}</div>
            </div>
          </el-col>
        </el-row>

        <h3 style="margin: 20px 0 12px">容器</h3>
        <el-table :data="selectedDeployment.containers || []" border>
          <el-table-column prop="name" label="容器名" width="150" />
          <el-table-column prop="image" label="镜像" min-width="300" />
          <el-table-column label="资源请求" width="180">
            <template #default="{ row }">
              <div>CPU: {{ row.resources?.requests?.cpu || '-' }}</div>
              <div>内存：{{ row.resources?.requests?.memory || '-' }}</div>
            </template>
          </el-table-column>
          <el-table-column label="资源限制" width="180">
            <template #default="{ row }">
              <div>CPU: {{ row.resources?.limits?.cpu || '-' }}</div>
              <div>内存：{{ row.resources?.limits?.memory || '-' }}</div>
            </template>
          </el-table-column>
        </el-table>

        <h3 style="margin: 20px 0 12px">标签</h3>
        <div class="labels-container">
          <el-tag
            v-for="(value, key) in selectedDeployment.labels"
            :key="key"
            size="small"
            style="margin-right: 8px; margin-bottom: 8px"
          >
            {{ key }}={{ value }}
          </el-tag>
        </div>
      </div>
    </el-drawer>

    <!-- 扩缩容对话框 -->
    <el-dialog v-model="scaleVisible" title="扩缩容" width="400px">
      <el-form :model="scaleForm" label-width="100px">
        <el-form-item label="Deployment">
          <span>{{ scaleForm.name }}</span>
        </el-form-item>
        <el-form-item label="副本数" required>
          <el-input-number v-model="scaleForm.replicas" :min="0" :max="100" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="scaleVisible = false">取消</el-button>
        <el-button type="primary" @click="handleScale">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Refresh, Search, ArrowDown, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { deploymentApi, type Deployment } from '@/api/deployment'
import { clusterApi } from '@/api/cluster'

const loading = ref(false)
const detailLoading = ref(false)
const detailVisible = ref(false)
const scaleVisible = ref(false)

const filters = ref({
  keyword: '',
  namespace: '',
})

const pagination = ref({
  page: 1,
  pageSize: 10,
  total: 0,
})

const namespaces = ref<string[]>([])
const deployments = ref<Deployment[]>([])
const selectedDeployments = ref<any[]>([])
const selectedDeployment = ref<any>({})
const scaleForm = ref({ name: '', replicas: 3 })

const filteredDeployments = computed(() => {
  let result = deployments.value

  if (filters.value.keyword) {
    const keyword = filters.value.keyword.toLowerCase()
    result = result.filter((d) => d.name.toLowerCase().includes(keyword))
  }

  if (filters.value.namespace) {
    result = result.filter((d) => d.namespace === filters.value.namespace)
  }

  pagination.value.total = result.length
  return result
})

function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

async function fetchDeployments() {
  loading.value = true
  try {
    const data = await deploymentApi.getDeployments(filters.value.namespace)
    deployments.value = data.deployments || []
  } catch (error) {
    console.error('Failed to fetch deployments:', error)
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

async function handleRefresh() {
  await fetchDeployments()
  ElMessage.success('刷新成功')
}

function handleFilter() {
  pagination.value.page = 1
}

function handleSelectionChange(selection: any[]) {
  selectedDeployments.value = selection
}

function handlePageChange() {
  // 处理分页
}

function viewDeployment(deployment: any) {
  selectedDeployment.value = deployment
  detailVisible.value = true
}

function handleCloseDetail(done: () => void) {
  done()
}

function showScaleDialog(deployment: any) {
  scaleForm.value = {
    name: deployment.name,
    replicas: deployment.replicas?.desired || 3,
  }
  scaleVisible.value = true
}

async function handleScale() {
  try {
    // TODO: 调用 API 进行扩缩容
    await new Promise(resolve => setTimeout(resolve, 500))
    ElMessage.success(`已将 ${scaleForm.value.name} 副本数调整为 ${scaleForm.value.replicas}`)
    scaleVisible.value = false
    fetchDeployments()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function handleDeploymentAction(command: string, deployment: any) {
  try {
    if (command === 'restart') {
      await ElMessageBox.confirm(`确定要重启 ${deployment.name} 吗？`, '确认重启', { type: 'warning' })
      ElMessage.success('重启操作已提交')
    } else if (command === 'rollback') {
      ElMessage.info('回滚功能开发中')
    } else if (command === 'delete') {
      await ElMessageBox.confirm(`确定要删除 ${deployment.name} 吗？`, '确认删除', { type: 'error' })
      ElMessage.success('删除成功')
    }
    fetchDeployments()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

async function handleBatchAction(command: string) {
  if (selectedDeployments.value.length === 0) {
    ElMessage.warning('请先选择 Deployment')
    return
  }

  try {
    if (command === 'restart') {
      await ElMessageBox.confirm(`确定要重启选中的 ${selectedDeployments.value.length} 个 Deployment 吗？`, { type: 'warning' })
      ElMessage.success('批量重启操作已提交')
    } else if (command === 'delete') {
      await ElMessageBox.confirm(`确定要删除选中的 ${selectedDeployments.value.length} 个 Deployment 吗？`, { type: 'error' })
      ElMessage.success('批量删除操作已提交')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

function showCreateDialog() {
  ElMessage.info('创建 Deployment 功能开发中')
}

onMounted(async () => {
  await fetchNamespaces()
  await fetchDeployments()
})
</script>

<style scoped lang="scss">
.deployments-page {
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

.text-danger {
  color: #f56c6c;
  font-weight: 600;
}

.replicas-info {
  font-size: 16px;
  font-weight: 600;
}

.container-image {
  font-size: 13px;
  color: #666;
  padding: 4px 0;
}

.deployment-detail {
  h3 {
    font-size: 16px;
    font-weight: 600;
    color: #333;
    margin-top: 20px;
  }

  .stat-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    padding: 20px;
    text-align: center;

    .stat-label {
      font-size: 13px;
      color: rgba(255, 255, 255, 0.8);
      margin-bottom: 8px;
    }

    .stat-value {
      font-size: 28px;
      font-weight: 700;
      color: #fff;

      &.success {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }

      &.warning {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }
    }
  }

  .labels-container {
    padding: 12px;
    background: #f5f7fa;
    border-radius: 8px;
  }
}
</style>
