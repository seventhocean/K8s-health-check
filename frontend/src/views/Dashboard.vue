<template>
  <div class="dashboard">
    <h1 class="page-title">集群概览</h1>

    <div v-loading="loading" class="content">
      <!-- 概览卡片 -->
      <el-row :gutter="20" class="summary-cards">
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="card-content">
              <div class="card-icon nodes">
                <el-icon><Cpu /></el-icon>
              </div>
              <div class="card-info">
                <div class="label">节点</div>
                <div class="value">
                  {{ summary?.nodes.total || 0 }}
                  <span class="sub">就绪：{{ summary?.nodes.ready || 0 }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card shadow="hover">
            <div class="card-content">
              <div class="card-icon pods">
                <el-icon><Box /></el-icon>
              </div>
              <div class="card-info">
                <div class="label">Pods</div>
                <div class="value">
                  {{ summary?.pods.total || 0 }}
                  <span class="sub">运行：{{ summary?.pods.by_phase?.Running || 0 }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card shadow="hover">
            <div class="card-content">
              <div class="card-icon deployments">
                <el-icon><SetUp /></el-icon>
              </div>
              <div class="card-info">
                <div class="label">Deployments</div>
                <div class="value">
                  {{ summary?.deployments.total || 0 }}
                  <span class="sub">就绪：{{ summary?.deployments.ready || 0 }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card shadow="hover">
            <div class="card-content">
              <div class="card-icon namespaces">
                <el-icon><Folder /></el-icon>
              </div>
              <div class="card-info">
                <div class="label">命名空间</div>
                <div class="value">
                  {{ namespaceCount }}
                  <span class="sub">活跃</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 资源使用图表 -->
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>Pod 状态分布</span>
            </template>
            <div ref="podChartRef" style="height: 300px"></div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card>
            <template #header>
              <span>资源容量</span>
            </template>
            <div ref="resourceChartRef" style="height: 300px"></div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 命名空间列表 -->
      <el-card style="margin-top: 20px">
        <template #header>
          <span>命名空间</span>
        </template>
        <el-table :data="namespaces" style="width: 100%">
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="pods" label="Pods" />
          <el-table-column prop="deployments" label="Deployments" />
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Cpu, Box, SetUp, Folder } from '@element-plus/icons-vue'
import { useClusterStore } from '@/stores/cluster'
import { clusterApi } from '@/api/cluster'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'

const clusterStore = useClusterStore()
const summary = computed(() => clusterStore.summary)
const loading = computed(() => clusterStore.loading)

const podChartRef = ref<HTMLElement>()
const resourceChartRef = ref<HTMLElement>()
let podChart: ECharts | null = null
let resourceChart: ECharts | null = null

const namespaceCount = computed(() => {
  return Object.keys(summary.value?.resources || {}).length
})

const namespaces = ref<any[]>([])

async function fetchNamespaces() {
  try {
    const data = await clusterApi.getNamespaces()
    namespaces.value = Object.entries(data.details || {}).map(([name, info]: any) => ({
      name,
      pods: info.pods,
      deployments: info.deployments,
    }))
  } catch (error) {
    console.error('Failed to fetch namespaces:', error)
  }
}

function initCharts() {
  if (podChartRef.value) {
    podChart = echarts.init(podChartRef.value)
  }
  if (resourceChartRef.value) {
    resourceChart = echarts.init(resourceChartRef.value)
  }
}

function updatePodChart() {
  if (!podChart || !summary.value) return

  const phases = summary.value.pods.by_phase || {}
  const data = Object.entries(phases).map(([key, value]) => ({
    name: key,
    value,
  }))

  podChart.setOption({
    tooltip: {
      trigger: 'item',
    },
    legend: {
      orient: 'vertical',
      left: 'left',
    },
    series: [
      {
        type: 'pie',
        radius: '50%',
        data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
      },
    ],
  })
}

function updateResourceChart() {
  if (!resourceChart || !summary.value) return

  const cpuCapacity = (summary.value.resources.total_cpu_capacity_millicores || 0) / 1000
  const cpuAllocatable = (summary.value.resources.total_cpu_allocatable_millicores || 0) / 1000
  const cpuRequested = (summary.value.resources.total_cpu_requested_millicores || 0) / 1000
  const cpuAvailable = (summary.value.resources.total_cpu_available_millicores || 0) / 1000

  const memoryCapacity = (summary.value.resources.total_memory_capacity_bytes || 0) / (1024 ** 3)
  const memoryAllocatable = (summary.value.resources.total_memory_allocatable_bytes || 0) / (1024 ** 3)
  const memoryRequested = (summary.value.resources.total_memory_requested_bytes || 0) / (1024 ** 3)
  const memoryAvailable = (summary.value.resources.total_memory_available_bytes || 0) / (1024 ** 3)

  resourceChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
    },
    legend: {
      data: ['容量', '可分配', '已分配', '可用'],
    },
    xAxis: {
      type: 'category',
      data: ['CPU (cores)', 'Memory (GB)'],
    },
    yAxis: {
      type: 'value',
    },
    series: [
      {
        name: '容量',
        type: 'bar',
        data: [cpuCapacity, memoryCapacity],
      },
      {
        name: '可分配',
        type: 'bar',
        data: [cpuAllocatable, memoryAllocatable],
      },
      {
        name: '已分配',
        type: 'bar',
        data: [cpuRequested, memoryRequested],
      },
      {
        name: '可用',
        type: 'bar',
        data: [cpuAvailable, memoryAvailable],
      },
    ],
  })
}

watch(summary, () => {
  updatePodChart()
  updateResourceChart()
})

onMounted(async () => {
  await clusterStore.fetchSummary()
  await fetchNamespaces()
  initCharts()
  updatePodChart()
  updateResourceChart()

  window.addEventListener('resize', () => {
    podChart?.resize()
    resourceChart?.resize()
  })
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #333;
}

.content {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
}

.summary-cards .card-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.card-icon {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #fff;
}

.card-icon.nodes {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.card-icon.pods {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.card-icon.deployments {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.card-icon.namespaces {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.card-info .label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.card-info .value {
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.card-info .value .sub {
  font-size: 12px;
  font-weight: normal;
  color: #999;
  margin-left: 8px;
}

.el-card {
  border: none;
}
</style>
