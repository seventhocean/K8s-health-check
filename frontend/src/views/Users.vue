<template>
  <div class="users-page">
    <div class="page-header">
      <h1 class="page-title">用户管理</h1>
      <div class="header-actions">
        <el-button @click="handleRefresh"><el-icon><Refresh /></el-icon> 刷新</el-button>
        <el-button type="primary" @click="showCreate"><el-icon><Plus /></el-icon> 创建用户</el-button>
      </div>
    </div>

    <el-card v-loading="loading">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-input v-model="filters.keyword" placeholder="搜索用户名、邮箱" style="width: 240px" clearable>
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-select v-model="filters.role" placeholder="角色" clearable style="width: 140px">
            <el-option label="管理员" value="admin" />
            <el-option label="开发者" value="developer" />
            <el-option label="观察者" value="viewer" />
          </el-select>
        </div>
      </div>

      <el-table :data="users" stripe>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">{{ row.status === 'active' ? '激活' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户名" min-width="150" />
        <el-table-column prop="email" label="邮箱" min-width="200" />
        <el-table-column prop="phone" label="手机号" width="140" />
        <el-table-column label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'">{{ row.roleName }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="最后登录" width="160">
          <template #default="{ row }">{{ row.lastLogin }}</template>
        </el-table-column>
        <el-table-column label="创建时间" width="160">
          <template #default="{ row }">{{ row.createdAt }}</template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">详情</el-button>
            <el-button link type="warning" @click="editUser(row)">编辑</el-button>
            <el-button link :type="row.status === 'active' ? 'warning' : 'success'" @click="toggleStatus(row)">
              {{ row.status === 'active' ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50]" :total="pagination.total" layout="total, sizes, prev, pager, next, jumper" />
      </div>
    </el-card>

    <!-- 创建/编辑用户对话框 -->
    <el-dialog v-model="userDialogVisible" :title="isEdit ? '编辑用户' : '创建用户'" width="500px">
      <el-form :model="userForm" label-width="100px">
        <el-form-item label="用户名" required><el-input v-model="userForm.username" placeholder="请输入用户名" /></el-form-item>
        <el-form-item label="邮箱" required><el-input v-model="userForm.email" placeholder="请输入邮箱" /></el-form-item>
        <el-form-item label="手机号"><el-input v-model="userForm.phone" placeholder="请输入手机号" /></el-form-item>
        <el-form-item label="角色" required>
          <el-select v-model="userForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="开发者" value="developer" />
            <el-option label="观察者" value="viewer" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="!isEdit" label="密码" required>
          <el-input v-model="userForm.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="userDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveUser">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Refresh, Search, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const isEdit = ref(false)
const userDialogVisible = ref(false)
const users = ref<any[]>([])
const filters = ref({ keyword: '', role: '' })
const pagination = ref({ page: 1, pageSize: 10, total: 3 })
const userForm = ref({ username: '', email: '', phone: '', role: 'viewer', password: '' })

async function fetchData() {
  loading.value = true
  try {
    users.value = [
      { username: 'admin', email: 'admin@example.com', phone: '13800138000', role: 'admin', roleName: '管理员', status: 'active', lastLogin: '2024-01-15 10:00', createdAt: '2024-01-01' },
      { username: 'developer', email: 'dev@example.com', phone: '13900139000', role: 'developer', roleName: '开发者', status: 'active', lastLogin: '2024-01-14 15:30', createdAt: '2024-01-02' },
      { username: 'viewer', email: 'view@example.com', phone: '', role: 'viewer', roleName: '观察者', status: 'disabled', lastLogin: '2024-01-10 09:00', createdAt: '2024-01-03' },
    ]
  } finally {
    loading.value = false
  }
}

function handleRefresh() { fetchData(); ElMessage.success('刷新成功') }
function showCreate() { isEdit.value = false; userForm.value = { username: '', email: '', phone: '', role: 'viewer', password: '' }; userDialogVisible.value = true }
function editUser(row: any) { isEdit.value = true; Object.assign(userForm.value, { ...row, password: '' }); userDialogVisible.value = true }
function viewDetail(row: any) { ElMessage.info(`查看用户：${row.username}`) }
function toggleStatus(row: any) {
  row.status = row.status === 'active' ? 'disabled' : 'active'
  ElMessage.success(`已${row.status === 'active' ? '启用' : '禁用'}用户 ${row.username}`)
}
function handleSaveUser() {
  if (!userForm.value.username || !userForm.value.email) { ElMessage.warning('请填写必填项'); return }
  ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
  userDialogVisible.value = false
  fetchData()
}

onMounted(() => { fetchData() })
</script>

<style scoped lang="scss">
.users-page { padding: 20px;
  .page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;
    .page-title { font-size: 24px; font-weight: 600; color: #1a1f3a; margin: 0; }
    .header-actions { display: flex; gap: 12px; }
  }
  .toolbar { display: flex; margin-bottom: 16px;
    .toolbar-left { display: flex; align-items: center; gap: 12px; }
  }
  .pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }
}
</style>
