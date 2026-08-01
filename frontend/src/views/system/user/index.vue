<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Download, Edit, Plus, Refresh, Search } from '@element-plus/icons-vue'
import { createUser, deleteUser, exportUsers, getRoleOptions, getUsers, updateUser } from '../../../api/user'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const roleOptions = ref([])

const query = reactive({
  page: 1,
  page_size: 10,
  keyword: ''
})

async function load() {
  loading.value = true
  try {
    const res = await getUsers(query)
    list.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

async function loadRoles() {
  roleOptions.value = await getRoleOptions()
}

function handleSearch() {
  query.page = 1
  load()
}

function handleReset() {
  query.keyword = ''
  query.page = 1
  load()
}

function handleExport() {
  exportUsers({ keyword: query.keyword })
}

function handlePageChange(page) {
  query.page = page
  load()
}

// ---------- 新增 / 编辑 ----------
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()
const form = reactive({
  id: null,
  username: '',
  password: '',
  nickname: '',
  email: '',
  phone: '',
  status: 'active',
  role_id: null
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

function openCreate() {
  isEdit.value = false
  Object.assign(form, {
    id: null,
    username: '',
    password: '',
    nickname: '',
    email: '',
    phone: '',
    status: 'active',
    role_id: null
  })
  dialogVisible.value = true
}

function openEdit(row) {
  isEdit.value = true
  Object.assign(form, {
    id: row.id,
    username: row.username,
    password: '',
    nickname: row.nickname,
    email: row.email,
    phone: row.phone,
    status: row.status,
    role_id: row.role_id
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  await formRef.value.validate()
  const data = {
    nickname: form.nickname,
    email: form.email,
    phone: form.phone,
    status: form.status,
    role_id: form.role_id
  }
  if (isEdit.value) {
    if (form.password) data.password = form.password
    await updateUser(form.id, data)
    ElMessage.success('修改成功')
  } else {
    data.username = form.username
    data.password = form.password
    await createUser(data)
    ElMessage.success('新增成功')
  }
  dialogVisible.value = false
  load()
}

// ---------- 启用 / 禁用 ----------
async function toggleStatus(row) {
  const status = row.status === 'active' ? 'disabled' : 'active'
  await updateUser(row.id, { status })
  ElMessage.success(status === 'active' ? '已启用' : '已禁用')
  load()
}

// ---------- 删除 ----------
function handleDelete(row) {
  ElMessageBox.confirm(`确定要删除用户「${row.username}」吗?`, '警告', { type: 'warning' })
    .then(async () => {
      await deleteUser(row.id)
      ElMessage.success('删除成功')
      load()
    })
    .catch(() => {})
}

onMounted(() => {
  load()
  loadRoles()
})
</script>

<template>
  <el-card shadow="never">
    <!-- 搜索栏 -->
    <div class="toolbar">
      <el-input
        v-model="query.keyword"
        placeholder="搜索用户名 / 昵称 / 邮箱"
        clearable
        style="width: 260px"
        @keyup.enter="handleSearch"
      >
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
      <el-button :icon="Refresh" @click="handleReset">重置</el-button>
      <div class="spacer" />
      <el-button v-permission="'user:view'" :icon="Download" @click="handleExport">导出</el-button>
      <el-button v-permission="'user:add'" type="primary" :icon="Plus" @click="openCreate">
        新增用户
      </el-button>
    </div>

    <!-- 表格 -->
    <el-table v-loading="loading" :data="list" stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="username" label="用户名" width="120" />
      <el-table-column prop="nickname" label="昵称" width="120" />
      <el-table-column prop="email" label="邮箱" min-width="180" />
      <el-table-column prop="phone" label="手机号" width="130" />
      <el-table-column label="角色" width="120">
        <template #default="{ row }">{{ row.role?.name || '-' }}</template>
      </el-table-column>
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
            {{ row.status === 'active' ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="170" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button v-permission="'user:edit'" link type="primary" :icon="Edit" @click="openEdit(row)">
            编辑
          </el-button>
          <el-button v-permission="'user:edit'" link type="warning" @click="toggleStatus(row)">
            {{ row.status === 'active' ? '禁用' : '启用' }}
          </el-button>
          <el-button v-permission="'user:delete'" link type="danger" :icon="Delete" @click="handleDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
      v-model:current-page="query.page"
      :page-size="query.page_size"
      :total="total"
      layout="total, prev, pager, next"
      class="pagination"
      @current-change="handlePageChange"
    />
  </el-card>

  <!-- 新增/编辑弹窗 -->
  <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑用户' : '新增用户'" width="480px" destroy-on-close>
    <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
      <el-form-item label="用户名" prop="username">
        <el-input v-model="form.username" :disabled="isEdit" placeholder="登录账号" />
      </el-form-item>
      <el-form-item v-if="!isEdit" label="密码" prop="password">
        <el-input v-model="form.password" type="password" show-password placeholder="初始密码" />
      </el-form-item>
      <el-form-item v-else label="密码">
        <el-input v-model="form.password" type="password" show-password placeholder="留空则不修改" />
      </el-form-item>
      <el-form-item label="昵称">
        <el-input v-model="form.nickname" placeholder="显示名称" />
      </el-form-item>
      <el-form-item label="邮箱">
        <el-input v-model="form.email" placeholder="邮箱地址" />
      </el-form-item>
      <el-form-item label="手机号">
        <el-input v-model="form.phone" placeholder="手机号码" />
      </el-form-item>
      <el-form-item label="角色">
        <el-select v-model="form.role_id" placeholder="选择角色" clearable style="width: 100%">
          <el-option v-for="role in roleOptions" :key="role.id" :label="role.name" :value="role.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-radio-group v-model="form.status">
          <el-radio value="active">启用</el-radio>
          <el-radio value="disabled">禁用</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit">确定</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}
.spacer {
  flex: 1;
}
.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>
