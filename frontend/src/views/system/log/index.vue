<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { Refresh, Search } from '@element-plus/icons-vue'
import { getLoginLogs, getOperationLogs } from '../../../api/log'

const activeTab = ref('operation')
const loading = ref(false)

// ---------- 操作日志 ----------
const opList = ref([])
const opTotal = ref(0)
const opQuery = reactive({ page: 1, page_size: 10, username: '', method: '' })

// ---------- 登录日志 ----------
const loginList = ref([])
const loginTotal = ref(0)
const loginQuery = reactive({ page: 1, page_size: 10, username: '', success: 0 })

async function loadOperation() {
  loading.value = true
  try {
    const res = await getOperationLogs(opQuery)
    opList.value = res.items
    opTotal.value = res.total
  } finally {
    loading.value = false
  }
}

async function loadLogin() {
  loading.value = true
  try {
    const res = await getLoginLogs(loginQuery)
    loginList.value = res.items
    loginTotal.value = res.total
  } finally {
    loading.value = false
  }
}

function load() {
  activeTab.value === 'operation' ? loadOperation() : loadLogin()
}

function handleSearch() {
  activeTab.value === 'operation' ? (opQuery.page = 1) : (loginQuery.page = 1)
  load()
}

function handleReset() {
  if (activeTab.value === 'operation') {
    opQuery.username = ''
    opQuery.method = ''
    opQuery.page = 1
  } else {
    loginQuery.username = ''
    loginQuery.success = 0
    loginQuery.page = 1
  }
  load()
}

function handlePageChange(page) {
  activeTab.value === 'operation' ? (opQuery.page = page) : (loginQuery.page = page)
  load()
}

// 操作日志 params 展示(格式化 JSON)
function formatParams(params) {
  if (!params) return '-'
  try {
    return JSON.stringify(JSON.parse(params), null, 0)
  } catch {
    return params
  }
}

const methodTag = (m) => ({ POST: 'success', PUT: 'warning', DELETE: 'danger', PATCH: 'info' }[m] || 'info')

watch(activeTab, () => {
  if (activeTab.value === 'operation') {
    opQuery.page = 1
    loadOperation()
  } else {
    loginQuery.page = 1
    loadLogin()
  }
})

onMounted(loadOperation)
</script>

<template>
  <el-card shadow="never">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="操作日志" name="operation">
        <div class="toolbar">
          <el-input
            v-model="opQuery.username"
            placeholder="按操作人搜索"
            clearable
            style="width: 180px"
            @keyup.enter="handleSearch"
          />
          <el-select v-model="opQuery.method" placeholder="全部方法" clearable style="width: 120px" @change="handleSearch">
            <el-option v-for="m in ['POST', 'PUT', 'DELETE']" :key="m" :label="m" :value="m" />
          </el-select>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </div>

        <el-table v-loading="loading" :data="opList" stripe>
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="username" label="操作人" width="110" />
          <el-table-column label="方法" width="90">
            <template #default="{ row }">
              <el-tag :type="methodTag(row.method)" size="small">{{ row.method }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="path" label="接口路径" min-width="180" />
          <el-table-column prop="status_code" label="状态码" width="90" />
          <el-table-column label="请求参数" min-width="220">
            <template #default="{ row }">
              <el-text type="info" size="small">{{ formatParams(row.params) }}</el-text>
            </template>
          </el-table-column>
          <el-table-column prop="ip" label="IP" width="130" />
          <el-table-column prop="created_at" label="操作时间" width="170" />
        </el-table>

        <el-pagination
          v-model:current-page="opQuery.page"
          :page-size="opQuery.page_size"
          :total="opTotal"
          layout="total, prev, pager, next"
          class="pagination"
          @current-change="handlePageChange"
        />
      </el-tab-pane>

      <el-tab-pane label="登录日志" name="login">
        <div class="toolbar">
          <el-input
            v-model="loginQuery.username"
            placeholder="按用户名搜索"
            clearable
            style="width: 180px"
            @keyup.enter="handleSearch"
          />
          <el-select v-model="loginQuery.success" placeholder="全部结果" style="width: 130px" @change="handleSearch">
            <el-option label="全部结果" :value="0" />
            <el-option label="登录成功" :value="1" />
            <el-option label="登录失败" :value="2" />
          </el-select>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </div>

        <el-table v-loading="loading" :data="loginList" stripe>
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="username" label="用户名" width="130" />
          <el-table-column label="结果" width="90">
            <template #default="{ row }">
              <el-tag :type="row.success ? 'success' : 'danger'" size="small">
                {{ row.success ? '成功' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="message" label="信息" min-width="220" />
          <el-table-column prop="ip" label="IP" width="130" />
          <el-table-column prop="created_at" label="时间" width="170" />
        </el-table>

        <el-pagination
          v-model:current-page="loginQuery.page"
          :page-size="loginQuery.page_size"
          :total="loginTotal"
          layout="total, prev, pager, next"
          class="pagination"
          @current-change="handlePageChange"
        />
      </el-tab-pane>
    </el-tabs>
  </el-card>
</template>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}
.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>
