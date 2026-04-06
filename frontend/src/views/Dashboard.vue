<template>
  <div class="dashboard-page">
    <div class="page-header">
      <h1 class="page-title">Dashboard</h1>
      <div class="header-actions">
        <el-button @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-dropdown @command="handleTimeRange">
          <el-button>
            {{ timeRangeLabel }}
            <el-icon><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="1h">最近 1 小时</el-dropdown-item>
              <el-dropdown-item command="6h">最近 6 小时</el-dropdown-item>
              <el-dropdown-item command="24h">最近 24 小时</el-dropdown-item>
              <el-dropdown-item command="7d">最近 7 天</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <div v-loading="loading" class="dashboard-content">
      <!-- 统计卡片 - 4 列网格 -->
      <el-row :gutter="20" class="stat-cards-row">
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-icon nodes">
                <el-icon><Cpu /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-label">节点总数</div>
                <div class="stat-value">{{ summary.nodes.total || 0 }}</div>
                <div class="stat-sub">
                  <el-tag :type="summary.nodes.ready > 0 ? 'success' : 'danger'" size="small">
                    就绪：{{ summary.nodes.ready || 0 }}
                  </el-tag>
                </div>
              </div>
            </div>
            <div class="stat-trend">
              <span :class="trendClass(summary.nodes.trend)">
                <el-icon v-if="summary.nodes.trend > 0"><Top /></el-icon>
                <el-icon v-else-if="summary.nodes.trend < 0"><Bottom /></el-icon>
                {{ Math.abs(summary.nodes.trend || 0) }}%
              </span>
              <span class="trend-label">较上周</span>
            </div>
          </div>
        </el-col>

        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-icon pods">
                <el-icon><Box /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-label">Pod 总数</div>
                <div class="stat-value">{{ summary.pods.total || 0 }}</div>
                <div class="stat-sub">
                  <el-tag type="success" size="small">
                    运行：{{ summary.pods.by_phase?.Running || 0 }}
                  </el-tag>
                </div>
              </div>
            </div>
            <div class="stat-trend">
              <span :class="trendClass(summary.pods.trend)">
                <el-icon v-if="summary.pods.trend > 0"><Top /></el-icon>
                <el-icon v-else-if="summary.pods.trend < 0"><Bottom /></el-icon>
                {{ Math.abs(summary.pods.trend || 0) }}%
              </span>
              <span class="trend-label">较上周</span>
            </div>
          </div>
        </el-col>

        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-icon deployments">
                <el-icon><SetUp /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-label">工作负载</div>
                <div class="stat-value">{{ summary.deployments.total || 0 }}</div>
                <div class="stat-sub">
                  <el-tag type="success" size="small">
                    就绪：{{ summary.deployments.ready || 0 }}
                  </el-tag>
                </div>
              </div>
            </div>
            <div class="stat-trend">
              <span :class="trendClass(summary.deployments.trend)">
                <el-icon v-if="summary.deployments.trend > 0"><Top /></el-icon>
                <el-icon v-else-if="summary.deployments.trend < 0"><Bottom /></el-icon>
                {{ Math.abs(summary.deployments.trend || 0) }}%
              </span>
              <span class="trend-label">较上周</span>
            </div>
          </div>
        </el-col>

        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-icon namespaces">
                <el-icon><Grid /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-label">命名空间</div>
                <div class="stat-value">{{ namespaceCount }}</div>
                <div class="stat-sub">
                  <el-tag type="success" size="small">活跃</el-tag>
                </div>
              </div>
            </div>
            <div class="stat-trend">
              <span class="trend-stable">
                <el-icon><Minus /></el-icon>
                0%
              </span>
              <span class="trend-label">较上周</span>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 资源使用率卡片 -->
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="6">
          <div class="stat-card resource-card">
            <div class="card-header">
              <span class="card-title">CPU 使用率</span>
              <el-tag :type="cpuUsageType" size="small">{{ cpuUsagePercent }}%</el-tag>
            </div>
            <div class="resource-chart" ref="cpuGaugeRef"></div>
          </div>
        </el-col>

        <el-col :span="6">
          <div class="stat-card resource-card">
            <div class="card-header">
              <span class="card-title">内存使用率</span>
              <el-tag :type="memoryUsageType" size="small">{{ memoryUsagePercent }}%</el-tag>
            </div>
            <div class="resource-chart" ref="memoryGaugeRef"></div>
          </div>
        </el-col>

        <el-col :span="6">
          <div class="stat-card resource-card">
            <div class="card-header">
              <span class="card-title">存储使用率</span>
              <el-tag :type="storageUsageType" size="small">{{ storageUsagePercent }}%</el-tag>
            </div>
            <div class="resource-chart" ref="storageGaugeRef"></div>
          </div>
        </el-col>

        <el-col :span="6">
          <div class="stat-card resource-card">
            <div class="card-header">
              <span class="card-title">Pod 使用率</span>
              <el-tag :type="podUsageType" size="small">{{ podUsagePercent }}%</el-tag>
            </div>
            <div class="resource-chart" ref="podGaugeRef"></div>
          </div>
        </el-col>
      </el-row>

      <!-- 图表行 -->
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header-title">
                <span>资源趋势</span>
                <el-radio-group v-model="resourceTrendType" size="small" @change="updateResourceTrendChart">
                  <el-radio-button label="cpu">CPU</el-radio-button>
                  <el-radio-button label="memory">内存</el-radio-button>
                </el-radio-group>
              </div>
            </template>
            <div ref="resourceTrendChartRef" style="height: 300px"></div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header-title">
                <span>Pod 状态分布</span>
              </div>
            </template>
            <div ref="podStatusChartRef" style="height: 300px"></div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 告警列表和命名空间 -->
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="16">
          <el-card>
            <template #header>
              <div class="card-header-title">
                <span>告警列表</span>
                <el-button link type="primary" @click="viewAllAlerts">
                  查看全部
                  <el-icon><ArrowRight /></el-icon>
                </el-button>
              </div>
            </template>
            <div class="alert-list">
              <div v-for="(alert, index) in alerts" :key="index" class="alert-item" :class="alert.level">
                <div class="alert-icon">
                  <el-icon v-if="alert.level === 'critical'"><CircleClose /></el-icon>
                  <el-icon v-else-if="alert.level === 'warning'"><Warning /></el-icon>
                  <el-icon v-else><InfoFilled /></el-icon>
                </div>
                <div class="alert-content">
                  <div class="alert-title">{{ alert.title }}</div>
                  <div class="alert-desc">{{ alert.description }}</div>
                </div>
                <div class="alert-meta">
                  <div class="alert-time">{{ alert.time }}</div>
                  <el-button link type="primary" @click="handleAlertAction(alert)">
                    处理
                  </el-button>
                </div>
              </div>
              <div v-if="alerts.length === 0" class="empty-state">
                <el-icon style="font-size: 48px; color: #67C23A"><CircleCheck /></el-icon>
                <p>暂无告警</p>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card>
            <template #header>
              <div class="card-header-title">
                <span>命名空间资源</span>
              </div>
            </template>
            <div class="namespace-list">
              <div v-for="ns in namespaces" :key="ns.name" class="namespace-item">
                <div class="namespace-info">
                  <span class="namespace-name">{{ ns.name }}</span>
                  <el-tag size="small" type="info">{{ ns.pods }} Pods</el-tag>
                </div>
                <div class="namespace-resources">
                  <div class="resource-bar">
                    <el-progress
                      :percentage="ns.cpuUsage"
                      :stroke-width="6"
                      :show-text="false"
                      :color="getProgressColor(ns.cpuUsage)"
                    />
                  </div>
                  <div class="resource-bar">
                    <el-progress
                      :percentage="ns.memoryUsage"
                      :stroke-width="6"
                      :show-text="false"
                      :color="getProgressColor(ns.memoryUsage)"
                    />
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  Cpu,
  Box,
  SetUp,
  Grid,
  Refresh,
  ArrowDown,
  ArrowRight,
  Top,
  Bottom,
  Minus,
  CircleClose,
  Warning,
  InfoFilled,
  CircleCheck,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'
import { useClusterStore } from '@/stores/cluster'
import { clusterApi } from '@/api/cluster'

const clusterStore = useClusterStore()

const loading = ref(false)
const summary = ref<any>({
  nodes: { total: 0, ready: 0, trend: 0 },
  pods: { total: 0, by_phase: {}, trend: 0 },
  deployments: { total: 0, ready: 0, trend: 0 },
  resources: {},
})

const timeRangeLabel = ref('最近 24 小时')
const resourceTrendType = ref('cpu')

// 图表引用
const cpuGaugeRef = ref<HTMLElement>()
const memoryGaugeRef = ref<HTMLElement>()
const storageGaugeRef = ref<HTMLElement>()
const podGaugeRef = ref<HTMLElement>()
const resourceTrendChartRef = ref<HTMLElement>()
const podStatusChartRef = ref<HTMLElement>()

let cpuGauge: ECharts | null = null
let memoryGauge: ECharts | null = null
let storageGauge: ECharts | null = null
let podGauge: ECharts | null = null
let resourceTrendChart: ECharts | null = null
let podStatusChart: ECharts | null = null

// 告警数据
const alerts = ref([
  {
    level: 'critical',
    title: '节点 node-3 磁盘空间不足',
    description: '磁盘使用率已达 95%，剩余空间不足 10GB',
    time: '5 分钟前',
  },
  {
    level: 'warning',
    title: '节点 node-1 CPU 使用率过高',
    description: 'CPU 使用率持续超过 90% 达 10 分钟',
    time: '10 分钟前',
  },
  {
    level: 'warning',
    title: 'Pod 重启次数过多',
    description: 'nginx-deployment-7d8f9b 在 1 小时内重启 5 次',
    time: '30 分钟前',
  },
])

// 命名空间数据
const namespaces = ref([
  { name: 'default', pods: 12, cpuUsage: 45, memoryUsage: 62 },
  { name: 'kube-system', pods: 25, cpuUsage: 78, memoryUsage: 85 },
  { name: 'monitoring', pods: 8, cpuUsage: 35, memoryUsage: 42 },
  { name: 'production', pods: 45, cpuUsage: 82, memoryUsage: 75 },
  { name: 'staging', pods: 18, cpuUsage: 25, memoryUsage: 30 },
])

// 计算属性
const namespaceCount = computed(() => namespaces.value.length)

const cpuUsagePercent = computed(() => {
  const total = summary.value.resources?.total_cpu_capacity_millicores || 0
  const used = summary.value.resources?.total_cpu_requested_millicores || 0
  return total > 0 ? Math.round((used / total) * 100) : 0
})

const memoryUsagePercent = computed(() => {
  const total = summary.value.resources?.total_memory_capacity_bytes || 0
  const used = summary.value.resources?.total_memory_requested_bytes || 0
  return total > 0 ? Math.round((used / total) * 100) : 0
})

const storageUsagePercent = computed(() => {
  const total = summary.value.resources?.total_storage_capacity_bytes || 0
  const used = summary.value.resources?.total_storage_used_bytes || 0
  return total > 0 ? Math.round((used / total) * 100) : 0
})

const podUsagePercent = computed(() => {
  const total = summary.value.resources?.total_pods_capacity || 0
  const used = summary.value.resources?.total_pods_requested || 0
  return total > 0 ? Math.round((used / total) * 100) : 0
})

const cpuUsageType = computed(() => getUsageType(cpuUsagePercent.value))
const memoryUsageType = computed(() => getUsageType(memoryUsagePercent.value))
const storageUsageType = computed(() => getUsageType(storageUsagePercent.value))
const podUsageType = computed(() => getUsageType(podUsagePercent.value))

function getUsageType(percent: number): 'success' | 'warning' | 'danger' {
  if (percent >= 80) return 'danger'
  if (percent >= 60) return 'warning'
  return 'success'
}

function trendClass(trend: number): string {
  if (trend > 0) return 'trend-up'
  if (trend < 0) return 'trend-down'
  return 'trend-stable'
}

function getProgressColor(percent: number): string {
  if (percent >= 80) return '#F56C6C'
  if (percent >= 60) return '#E6A23C'
  return '#67C23A'
}

// 初始化图表
function initGaugeChart(container: HTMLElement | undefined, value: number, color: string): ECharts {
  const chart = echarts.init(container)
  chart.setOption({
    series: [
      {
        type: 'gauge',
        progress: {
          show: true,
          width: 18,
          itemStyle: {
            color: color,
          },
        },
        axisLine: {
          lineStyle: {
            width: 18,
          },
        },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        pointer: {
          show: false,
        },
        anchor: { show: false },
        title: { show: false },
        detail: {
          valueAnimation: true,
          offsetCenter: [0, '0%'],
          fontSize: 24,
          fontWeight: 'bold',
          color: '#333',
          formatter: '{value}%',
        },
        data: [{ value: value.toFixed(1) }],
      },
    ],
  })
  return chart
}

function initResourceTrendChart() {
  if (!resourceTrendChartRef.value) return
  resourceTrendChart = echarts.init(resourceTrendChartRef.value)

  const hours = []
  const data1 = []
  const data2 = []
  for (let i = 23; i >= 0; i--) {
    const hour = new Date(Date.now() - i * 3600000)
    hours.push(`${hour.getHours()}:00`)
    data1.push(Math.round(Math.random() * 40 + 30))
    data2.push(Math.round(Math.random() * 30 + 20))
  }

  const option = {
    tooltip: {
      trigger: 'axis',
    },
    legend: {
      data: ['CPU 使用率', '内存使用率'],
      bottom: 10,
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: hours,
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLabel: {
        formatter: '{value}%',
      },
    },
    series: [
      {
        name: 'CPU 使用率',
        type: 'line',
        smooth: true,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.5)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' },
          ]),
        },
        lineStyle: {
          width: 3,
          color: '#409EFF',
        },
        data: data1,
      },
      {
        name: '内存使用率',
        type: 'line',
        smooth: true,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(103, 194, 58, 0.5)' },
            { offset: 1, color: 'rgba(103, 194, 58, 0.05)' },
          ]),
        },
        lineStyle: {
          width: 3,
          color: '#67C23A',
        },
        data: data2,
      },
    ],
  }

  resourceTrendChart.setOption(option)
}

function initPodStatusChart() {
  if (!podStatusChartRef.value) return
  podStatusChart = echarts.init(podStatusChartRef.value)

  const phases = summary.value.pods.by_phase || {}
  const data = Object.entries(phases).map(([key, value]) => ({
    name: key,
    value,
  }))

  const colors = ['#67C23A', '#F56C6C', '#E6A23C', '#909399', '#409EFF']

  podStatusChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
    },
    legend: {
      orient: 'vertical',
      left: 'left',
    },
    color: colors,
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['60%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2,
        },
        label: {
          show: false,
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold',
          },
        },
        data: data.length > 0 ? data : [{ name: '无数据', value: 1 }],
      },
    ],
  })
}

function updateResourceTrendChart() {
  if (!resourceTrendChart) return

  // 根据类型更新图表
  // TODO: 根据 resourceTrendType 获取不同数据
}

// 处理方法
async function handleRefresh() {
  loading.value = true
  try {
    await clusterStore.fetchSummary()
    const data = await clusterApi.getSummary()
    summary.value = data

    // 更新仪表图
    setTimeout(() => {
      cpuGauge?.setOption({ series: [{ data: [{ value: cpuUsagePercent.value }] }] })
      memoryGauge?.setOption({ series: [{ data: [{ value: memoryUsagePercent.value }] }] })
      storageGauge?.setOption({ series: [{ data: [{ value: storageUsagePercent.value }] }] })
      podGauge?.setOption({ series: [{ data: [{ value: podUsagePercent.value }] }] })
      initPodStatusChart()
    }, 100)

    ElMessage.success('数据已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    loading.value = false
  }
}

function handleTimeRange(command: string) {
  const labels: Record<string, string> = {
    '1h': '最近 1 小时',
    '6h': '最近 6 小时',
    '24h': '最近 24 小时',
    '7d': '最近 7 天',
  }
  timeRangeLabel.value = labels[command]
  // TODO: 根据时间范围更新数据
}

function viewAllAlerts() {
  // TODO: 跳转到告警页面
  ElMessage.info('告警列表功能开发中')
}

function handleAlertAction(alert: any) {
  // TODO: 处理告警
  ElMessage.info(`处理告警：${alert.title}`)
}

onMounted(async () => {
  loading.value = true
  try {
    await clusterStore.fetchSummary()
    summary.value = clusterStore.summary || {}

    // 初始化图表
    if (cpuGaugeRef.value) cpuGauge = initGaugeChart(cpuGaugeRef.value, cpuUsagePercent.value, '#409EFF')
    if (memoryGaugeRef.value) memoryGauge = initGaugeChart(memoryGaugeRef.value, memoryUsagePercent.value, '#67C23A')
    if (storageGaugeRef.value) storageGauge = initGaugeChart(storageGaugeRef.value, storageUsagePercent.value, '#E6A23C')
    if (podGaugeRef.value) podGauge = initGaugeChart(podGaugeRef.value, podUsagePercent.value, '#909399')

    initResourceTrendChart()
    initPodStatusChart()

    window.addEventListener('resize', () => {
      cpuGauge?.resize()
      memoryGauge?.resize()
      storageGauge?.resize()
      podGauge?.resize()
      resourceTrendChart?.resize()
      podStatusChart?.resize()
    })
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  cpuGauge?.dispose()
  memoryGauge?.dispose()
  storageGauge?.dispose()
  podGauge?.dispose()
  resourceTrendChart?.dispose()
  podStatusChart?.dispose()
})
</script>

<style scoped lang="scss">
.dashboard-page {
  padding: 20px;
}

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

.dashboard-content {
  .stat-cards-row {
    .stat-card {
      background: #fff;
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
      transition: all 0.3s ease;

      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
      }

      .stat-content {
        display: flex;
        align-items: flex-start;
        gap: 16px;
        margin-bottom: 16px;
      }

      .stat-icon {
        width: 56px;
        height: 56px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 26px;
        color: #fff;
        flex-shrink: 0;

        &.nodes {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        &.pods {
          background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }

        &.deployments {
          background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }

        &.namespaces {
          background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }
      }

      .stat-info {
        flex: 1;

        .stat-label {
          font-size: 13px;
          color: #888;
          margin-bottom: 6px;
        }

        .stat-value {
          font-size: 28px;
          font-weight: 700;
          color: #1a1a1a;
          margin-bottom: 8px;
        }
      }

      .stat-trend {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 13px;
        padding-top: 8px;
        border-top: 1px solid #f0f0f0;

        span:first-child {
          display: flex;
          align-items: center;
          gap: 2px;
          font-weight: 500;

          &.trend-up {
            color: #f56c6c;
          }

          &.trend-down {
            color: #67c23a;
          }

          &.trend-stable {
            color: #909399;
          }
        }

        .trend-label {
          color: #999;
        }
      }
    }

    .resource-card {
      .card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;

        .card-title {
          font-size: 14px;
          font-weight: 600;
          color: #666;
        }
      }

      .resource-chart {
        height: 120px;
      }
    }
  }

  .card-header-title {
    display: flex;
    align-items: center;
    justify-content: space-between;

    span:first-child {
      font-weight: 600;
      font-size: 15px;
    }
  }

  .alert-list {
    .alert-item {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      padding: 12px;
      border-radius: 8px;
      margin-bottom: 8px;

      &.critical {
        background: #fef0f0;
      }

      &.warning {
        background: #fdf6ec;
      }

      &.info {
        background: #ecf5ff;
      }

      .alert-icon {
        font-size: 20px;
        flex-shrink: 0;

        .el-icon {
          color: inherit;
        }
      }

      &.critical {
        .alert-icon {
          color: #f56c6c;
        }
      }

      &.warning {
        .alert-icon {
          color: #e6a23c;
        }
      }

      &.info {
        .alert-icon {
          color: #409eff;
        }
      }

      .alert-content {
        flex: 1;

        .alert-title {
          font-size: 14px;
          font-weight: 500;
          color: #333;
          margin-bottom: 4px;
        }

        .alert-desc {
          font-size: 13px;
          color: #666;
        }
      }

      .alert-meta {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 4px;

        .alert-time {
          font-size: 12px;
          color: #999;
        }
      }
    }

    .empty-state {
      text-align: center;
      padding: 40px 20px;

      p {
        margin-top: 12px;
        color: #666;
      }
    }
  }

  .namespace-list {
    .namespace-item {
      padding: 12px 0;
      border-bottom: 1px solid #f0f0f0;

      &:last-child {
        border-bottom: none;
      }

      .namespace-info {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 8px;

        .namespace-name {
          font-weight: 500;
          color: #333;
        }
      }

      .namespace-resources {
        display: flex;
        flex-direction: column;
        gap: 6px;

        .resource-bar {
          display: flex;
          align-items: center;
          gap: 8px;
        }
      }
    }
  }
}

:deep(.el-card) {
  border: none;
  border-radius: 12px;
}
</style>
