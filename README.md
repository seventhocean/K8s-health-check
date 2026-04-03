# K8s Health Check

Kubernetes 集群监控系统，提供节点、Pod、Deployment 等资源的健康状态监控和可视化展示。

## 功能特性

- **节点监控**: 实时监控 K8s 节点状态、资源容量、健康条件
- **Pod 监控**: 查看所有 Pod 状态、重启次数、资源使用
- **Deployment 监控**: 追踪部署状态、副本数、滚动更新进度
- **集群概览**: 仪表盘展示集群整体健康状况
- **实时推送**: WebSocket 实时推送指标更新
- **数据持久化**: MySQL 存储历史数据，Redis 缓存加速访问

## 技术架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Vue 3     │────▶│  FastAPI    │────▶│   K8s API   │
│  Frontend   │◀────│   Backend   │◀────│   Server    │
└─────────────┘     └─────────────┘     └─────────────┘
                          │
                   ┌──────┴──────┐
                   ▼             ▼
              ┌─────────┐  ┌─────────┐
              │  MySQL  │  │  Redis  │
              └─────────┘  └─────────┘
```

## 快速开始

### 本地开发

1. **克隆项目**
```bash
git clone <repository>
cd K8s-health-check
```

2. **安装依赖**
```bash
make install
```

3. **配置环境变量**
```bash
cp backend/.env.example backend/.env
# 编辑 backend/.env 配置 K8s API Server 地址
```

4. **启动服务**
```bash
# 方式一：使用 docker-compose (推荐)
docker-compose up -d

# 方式二：分别启动前后端
make dev          # 后端
make dev-frontend # 前端
```

5. **访问应用**
- 前端：http://localhost:80
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

### K8s 集群部署

1. **构建镜像**
```bash
make build
```

2. **推送镜像到仓库** (如果需要)
```bash
docker tag k8s-monitor-backend:latest <your-registry>/k8s-monitor-backend:latest
docker tag k8s-monitor-frontend:latest <your-registry>/k8s-monitor-frontend:latest
docker push <your-registry>/k8s-monitor-backend:latest
docker push <your-registry>/k8s-monitor-frontend:latest
```

3. **部署到 K8s**
```bash
kubectl apply -f deploy/k8s/manifests.yml
```

4. **访问服务**
- NodePort: http://<node-ip>:30080

## 项目结构

```
K8s-health-check/
├── backend/
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── collectors/     # 数据采集器
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务服务
│   │   └── utils/          # 工具函数
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/            # API 客户端
│   │   ├── components/     # 组件
│   │   ├── stores/         # Pinia 状态管理
│   │   ├── views/          # 页面视图
│   │   └── router/         # 路由配置
│   ├── package.json
│   └── Dockerfile
├── deploy/
│   ├── k8s/                # K8s 部署文件
│   └── mysql/              # MySQL 初始化脚本
├── docker-compose.yml
└── Makefile
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/nodes` | 获取节点列表 |
| GET | `/api/v1/nodes/{name}` | 获取单个节点 |
| GET | `/api/v1/pods` | 获取 Pod 列表 |
| GET | `/api/v1/deployments` | 获取 Deployment 列表 |
| GET | `/api/v1/cluster/summary` | 获取集群概览 |
| WS | `/ws/metrics` | WebSocket 实时推送 |

## 监控维度

### 节点层面
- CPU/内存容量和可分配量
- Pod 容量
- 节点健康状态 (Ready/NotReady)
- Kubelet 版本、操作系统信息

### K8s 资源层面
- Pod 状态分布 (Running/Pending/Failed)
- Deployment 副本状态
- 命名空间资源统计

## 扩展开发

### 添加新的 Collector

1. 继承 `BaseCollector` 类
2. 实现 `collect()` 方法
3. 在 `MetricsService` 中注册

```python
from app.collectors.base import BaseCollector

class MyCollector(BaseCollector):
    async def collect(self) -> Dict[str, Any]:
        # 实现数据采集逻辑
        pass
```

## 常见问题

### Q: 如何配置 K8s API Server 地址？
编辑 `backend/.env` 文件，设置 `K8S_APISERVER_URL`。

### Q: 本地开发如何连接 K8s 集群？
确保本地 `~/.kube/config` 配置正确，后端会自动加载 kubeconfig。

### Q: 如何修改数据采集间隔？
修改 `backend/.env` 中的 `COLLECTOR_INTERVAL` (秒)。

## License

MIT
