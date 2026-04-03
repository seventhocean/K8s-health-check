/** 格式化字节数 */
export function formatBytes(bytes: number): string {
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let unitIndex = 0
  let value = bytes

  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024
    unitIndex++
  }

  return `${value.toFixed(2)} ${units[unitIndex]}`
}

/** 格式化 CPU (millicores) */
export function formatCPU(millicores: number): string {
  if (millicores >= 1000) {
    return `${(millicores / 1000).toFixed(2)} cores`
  }
  return `${millicores.toFixed(0)}m`
}

/** 格式化百分比 */
export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`
}

/** 格式化时间 */
export function formatTime(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleString('zh-CN')
}

/** 格式化相对时间 */
export function formatRelativeTime(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date
  const now = new Date()
  const diff = now.getTime() - d.getTime()

  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 60) return `${minutes} 分钟前`
  if (hours < 24) return `${hours} 小时前`
  return `${days} 天前`
}

/** 获取状态颜色 */
export function getStatusColor(status: string): string {
  const colorMap: Record<string, string> = {
    'Ready': 'var(--el-color-success)',
    'True': 'var(--el-color-success)',
    'Running': 'var(--el-color-success)',
    'Succeeded': 'var(--el-color-success)',
    'False': 'var(--el-color-danger)',
    'NotReady': 'var(--el-color-danger)',
    'Failed': 'var(--el-color-danger)',
    'Error': 'var(--el-color-danger)',
    'Pending': 'var(--el-color-warning)',
    'Unknown': 'var(--el-color-info)',
  }
  return colorMap[status] || 'var(--el-color-info)'
}
