# K8s-health-check - 后续开发计划

**当前版本**: v1.1.0  
**最后更新**: 2026-04-06

---

## 当前进度总览

| 阶段 | 状态 | 完成度 |
|------|------|--------|
| 阶段一：基础架构 | ✅ 已完成 | 100% |
| 阶段二：权限管理 | ✅ 已完成 | 100% |
| 阶段三：K8s 资源扩展 | 🔄 待开始 | 0% |
| 阶段四：监控功能 | ⏳ 未开始 | 0% |
| 阶段五：Pod 交互 | ⏳ 未开始 | 0% |
| 阶段六：告警系统 | ⏳ 未开始 | 0% |
| 阶段七：生产部署 | ⏳ 未开始 | 0% |

---

## 阶段三：K8s 资源扩展（详细计划）

### 目标
为以下 K8s 资源添加完整的监控和管理功能：
- Namespace
- Service
- Ingress
- NetworkPolicy
- PersistentVolume (PV)
- PersistentVolumeClaim (PVC)
- StorageClass
- ReplicaSet

### 开发流程（每个资源遵循相同模式）

#### 步骤 1: 创建数据模型 (`backend/app/models/metrics.py`)
```python
# 示例：ServiceMetrics
class ServiceMetrics(BaseModel):
    name: str
    namespace: str
    type: str
    cluster_ip: str
    external_ip: Optional[str]
    ports: List[Dict[str, Any]]
    selector: Optional[Dict[str, str]]
    created_at: str
```

#### 步骤 2: 创建收集器 (`backend/app/collectors/`)
```python
# 示例：backend/app/collectors/service_collector.py
class ServiceCollector(BaseCollector):
    async def collect(self) -> Dict[str, Any]:
        # 使用 kubernetes async client 获取资源
        # 解析数据
        # 返回 Dict
```

#### 步骤 3: 注册到 MetricsService (`backend/app/services/metrics_service.py`)
```python
from app.collectors.service_collector import ServiceCollector

class MetricsService:
    def __init__(self):
        self.service_collector = ServiceCollector()
    
    async def collect_all(self):
        # 添加服务收集器调用
        service_data = await self.service_collector.run()
```

#### 步骤 4: 创建 API 路由 (`backend/app/api/routes/`)
```python
# 示例：backend/app/api/routes/services.py
from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_user

router = APIRouter()

@router.get("/services")
async def list_services(namespace: Optional[str] = None, ...):
    # 从缓存或收集器获取数据
```

#### 步骤 5: 注册路由 (`backend/app/main.py` 和 `backend/app/api/routes/__init__.py`)

#### 步骤 6: 创建前端 API 客户端 (`frontend/src/api/`)
```typescript
// 示例：frontend/src/api/service.ts
export function getServices(params?: { namespace?: string }) {
  return request({ url: '/api/v1/services', method: 'get', params })
}
```

#### 步骤 7: 创建 Pinia Store (`frontend/src/stores/`)
```typescript
// 示例：frontend/src/stores/service.ts
export const useServiceStore = defineStore('service', {
  state: () => ({ services: [] }),
  actions: {
    async fetchServices() { ... }
  }
})
```

#### 步骤 8: 创建/更新前端视图 (`frontend/src/views/`)
- 使用 CommonList.vue 作为基础
- 实现资源特定的列定义和操作按钮

#### 步骤 9: 添加路由 (`frontend/src/router/index.ts`)
- 已在 router 中预注册路径

### 优先级顺序

| 优先级 | 资源 | 原因 |
|--------|------|------|
| P0 | Namespace | 基础资源，其他资源依赖 |
| P0 | Service | 核心网络资源，使用频繁 |
| P1 | ReplicaSet | 工作负载相关，已有前端页面 |
| P1 | Ingress | 入口管理，重要 |
| P2 | PV/PVC | 存储管理，已有前端页面 |
| P2 | StorageClass | 存储类配置，已有前端页面 |
| P3 | NetworkPolicy | 网络策略，安全性相关 |

---

## 阶段四：监控功能

### 目标
- [ ] 资源使用趋势图表（24 小时/7 天/30 天）
- [ ] 历史数据存储到 MySQL
- [ ] 资源预测分析（基于历史数据）

### 开发步骤

#### 1. 历史数据存储
```sql
-- 添加历史指标表
CREATE TABLE node_metrics_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    node_name VARCHAR(255),
    cpu_usage DECIMAL(10,2),
    memory_usage DECIMAL(10,2),
    collected_at TIMESTAMP
);
```

#### 2. 定时任务
```python
# 使用 APScheduler 或 asyncio 定时任务
async def store_historical_metrics():
    # 定期将 Redis 中的指标写入 MySQL
```

#### 3. 前端图表
- 使用 ECharts 时间序列图
- 支持时间范围选择

---

## 阶段五：Pod 交互

### 目标
- [ ] Pod 日志查看（支持多容器）
- [ ] 容器终端（WebSocket exec）
- [ ] Pod 事件流

### 技术要点

#### 日志查看
```python
from kubernetes_asyncio import client

async def get_pod_logs(name, namespace, container=None):
    v1 = client.CoreV1Api()
    logs = await v1.read_namespaced_pod_log(
        name=name,
        namespace=namespace,
        container=container,
        tail_lines=100
    )
```

#### 容器终端
```python
# WebSocket 连接 K8s exec API
# 使用 kubernetes-client 的 stream 功能
# 前端使用 xterm.js 渲染终端
```

---

## 阶段六：告警系统

### 目标
- [ ] 告警规则配置（CPU/内存/磁盘阈值）
- [ ] 告警通知（邮件/钉钉/企业微信）
- [ ] 告警历史记录

### 数据模型
```python
class AlertRule(BaseModel):
    name: str
    resource_type: str  # node/pod/deployment
    metric: str  # cpu/memory
    threshold: float
    operator: str  # gt/lt/eq
    notification_channels: List[str]
```

### 通知渠道
```python
class NotificationChannel:
    EMAIL = "email"
    DINGTALK = "dingtalk"
    WECHAT = "wechat"
```

---

## 阶段七：生产部署

### 目标
- [ ] Docker Compose 完整配置（含监控栈）
- [ ] Kubernetes Helm Chart
- [ ] 性能优化（连接池、缓存策略）
- [ ] 安全加固（HTTPS、RBAC、审计）

### Helm Chart 结构
```
charts/
  k8s-monitor/
    Chart.yaml
    values.yaml
    templates/
      deployment.yaml
      service.yaml
      configmap.yaml
      rbac.yaml
```

---

## 立即行动：阶段三启动清单

### 准备工作
- [ ] 确认 kubernetes-asyncio client 支持所有资源类型
- [ ] 检查前端 UI 组件通用性
- [ ] 准备测试 K8s 集群

### 第一个资源：Namespace

**后端任务：**
- [ ] 在 `models/metrics.py` 添加 `NamespaceMetrics`
- [ ] 创建 `collectors/namespace_collector.py`
- [ ] 在 `MetricsService` 注册
- [ ] 创建 `api/routes/namespaces.py` (已有部分)
- [ ] 在 `main.py` 注册路由

**前端任务：**
- [ ] 创建 `api/namespace.ts`
- [ ] 创建 `stores/namespace.ts`
- [ ] 完善 `views/Namespaces.vue`

---

## 开发规范

### 代码规范
- 后端：遵循 PEP 8，使用 `ruff` 格式化
- 前端：遵循 ESLint 配置，使用 `Prettier`

### 提交规范
```
feat: 添加 Namespace 收集器
fix: 修复 Pod 列表筛选问题
docs: 更新 API 文档
refactor: 重构收集器基类
```

### 测试要求
- 后端：每个收集器至少一个单元测试
- 前端：关键组件快照测试

---

## 预计时间表

| 阶段 | 预计开始 | 预计完成 | 周期 |
|------|----------|----------|------|
| 阶段三 | 2026-04-07 | 2026-04-14 | 1 周 |
| 阶段四 | 2026-04-15 | 2026-04-21 | 1 周 |
| 阶段五 | 2026-04-22 | 2026-04-30 | 1.5 周 |
| 阶段六 | 2026-05-01 | 2026-05-15 | 2 周 |
| 阶段七 | 2026-05-16 | 2026-05-31 | 2 周 |

---

## 风险与依赖

### 风险
1. **K8s API 兼容性** - 不同版本 K8s API 可能存在差异
2. **性能问题** - 大量资源时收集器可能变慢
3. **前端复杂度** - 资源类型增多后 UI 可能变得复杂

### 缓解措施
1. 使用 kubernetes-asyncio 官方客户端，保持版本兼容
2. 优化收集器使用并发收集，添加分页支持
3. 提前设计好通用列表组件，减少重复代码

---

**文档维护**: 请在完成每个任务后更新此文档和 `IMPLEMENTATION_STATUS.md`
