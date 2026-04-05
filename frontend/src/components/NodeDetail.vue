<template>
  <div class="node-detail" v-loading="loading">
    <!-- 基本信息卡片 -->
    <el-card class="info-card">
      <div class="card-header">
        <div class="header-left">
          <el-icon class="header-icon"><Cpu /></el-icon>
          <div class="header-info">
            <h2 class="node-name">{{ nodeDetail.name }}</h2>
            <div class="node-status">
              <el-tag :type="nodeDetail.is_ready ? 'success' : 'danger'">
                {{ nodeDetail.is_ready ? 'Ready' : 'NotReady' }}
              </el-tag>
              <span class="node-version">{{ nodeDetail.kubelet_version }}</span>
            </div>
          </div>
        </div>
        <div class="header-actions">
          <el-button :type="nodeDetail.is_ready ? 'warning' : 'success'" @click="handleCordonUncordon">
            {{ nodeDetail.is_ready ? 'Cordon' : 'Uncordon' }}
          </el-button>
          <el-button type="danger" @click="handleDrain">Drain</el-button>
        </div>
      </div>

      <el-descriptions :column="3" border class="node-descriptions">
        <el-descriptions-item label="操作系统">{{ nodeDetail.os_image || '-' }}</el-descriptions-item>
        <el-descriptions-item label="架构">{{ nodeDetail.architecture || '-' }}</el-descriptions-item>
        <el-descriptions-item label="Internal IP">{{ nodeDetail.addresses?.InternalIP || '-' }}</el-descriptions-item>
        <el-descriptions-item label="External IP">{{ nodeDetail.addresses?.ExternalIP || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(nodeDetail.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="标签">
          <el-tag v-for="(value, key) in nodeDetail.labels" :key="key" size="small" style="margin-right: 4px; margin-bottom: 4px">
            {{ key }}={{ value }}
          </el-tag>
          <span v-if="!nodeDetail.labels || Object.keys(nodeDetail.labels).length === 0">-</span>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 标签页 -->
    <el-card style="margin-top: 20px">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane name="overview">
          <template #label>
            <span><el-icon><DataBoard /></el-icon> 资源概览</span>
          </template>

          <!-- 资源容量卡片 -->
          <el-row :gutter="20" style="margin-top: 20px">
            <el-col :span="6">
              <div class="resource-stat-card">
                <div class="resource-icon cpu">
                  <el-icon><Cpu /></el-icon>
                </div>
                <div class="resource-info">
                  <div class="resource-label">CPU 容量</div>
                  <div class="resource-value">{{ formatCPU(nodeDetail.capacity?.cpu) }}</div>
                  <div class="resource-sub">可分配：{{ formatCPU(nodeDetail.allocatable?.cpu) }}</div>
                </div>
              </div>
            </el-col>

            <el-col :span="6">
              <div class="resource-stat-card">
                <div class="resource-icon memory">
                  <el-icon><Memo /></el-icon>
                </div>
                <div class="resource-info">
                  <div class="resource-label">内存容量</div>
                  <div class="resource-value">{{ formatBytes(nodeDetail.capacity?.memory_bytes) }}</div>
                  <div class="resource-sub">可分配：{{ formatBytes(nodeDetail.allocatable?.memory_bytes) }}</div>
                </div>
              </div>
            </el-col>

            <el-col :span="6">
              <div class="resource-stat-card">
                <div class="resource-icon pods">
                  <el-icon><Box /></el-icon>
                </div>
                <div class="resource-info">
                  <div class="resource-label">Pod 容量</div>
                  <div class="resource-value">{{ nodeDetail.allocatable?.pods || 0 }}</div>
                  <div class="resource-sub">已运行：{{ runningPods }} 个</div>
                </div>
              </div>
            </el-col>

            <el-col :span="6">
              <div class="resource-stat-card">
                <div class="resource-icon storage">
                  <el-icon><Folder /></el-icon>
                </div>
                <div class="resource-info">
                  <div class="resource-label">存储容量</div>
                  <div class="resource-value">{{ formatBytes(nodeDetail.capacity?.ephemeral_storage_bytes) }}</div>
                  <div class="resource-sub">可分配：{{ formatBytes(nodeDetail.allocatable?.ephemeral_storage_bytes) }}</div>
                </div>
              </div>
            </el-col>
          </el-row>

          <!-- 资源使用图表 -->
          <el-row :gutter="20" style="margin-top: 20px">
            <el-col :span="12">
              <div class="chart-card">
                <div class="chart-title">CPU 使用趋势</div>
                <div ref="cpuTrendChartRef" style="height: 300px"></div>
              </div>
            </el-col>

            <el-col :span="12">
              <div class="chart-card">
                <div class="chart-title">内存使用趋势</div>
                <div ref="memoryTrendChartRef" style="height: 300px"></div>
              </div>
            </el-col>
          </el-row>
        </el-tab-pane>

        <el-tab-pane name="pods">
          <template #label>
            <span><el-icon><Box /></el-icon> 运行中的 Pod ({{ pods.length }})</span>
          </template>

          <el-table :data="pods" style="width: 100%" v-loading="podsLoading">
            <el-table-column prop="name" label="Pod 名称" min-width="200">
              <template #default="{ row }">
                <el-link type="primary" @click="viewPod(row.name)">{{ row.name }}</el-link>
              </template>
            </el-table-column>
            <el-table-column prop="namespace" label="命名空间" width="150" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.phase === 'Running' ? 'success' : 'warning'">{{ row.phase }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="restarts" label="重启次数" width="80" />
            <el-table-column label="CPU 请求" width="100">
              <template #default="{ row }">{{ row.cpu_request || '-' }}</template>
            </el-table-column>
            <el-table-column label="内存请求" width="100">
              <template #default="{ row }">{{ formatBytes(row.memory_request_bytes) || '-' }}</template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="viewPod(row.name)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane name="events">
          <template #label>
            <span><el-icon><Bell /></el-icon> 事件</span>
          </template>

          <el-table :data="events" style="width: 100%" v-loading="eventsLoading">
            <el-table-column prop="type" label="类型" width="80">
              <template #default="{ row }">
                <el-tag :type="row.type === 'Normal' ? 'info' : 'warning'">{{ row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="reason" label="原因" width="150" />
            <el-table-column prop="message" label="消息" min-width="300" />
            <el-table-column prop="count" label="次数" width="80" />
            <el-table-column prop="firstTimestamp" label="首次发生" width="160">
              <template #default="{ row }">{{ formatDate(row.firstTimestamp) }}</template>
            </el-table-column>
            <el-table-column prop="lastTimestamp" label="最近发生" width="160">
              <template #default="{ row }">{{ formatDate(row.lastTimestamp) }}</template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane name="conditions">
          <template #label>
            <span><el-icon><Warning /></el-icon> 节点条件</span>
          </template>

          <el-table :data="conditions" style="width: 100%">
            <el-table-column prop="type" label="类型" width="200" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'True' ? 'success' : 'danger'">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="reason" label="原因" width="150" />
            <el-table-column prop="message" label="消息" min-width="300" />
            <el-table-column prop="lastTransitionTime" label="最后转变时间" width="180">
              <template #default="{ row }">{{ formatDate(row.lastTransitionTime) }}</template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import {
  Cpu,
  Memo,
  Box,
  Folder,
  DataBoard,
  Bell,
  Warning,
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'
import { useNodeStore } from '@/stores/node'
import { formatCPU, formatBytes } from '@/utils'

const props = defineProps<{
  nodeName: string
}>()

const nodeStore = useNodeStore()

const loading = ref(false)
const podsLoading = ref(false)
const eventsLoading = ref(false)
const activeTab = ref('overview')

const nodeDetail = ref<any>({
  name: '',
  is_ready: false,
  kubelet_version: '',
  os_image: '',
  architecture: '',
  addresses: {},
  labels: {},
  capacity: {},
  allocatable: {},
  conditions: [],
  created_at: '',
})

const pods = ref<any[]>([])
const events = ref<any[]>([])
const conditions = ref<any[]>([])
const runningPods = ref(0)

let cpuTrendChart: ECharts | null = null
let memoryTrendChart: ECharts | null = null

const cpuTrendChartRef = ref<HTMLElement>()
const memoryTrendChartRef = ref<HTMLElement>()

function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

async function fetchNodeDetail() {
  loading.value = true
  try {
    const data = await nodeStore.fetchNode(props.nodeName)
    nodeDetail.value = data || {}

    // 解析条件
    if (data?.conditions) {
      conditions.value = Object.entries(data.conditions).map(([type, status]: any) => ({
        type,
        status: status === 'True' ? 'True' : 'False',
        reason: '',
        message: '',
        lastTransitionTime: '',
      }))
    }

    // 模拟 Pod 数据
    fetchPods()
    fetchEvents()
  } catch (error) {
    ElMessage.error('获取节点详情失败')
  } finally {
    loading.value = false
  }
}

async function fetchPods() {
  podsLoading.value = true
  try {
    // TODO: 调用 API 获取该节点上的 Pod
    // 模拟数据
    pods.value = [
      { name: 'nginx-deployment-7d8f9b', namespace: 'default', phase: 'Running', restarts: 0, cpu_request: '100m', memory_request_bytes: 128 * 1024 * 1024 },
      { name: 'redis-master-0', namespace: 'default', phase: 'Running', restarts: 2, cpu_request: '200m', memory_request_bytes: 256 * 1024 * 1024 },
    ]
    runningPods.value = pods.value.filter(p => p.phase === 'Running').length
  } finally {
    podsLoading.value = false
  }
}

async function fetchEvents() {
  eventsLoading.value = true
  try {
    // TODO: 调用 API 获取节点事件
    events.value = [
      { type: 'Normal', reason: 'NodeReady', message: 'Node is ready', count: 1, firstTimestamp: new Date().toISOString(), lastTimestamp: new Date().toISOString() },
      { type: 'Warning', reason: 'NodeNotReady', message: 'Node is not ready', count: 3, firstTimestamp: new Date(Date.now() - 3600000).toISOString(), lastTimestamp: new Date(Date.now() - 1800000).toISOString() },
    ]
  } finally {
    eventsLoading.value = false
  }
}

function initCharts() {
  if (cpuTrendChartRef.value) {
    cpuTrendChart = echarts.init(cpuTrendChartRef.value)

    const hours = []
    const data = []
    for (let i = 23; i >= 0; i--) {
      hours.push(`${i}h`)
      data.push(Math.round(Math.random() * 40 + 30))
    }

    cpuTrendChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: hours },
      yAxis: { type: 'value', axisLabel: { formatter: '{value}%' } },
      series: [{
        type: 'line',
        smooth: true,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.5)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' },
          ]),
        },
        lineStyle: { width: 3, color: '#409EFF' },
        data,
      }],
    })
  }

  if (memoryTrendChartRef.value) {
    memoryTrendChart = echarts.init(memoryTrendChartRef.value)

    const hours = []
    const data = []
    for (let i = 23; i >= 0; i--) {
      hours.push(`${i}h`)
      data.push(Math.round(Math.random() * 30 + 40))
    }

    memoryTrendChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: hours },
      yAxis: { type: 'value', axisLabel: { formatter: '{value}%' } },
      series: [{
        type: 'line',
        smooth: true,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(103, 194, 58, 0.5)' },
            { offset: 1, color: 'rgba(103, 194, 58, 0.05)' },
          ]),
        },
        lineStyle: { width: 3, color: '#67C23A' },
        data,
      }],
    })
  }
}

function handleTabChange(tab: string) {
  if (tab === 'overview') {
    setTimeout(() => {
      initCharts()
    }, 100)
  }
}

function handleCordonUncordon() {
  ElMessageBox.confirm(
    `确定要${nodeDetail.value.is_ready ? 'Cordon' : 'Uncordon'}此节点吗？`,
    '确认操作',
    { type: 'warning' }
  ).then(() => {
    ElMessage.success('操作成功')
    fetchNodeDetail()
  }).catch(() => {})
}

function handleDrain() {
  ElMessageBox.confirm(
    '确定要 Drain 此节点吗？此操作将驱逐该节点上的所有 Pod',
    '警告',
    { type: 'error', confirmButtonText: '确认', cancelButtonText: '取消' }
  ).then(() => {
    ElMessage.success('开始 Drain 节点')
  }).catch(() => {})
}

function viewPod(name: string) {
  ElMessage.info(`查看 Pod: ${name}`)
}

watch(() => props.nodeName, () => {
  fetchNodeDetail()
})

onMounted(() => {
  fetchNodeDetail()

  window.addEventListener('resize', () => {
    cpuTrendChart?.resize()
    memoryTrendChart?.resize()
  })
})
</script>

<style scoped lang="scss">
.node-detail {
  .info-card {
    .card-header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      margin-bottom: 20px;

      .header-left {
        display: flex;
        align-items: flex-start;
        gap: 16px;

        .header-icon {
          font-size: 40px;
          color: #409EFF;
        }

        .header-info {
          .node-name {
            font-size: 20px;
            font-weight: 600;
            color: #333;
            margin: 0 0 8px 0;
          }

          .node-status {
            display: flex;
            align-items: center;
            gap: 12px;

            .node-version {
              font-size: 13px;
              color: #888;
            }
          }
        }
      }

      .header-actions {
        display: flex;
        gap: 12px;
      }
    }

    .node-descriptions {
      :deep(.el-descriptions__label) {
        width: 120px;
        font-weight: 500;
      }
    }
  }

  .resource-stat-card {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);

    .resource-icon {
      width: 56px;
      height: 56px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 26px;
      color: #fff;

      &.cpu {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }

      &.memory {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      }

      &.pods {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      }

      &.storage {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
      }
    }

    .resource-info {
      flex: 1;

      .resource-label {
        font-size: 13px;
        color: #888;
        margin-bottom: 6px;
      }

      .resource-value {
        font-size: 22px;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 4px;
      }

      .resource-sub {
        font-size: 12px;
        color: #999;
      }
    }
  }

  .chart-card {
    background: #fff;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);

    .chart-title {
      font-size: 16px;
      font-weight: 600;
      color: #333;
      margin-bottom: 16px;
    }
  }
}
</style>
