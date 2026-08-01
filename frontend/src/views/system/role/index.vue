<script setup>
import { nextTick, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Edit, Plus, Refresh, Search } from '@element-plus/icons-vue'
import { createRole, deleteRole, getRoles, updateRole } from '../../../api/role'

// 权限配置树(与后端权限码对应)
const PERMISSION_TREE = [
  { code: 'group:dashboard', label: '数据看板', children: [{ code: 'dashboard:view', label: '查看看板' }] },
  {
    code: 'group:user',
    label: '用户管理',
    children: [
      { code: 'user:view', label: '查看用户' },
      { code: 'user:add', label: '新增用户' },
      { code: 'user:edit', label: '编辑用户' },
      { code: 'user:delete', label: '删除用户' }
    ]
  },
  {
    code: 'group:role',
    label: '角色管理',
    children: [
      { code: 'role:view', label: '查看角色' },
      { code: 'role:add', label: '新增角色' },
      { code: 'role:edit', label: '编辑角色' },
      { code: 'role:delete', label: '删除角色' }
    ]
  },
  {
    code: 'group:product',
    label: '商品管理',
    children: [
      { code: 'product:view', label: '查看商品' },
      { code: 'product:add', label: '新增商品' },
      { code: 'product:edit', label: '编辑商品' },
      { code: 'product:delete', label: '删除商品' }
    ]
  },
  {
    code: 'group:log',
    label: '日志管理',
    children: [{ code: 'log:view', label: '查看日志' }]
  }
]

const loading = ref(false)
const list = ref([])
const total = ref(0)

const query = reactive({
  page: 1,
  page_size: 10,
  keyword: ''
})

async function load() {
  loading.value = true
  try {
    const res = await getRoles(query)
    list.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
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

function handlePageChange(page) {
  query.page = page
  load()
}

// ---------- 新增 / 编辑 ----------
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()
const treeRef = ref()
const form = reactive({
  id: null,
  name: '',
  code: '',
  description: ''
})

function openCreate() {
  isEdit.value = false
  Object.assign(form, { id: null, name: '', code: '', description: '' })
  dialogVisible.value = true
  nextTick(() => treeRef.value?.setCheckedKeys([]))
}

function openEdit(row) {
  isEdit.value = true
  Object.assign(form, {
    id: row.id,
    name: row.name,
    code: row.code,
    description: row.description
  })
  dialogVisible.value = true
  // 编辑时回显已勾选的权限码
  nextTick(() => {
    const keys = row.permissions.filter((p) => !p.startsWith('group:'))
    treeRef.value?.setCheckedKeys(keys)
  })
}

async function handleSubmit() {
  await formRef.value.validate()
  // 只收集叶子节点权限码(group 前缀为分组节点,不提交)
  const permissions = (treeRef.value?.getCheckedKeys(true) || []).filter(
    (k) => !k.startsWith('group:')
  )
  if (isEdit.value) {
    await updateRole(form.id, { name: form.name, description: form.description, permissions })
    ElMessage.success('修改成功')
  } else {
    await createRole({ ...form, permissions })
    ElMessage.success('新增成功')
  }
  dialogVisible.value = false
  load()
}

// ---------- 删除 ----------
function handleDelete(row) {
  ElMessageBox.confirm(`确定要删除角色「${row.name}」吗?`, '警告', { type: 'warning' })
    .then(async () => {
      await deleteRole(row.id)
      ElMessage.success('删除成功')
      load()
    })
    .catch(() => {})
}

onMounted(load)
</script>

<template>
  <el-card shadow="never">
    <div class="toolbar">
      <el-input
        v-model="query.keyword"
        placeholder="搜索角色名称"
        clearable
        style="width: 220px"
        @keyup.enter="handleSearch"
      >
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
      <el-button :icon="Refresh" @click="handleReset">重置</el-button>
      <div class="spacer" />
      <el-button v-permission="'role:add'" type="primary" :icon="Plus" @click="openCreate">
        新增角色
      </el-button>
    </div>

    <el-table v-loading="loading" :data="list" stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="name" label="角色名称" width="140" />
      <el-table-column prop="code" label="角色编码" width="140" />
      <el-table-column prop="description" label="描述" min-width="200" />
      <el-table-column label="权限数" width="90">
        <template #default="{ row }">{{ row.permissions.length }}</template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="170" />
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button v-permission="'role:edit'" link type="primary" :icon="Edit" @click="openEdit(row)">
            编辑
          </el-button>
          <el-button v-permission="'role:delete'" link type="danger" :icon="Delete" @click="handleDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="query.page"
      :page-size="query.page_size"
      :total="total"
      layout="total, prev, pager, next"
      class="pagination"
      @current-change="handlePageChange"
    />
  </el-card>

  <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑角色' : '新增角色'" width="560px" destroy-on-close>
    <el-form ref="formRef" :model="form" label-width="80px">
      <el-form-item label="角色名称" prop="name" :rules="[{ required: true, message: '请输入角色名称', trigger: 'blur' }]">
        <el-input v-model="form.name" placeholder="如: 运营专员" />
      </el-form-item>
      <el-form-item label="角色编码" prop="code" :rules="[{ required: true, message: '请输入角色编码', trigger: 'blur' }]">
        <el-input v-model="form.code" :disabled="isEdit" placeholder="如: operator" />
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="form.description" placeholder="角色职责说明" />
      </el-form-item>
      <el-form-item label="权限配置">
        <div class="tree-box">
          <el-tree
            ref="treeRef"
            :data="PERMISSION_TREE"
            node-key="code"
            show-checkbox
            check-strictly
            default-expand-all
            :props="{ label: 'label', children: 'children' }"
          />
        </div>
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
.tree-box {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 8px 12px;
  width: 100%;
  max-height: 320px;
  overflow: auto;
}
</style>
