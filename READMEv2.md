# K8s 集群监控管理平台

> Kubernetes 集群监控与管理系统 - 提供实时监控、资源管理、用户认证和告警通知功能

## 📋 目录

- [功能特性](#-功能特性)
- [技术栈](#-技术栈)
- [快速开始](#-快速开始)
- [API 接口](#-api-接口)
- [前端页面](#-前端页面)
- [用户认证](#-用户认证)
- [配置文件](#-配置文件)
- [部署指南](#-部署指南)
- [开发指南](#-开发指南)

---

## ✨ 功能特性

### 监控告警
- 📊 **实时集群概览** - CPU/内存/存储/Pod 使用率仪表图
- 📈 **资源趋势图表** - 24 小时资源使用趋势（ECharts 可视化）
- 🔔 **告警列表** - 实时告警展示与处理
- 📋 **命名空间资源** - 各命名空间资源使用配额与统计

### 资源管理
- 🖥️ **节点管理** - 节点列表/详情、Cordon/Uncordon/Drain 操作
- 📦 **Pod 管理** - Pod 列表/详情、日志查看、批量操作
- 🚀 **工作负载** - Deployment 管理、扩缩容、重启、回滚
- 🔗 **网络资源** - Service/Ingress/NetworkPolicy 管理
- 💾 **存储资源** - PV/PVC/StorageClass 管理
- 🏷️ **命名空间** - 命名空间管理与资源配额

### 系统管理
- 👤 **用户管理** - 用户 CRUD、角色分配、激活/禁用
- 🔐 **权限控制** - RBAC 角色权限（Admin/Developer/Viewer）
- 📝 **操作审计** - 用户操作日志记录与查询
- ⚙️ **系统设置** - 刷新间隔、通知配置、集群选择

---

## 🛠️ 技术栈

### 后端
| 技术 | 版本 | 说明 |
|------|------|------|
| Python | 3.10+ | 后端运行环境 |
| FastAPI | 0.109+ | Web 框架 |
| SQLAlchemy | 2.0+ | ORM 框架 |
| Kubernetes Client | 29.0+ | K8s API 客户端 |
| Pydantic | 2.0+ | 数据验证 |
| Redis | 5.0+ | 缓存层 |
| MySQL | 8.0+ | 数据持久化 |
| Python-Jose | 3.3+ | JWT 认证 |
| Passlib | 1.7+ | 密码加密 |
| SlowAPI | 0.1.9+ | 速率限制 |

### 前端
| 技术 | 版本 | 说明 |
|------|------|------|
| Vue | 3.4+ | 前端框架 |
| TypeScript | 5.3+ | 类型系统 |
| Element Plus | 2.5+ | UI 组件库 |
| ECharts | 5.4+ | 图表库 |
| Pinia | 2.1+ | 状态管理 |
| Vue Router | 4.2+ | 路由管理 |
| Axios | 1.6+ | HTTP 客户端 |
| Vite | 5.0+ | 构建工具 |

---

## 🚀 快速开始

### 前置要求
- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Redis 6.0+

### 1. 克隆项目
```bash
git clone <repository-url>
cd K8s-health-check
```

### 2. 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -e .
pip install email-validator

# 配置环境变量
cp .env.example .env
# 编辑 .env 配置数据库连接

# 创建数据库
mysql -u root -p -e "CREATE DATABASE k8s_monitor CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p -e "CREATE USER 'k8s_monitor'@'%' IDENTIFIED BY 'changeme';"
mysql -u root -p -e "GRANT ALL PRIVILEGES ON k8s_monitor.* TO 'k8s_monitor'@'%';"

# 创建默认管理员用户
python scripts/create_admin.py

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 前端启动

```bash
# 进入前端目录（新终端）
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 生产构建
npm run build
```

### 4. 访问系统

打开浏览器访问：`http://localhost:3000`

**默认管理员账号：**
- 用户名：`admin`
- 密码：`Admin@123`

⚠️ **首次登录后请立即修改密码！**

---

## 📡 API 接口

### 认证接口

| 方法 | 路径 | 说明 | 需要认证 |
|------|------|------|----------|
| POST | `/api/v1/auth/login` | 用户登录（速率限制：5 次/分钟） | ❌ |
| POST | `/api/v1/auth/register` | 用户注册（速率限制：3 次/分钟） | ❌ |
| GET | `/api/v1/auth/me` | 获取当前用户 | ✅ |
| POST | `/api/v1/auth/logout` | 用户登出 | ✅ |

**密码要求：**
- 至少 8 个字符
- 至少一个大写字母、一个小写字母、一个数字、一个特殊字符

### 用户管理

| 方法 | 路径 | 说明 | 需要权限 |
|------|------|------|----------|
| GET | `/api/v1/users` | 用户列表（支持筛选） | ✅ |
| POST | `/api/v1/users` | 创建用户 | Admin |
| GET | `/api/v1/users/{id}` | 用户详情 | ✅ |
| PUT | `/api/v1/users/{id}` | 更新用户 | Admin |
| DELETE | `/api/v1/users/{id}` | 删除用户 | Admin |
| GET | `/api/v1/users/audit/logs` | 审计日志 | ✅ |

### K8s 资源

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/nodes` | 获取节点列表 |
| GET | `/api/v1/nodes/{name}` | 获取单个节点详情 |
| GET | `/api/v1/nodes/{name}/metrics` | 获取节点指标 |
| GET | `/api/v1/pods` | 获取 Pod 列表 |
| GET | `/api/v1/deployments` | 获取 Deployment 列表 |
| GET | `/api/v1/cluster/summary` | 获取集群概览 |
| GET | `/api/v1/cluster/namespaces` | 获取命名空间列表 |
| WS | `/ws/metrics` | WebSocket 实时推送（需要 Token 认证） |

### 健康检查

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/ready` | 就绪检查 |

---

## 🖼️ 前端页面

| 页面 | 路径 | 功能描述 |
|------|------|----------|
| 登录页 | `/login` | 用户登录/注册/找回密码 |
| Dashboard | `/` | 集群概览、资源图表、告警列表 |
| 节点管理 | `/nodes` | 节点列表、状态监控、维护操作 |
| Pod 管理 | `/pods` | Pod 列表、日志查看、详情 |
| 工作负载 | `/deployments` | Deployment 管理、扩缩容 |
| ReplicaSet | `/replicasets` | ReplicaSet 列表与监控 |
| Service | `/services` | Service 配置管理 |
| Ingress | `/ingress` | Ingress 路由配置 |
| NetworkPolicy | `/networkpolicies` | 网络策略管理 |
| PV | `/pvs` | PersistentVolume 管理 |
| PVC | `/pvcs` | PersistentVolumeClaim 管理 |
| StorageClass | `/storageclasses` | 存储类配置 |
| 命名空间 | `/namespaces` | 命名空间与配额管理 |
| 用户管理 | `/users` | 用户 CRUD、角色管理 |
| 操作审计 | `/audit` | 操作日志查询 |
| 系统设置 | `/settings` | 系统配置、通知设置 |

---

## 🔐 用户认证

### 角色权限

| 角色 | 权限说明 |
|------|----------|
| **Admin** | 所有权限 - 用户管理、系统配置、资源操作 |
| **Developer** | 读写权限 - 资源管理、查看日志、执行操作 |
| **Viewer** | 只读权限 - 查看资源、监控数据 |

### Token 认证

系统使用 JWT Token 进行认证：

1. 登录后获取 Token
2. Token 存储在 `localStorage`
3. 请求自动携带 `Authorization: Bearer <token>`
4. Token 有效期 24 小时
5. 401 自动跳转登录

### 安全特性

- ✅ **密码强度验证** - 必须包含大小写字母、数字和特殊字符
- ✅ **速率限制** - 登录 5 次/分钟，注册 3 次/分钟
- ✅ **CORS 限制** - 仅允许配置的来源访问
- ✅ **WebSocket 认证** - 实时推送需要有效 Token
- ✅ **审计日志** - 记录所有用户操作

### 请求示例

```bash
# 登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 获取用户列表（需要认证）
curl http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer <your-token>"
```

---

## ⚙️ 配置文件

### 后端配置 (`backend/.env`)

```ini
# 应用配置
APP_NAME=K8s Health Check
DEBUG=true
HOST=0.0.0.0
PORT=8000

# 安全密钥（生产环境必须修改！）
SECRET_KEY=your-secret-key-change-in-production

# CORS 允许的来源（生产环境配置）
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Kubernetes 配置
K8S_APISERVER_URL=https://kubernetes.default.svc
K8S_SSL_VERIFY=true

# MySQL 配置
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=k8s_monitor
MYSQL_PASSWORD=changeme
MYSQL_DATABASE=k8s_monitor

# Redis 配置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_CACHE_TTL=30

# 采集器配置
COLLECTOR_INTERVAL=15
```

### 前端代理 (`frontend/vite.config.ts`)

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
    '/ws': {
      target: 'ws://localhost:8000',
      ws: true,
    },
  },
}
```

### 生产环境部署前检查

- [ ] 设置强 `SECRET_KEY`（至少 32 字符的随机字符串）
- [ ] 设置 `DEBUG=false`
- [ ] 配置 `ALLOWED_ORIGINS` 为实际域名
- [ ] 修改数据库密码
- [ ] 启用 HTTPS
- [ ] 首次登录后立即修改管理员密码

---

## 📦 部署指南

### Docker Compose 部署

```yaml
version: '3.8'
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: k8s_monitor
      MYSQL_USER: k8s_monitor
      MYSQL_PASSWORD: changeme
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    depends_on:
      - mysql
      - redis
    ports:
      - "8000:8000"
    environment:
      - MYSQL_HOST=mysql
      - REDIS_HOST=redis

  frontend:
    build: ./frontend
    depends_on:
      - backend
    ports:
      - "80:80"
```

### Kubernetes 部署

```bash
# 部署到 K8s 集群
kubectl apply -f deploy/k8s/manifests.yml

# 查看状态
kubectl get pods -n k8s-monitor
kubectl get svc -n k8s-monitor
```

---

## 🧑‍💻 开发指南

### 添加新的 K8s 资源收集器

1. 在 `backend/app/collectors/` 创建收集器
2. 继承 `BaseCollector` 实现 `collect()` 方法
3. 在 `MetricsService` 注册收集器
4. 在 `backend/app/api/routes/` 创建 API 路由
5. 在 `frontend/src/views/` 创建前端页面
6. 在 `frontend/src/router/` 添加路由

### 前端组件开发

```bash
# 安装依赖
npm install

# 开发模式
npm run dev

# 代码检查
npm run lint

# 生产构建
npm run build

# 预览构建
npm run preview
```

### 后端开发

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行服务
uvicorn app.main:app --reload

# 运行测试
pytest tests/

# 代码格式化
ruff format app/
```

---

## 📝 更新日志

### v1.1.0 (2026-04-06)
- 🔒 **安全加固** - 添加密码强度验证、速率限制、WebSocket 认证
- 🔒 **CORS 限制** - 仅允许配置的来源访问
- 🔒 **SECRET_KEY 持久化** - 强制设置，防止重启后 Token 失效
- 🐛 **修复 TypeScript 错误** - 前端编译通过
- 📚 **完善文档** - 更新安全配置说明

### v1.0.0 (2026-04-06)
- ✨ 前端重构 - 全新 K8s 监控 UI
- ✨ 用户认证系统 - JWT + RBAC
- ✨ 用户管理 - CRUD + 角色权限
- ✨ 操作审计 - 用户操作日志
- 🐛 修复已知问题
- 📚 完善文档

### v0.1.0 (2026-03-01)
- 初始版本发布
- 基础节点/Pod/Deployment 监控
- 集群概览功能

---

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

MIT License

---

## 📞 联系方式

如有问题或建议，请提交 Issue 或联系开发团队。
claude --resume bbcd838b-db15-4a17-a30a-aa120ed73a36