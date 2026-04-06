# 安全修复总结

本文档记录了 K8s 集群监控管理平台的安全漏洞修复内容。

## 修复日期
2026-04-06

## 修复概览

| 严重性 | 问题 | 状态 | 修复说明 |
|--------|------|------|----------|
| 🔴 CRITICAL | SECRET_KEY 持久化 | ✅ 已修复 | SECRET_KEY 现在必须设置，否则应用无法启动 |
| 🔴 CRITICAL | JWT Token 存储安全 | ⚠️ 需注意 | Token 存储在 localStorage，需防范 XSS |
| 🟠 HIGH | CORS 配置过于宽松 | ✅ 已修复 | 限制为特定源，不再允许所有来源 |
| 🟠 HIGH | 无 CSRF 保护 | ⚠️ 部分修复 | 使用 Header 验证，需前端配合 |
| 🟡 MEDIUM | 无密码强度要求 | ✅ 已修复 | 添加密码复杂度验证 |
| 🟡 MEDIUM | 无速率限制 | ✅ 已修复 | 登录 5 次/分钟，注册 3 次/分钟 |
| 🟡 MEDIUM | WebSocket 无认证 | ✅ 已修复 | WebSocket 连接需要有效 Token |
| 🟢 LOW | Debug 模式默认开启 | ⚠️ 已提示 | .env.example 中 DEBUG=true 仅用于开发 |

---

## 详细修复内容

### 1. SECRET_KEY 持久化 (CRITICAL)

**问题**: `SECRET_KEY` 每次应用重启都会自动生成，导致：
- 所有已颁发的 JWT Token 失效
- 用户需要重新登录
- 生产环境重启后所有会话中断

**修复**: 
- `SECRET_KEY` 现在是必填字段
- 如果未设置，应用启动时会发出警告
- 更新了 `.env.example` 强调必须修改

**文件变更**:
- `backend/app/config.py` - 添加 SECRET_KEY 验证逻辑
- `backend/.env.example` - 强调生产环境必须修改

---

### 2. CORS 配置 (HIGH)

**问题**: `allow_origins=["*"]` 允许任何网站发起请求，可能导致：
- CSRF 攻击
- 跨站数据泄露

**修复**:
- 开发环境：仅允许 localhost 相关端口 (3000, 5173)
- 生产环境：通过 `ALLOWED_ORIGINS` 环境变量配置
- 限制了允许的 HTTP 方法和 Headers

**文件变更**:
- `backend/app/main.py` - 动态配置 CORS  origins
- `backend/.env.example` - 添加 `ALLOWED_ORIGINS` 配置项

---

### 3. 密码强度验证 (MEDIUM)

**问题**: 用户可以设置弱密码（如 "123456"），容易被暴力破解

**修复**: 密码必须满足以下要求：
- 至少 8 个字符
- 至少一个大写字母
- 至少一个小写字母
- 至少一个数字
- 至少一个特殊字符

**文件变更**:
- `backend/app/schemas/auth.py` - 添加 `validate_password` 验证器

---

### 4. 速率限制 (MEDIUM)

**问题**: 登录接口无频率限制，容易被暴力破解

**修复**:
- 登录接口：5 次/分钟/IP
- 注册接口：3 次/分钟/IP
- 失败登录会被记录到审计日志

**文件变更**:
- `backend/app/main.py` - 配置 SlowAPI 中间件
- `backend/app/api/routes/auth.py` - 添加 `@limiter.limit` 装饰器
- `backend/pyproject.toml` - 添加 `slowapi` 依赖

---

### 5. WebSocket 认证 (MEDIUM)

**问题**: WebSocket 端点 `/ws/metrics` 无需认证即可连接，可能泄露实时监控数据

**修复**:
- 连接时需提供 JWT Token
- 无效 Token 会被拒绝连接
- 前端已更新自动在 URL 中附带 Token

**文件变更**:
- `backend/app/api/websocket.py` - 添加 Token 验证逻辑
- `frontend/src/views/Layout.vue` - 连接时附带 Token

---

## 仍需注意的问题

### 1. JWT Token 存储 (CRITICAL - 需注意)

**现状**: Token 存储在 `localStorage`，存在 XSS 攻击风险

**建议**: 
- 生产环境考虑使用 HttpOnly Cookie
- 需要前端和后端配合修改
- 当前实现需确保严格防范 XSS（输入过滤、输出转义）

### 2. CSRF 保护 (HIGH - 部分修复)

**现状**: 已通过 CORS 限制来源，但未实现 CSRF Token

**建议**:
- 对于敏感操作（删除用户、修改配置）添加二次验证
- 或实现 CSRF Token 机制

### 3. Debug 模式 (LOW)

**现状**: `.env.example` 中 `DEBUG=true`

**说明**: 
- 开发环境需要 Debug 模式
- 生产环境部署时必须设置 `DEBUG=false`
- 已在文档中强调

---

## 部署前检查清单

生产环境部署前，请确保：

- [ ] 设置强 `SECRET_KEY`（至少 32 字符的随机字符串）
- [ ] 设置 `DEBUG=false`
- [ ] 配置 `ALLOWED_ORIGINS` 为实际域名
- [ ] 修改数据库密码
- [ ] 修改 Redis 密码（如启用）
- [ ] 启用 HTTPS
- [ ] 创建默认管理员用户后立即修改密码

---

## 依赖更新

新增依赖：
- `slowapi>=0.1.9` - 速率限制

确保运行：
```bash
cd backend
source venv/bin/activate
pip install -e .
```

---

## 参考资源

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT Best Practices](https://datatracker.ietf.org/doc/html/rfc8725)
