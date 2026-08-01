<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Download, Edit, Plus, Refresh, Search } from '@element-plus/icons-vue'
import {
  createProduct,
  deleteProduct,
  exportProducts,
  getCategories,
  getProducts,
  updateProduct
} from '../../api/product'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const categories = ref([])

const query = reactive({
  page: 1,
  page_size: 10,
  keyword: '',
  category: ''
})

async function load() {
  loading.value = true
  try {
    const res = await getProducts(query)
    list.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

async function loadCategories() {
  categories.value = await getCategories()
}

function handleSearch() {
  query.page = 1
  load()
}

function handleReset() {
  query.keyword = ''
  query.category = ''
  query.page = 1
  load()
}

function handleExport() {
  exportProducts({ keyword: query.keyword, category: query.category })
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
  name: '',
  category: '',
  price: 0,
  stock: 0,
  status: 'on',
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }]
}

function openCreate() {
  isEdit.value = false
  Object.assign(form, {
    id: null,
    name: '',
    category: '',
    price: 0,
    stock: 0,
    status: 'on',
    description: ''
  })
  dialogVisible.value = true
}

function openEdit(row) {
  isEdit.value = true
  Object.assign(form, {
    id: row.id,
    name: row.name,
    category: row.category,
    price: row.price,
    stock: row.stock,
    status: row.status,
    description: row.description
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  await formRef.value.validate()
  const data = { ...form }
  delete data.id
  if (isEdit.value) {
    await updateProduct(form.id, data)
    ElMessage.success('修改成功')
  } else {
    await createProduct(data)
    ElMessage.success('新增成功')
  }
  dialogVisible.value = false
  load()
  loadCategories()
}

// ---------- 上架 / 下架 ----------
async function toggleStatus(row) {
  const status = row.status === 'on' ? 'off' : 'on'
  await updateProduct(row.id, { status })
  ElMessage.success(status === 'on' ? '已上架' : '已下架')
  load()
}

// ---------- 删除 ----------
function handleDelete(row) {
  ElMessageBox.confirm(`确定要删除商品「${row.name}」吗?`, '警告', { type: 'warning' })
    .then(async () => {
      await deleteProduct(row.id)
      ElMessage.success('删除成功')
      load()
    })
    .catch(() => {})
}

onMounted(() => {
  load()
  loadCategories()
})
</script>

<template>
  <el-card shadow="never">
    <div class="toolbar">
      <el-input
        v-model="query.keyword"
        placeholder="搜索商品名称"
        clearable
        style="width: 220px"
        @keyup.enter="handleSearch"
      >
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-select v-model="query.category" placeholder="全部分类" clearable style="width: 150px" @change="handleSearch">
        <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
      </el-select>
      <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
      <el-button :icon="Refresh" @click="handleReset">重置</el-button>
      <div class="spacer" />
      <el-button v-permission="'product:view'" :icon="Download" @click="handleExport">导出</el-button>
      <el-button v-permission="'product:add'" type="primary" :icon="Plus" @click="openCreate">
        新增商品
      </el-button>
    </div>

    <el-table v-loading="loading" :data="list" stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="name" label="商品名称" min-width="160" />
      <el-table-column prop="category" label="分类" width="120" />
      <el-table-column label="价格" width="110">
        <template #default="{ row }">¥ {{ row.price.toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="stock" label="库存" width="90" />
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === 'on' ? 'success' : 'info'">
            {{ row.status === 'on' ? '在售' : '下架' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="160" show-overflow-tooltip />
      <el-table-column prop="created_at" label="创建时间" width="170" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button v-permission="'product:edit'" link type="primary" :icon="Edit" @click="openEdit(row)">
            编辑
          </el-button>
          <el-button v-permission="'product:edit'" link type="warning" @click="toggleStatus(row)">
            {{ row.status === 'on' ? '下架' : '上架' }}
          </el-button>
          <el-button v-permission="'product:delete'" link type="danger" :icon="Delete" @click="handleDelete(row)">
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

  <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑商品' : '新增商品'" width="520px" destroy-on-close>
    <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
      <el-form-item label="商品名称" prop="name">
        <el-input v-model="form.name" placeholder="商品名称" />
      </el-form-item>
      <el-form-item label="分类">
        <el-select v-model="form.category" placeholder="选择分类" clearable allow-create filterable style="width: 100%">
          <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
        </el-select>
      </el-form-item>
      <el-form-item label="价格" prop="price">
        <el-input-number v-model="form.price" :min="0" :precision="2" :step="1" style="width: 100%" />
      </el-form-item>
      <el-form-item label="库存">
        <el-input-number v-model="form.stock" :min="0" :step="1" style="width: 100%" />
      </el-form-item>
      <el-form-item label="状态">
        <el-radio-group v-model="form.status">
          <el-radio value="on">在售</el-radio>
          <el-radio value="off">下架</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="form.description" type="textarea" :rows="3" placeholder="商品描述" />
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
