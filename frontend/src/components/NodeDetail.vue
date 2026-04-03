<template>
  <el-dialog :model-value="modelValue" @update:model-value="handleClose" title="节点详情" width="800px">
    <div v-if="node" class="node-detail">
      <el-descriptions title="基本信息" :column="2" border>
        <el-descriptions-item label="名称">{{ node.name }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="node.is_ready ? 'success' : 'danger'">
            {{ node.is_ready ? 'Ready' : 'NotReady' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Kubelet 版本">{{ node.kubelet_version }}</el-descriptions-item>
        <el-descriptions-item label="操作系统">{{ node.os_image }}</el-descriptions-item>
        <el-descriptions-item label="容器运行时">{{ node.container_runtime }}</el-descriptions-item>
        <el-descriptions-item label="Internal IP">{{ node.addresses?.InternalIP || '-' }}</el-descriptions-item>
      </el-descriptions>

      <h3 style="margin-top: 20px">资源容量</h3>
      <el-table :data="resourceData" style="width: 100%">
        <el-table-column prop="type" label="类型" />
        <el-table-column prop="capacity" label="容量" />
        <el-table-column prop="allocatable" label="可分配" />
      </el-table>

      <h3 style="margin-top: 20px">条件状态</h3>
      <el-table :data="conditionData" style="width: 100%">
        <el-table-column prop="type" label="条件" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === 'True' ? 'success' : 'danger'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="原因" />
        <el-table-column prop="message" label="消息" show-overflow-tooltip />
      </el-table>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { formatCPU, formatBytes } from '@/utils'

const props = defineProps<{
  modelValue: boolean
  node: any
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

const resourceData = computed(() => {
  if (!props.node) return []
  return [
    {
      type: 'CPU',
      capacity: formatCPU(props.node.capacity?.cpu || 0),
      allocatable: formatCPU(props.node.allocatable?.cpu || 0),
    },
    {
      type: '内存',
      capacity: formatBytes(props.node.capacity?.memory_bytes || 0),
      allocatable: formatBytes(props.node.allocatable?.memory_bytes || 0),
    },
    {
      type: 'Pod 数量',
      capacity: props.node.capacity?.pods || 0,
      allocatable: props.node.allocatable?.pods || 0,
    },
  ]
})

const conditionData = computed(() => {
  if (!props.node?.conditions) return []
  return Object.entries(props.node.conditions).map(([type, info]: any) => ({
    type,
    status: info.status,
    reason: info.reason || '-',
    message: info.message || '-',
  }))
})

function handleClose() {
  emit('update:modelValue', false)
}
</script>

<style scoped>
.node-detail {
  max-height: 600px;
  overflow-y: auto;
}
</style>
