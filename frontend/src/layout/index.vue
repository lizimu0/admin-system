<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import {
  ArrowDown,
  DataLine,
  Document,
  Goods,
  Setting,
  User,
  UserFilled
} from '@element-plus/icons-vue'
import { useUserStore } from '../store/user'
import { useTabsStore } from '../store/tabs'
import TagsView from './components/TagsView.vue'
import ProfileDialog from './components/ProfileDialog.vue'

const route = useRoute()
const router = useRouter()
const store = useUserStore()
const tabsStore = useTabsStore()

const nickname = computed(() => store.userInfo?.nickname || store.userInfo?.username || '')
const activeMenu = computed(() => route.path)
const profileVisible = ref(false)

// 面包屑
const breadcrumbs = computed(() => {
  const title = route.meta.title || ''
  if (route.path.startsWith('/system')) {
    return [{ label: '首页', path: '/dashboard' }, { label: '系统管理', path: '' }, { label: title, path: '' }]
  }
  return [{ label: '首页', path: '/dashboard' }, { label: title, path: '' }]
})

function has(code) {
  return store.hasPermission(code)
}

function handleCommand(command) {
  if (command === 'profile') {
    profileVisible.value = true
  } else if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗?', '提示', { type: 'warning' })
      .then(() => {
        store.logout()
        router.push('/login')
      })
      .catch(() => {})
  }
}

// 路由变化时更新标签页
watch(
  () => route.path,
  () => tabsStore.addTab(route),
  { immediate: true }
)
onMounted(() => tabsStore.addTab(route))
</script>

<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="logo">
        <el-icon :size="22" color="#409eff"><DataLine /></el-icon>
        <span>后台管理系统</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#001529"
        text-color="rgba(255,255,255,0.65)"
        active-text-color="#ffffff"
        class="menu"
      >
        <el-menu-item v-if="has('dashboard:view')" index="/dashboard">
          <el-icon><DataLine /></el-icon>
          <span>数据看板</span>
        </el-menu-item>

        <el-sub-menu v-if="has('user:view') || has('role:view') || has('log:view')" index="system">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item v-if="has('user:view')" index="/system/user">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          <el-menu-item v-if="has('role:view')" index="/system/role">
            <el-icon><UserFilled /></el-icon>
            <span>角色管理</span>
          </el-menu-item>
          <el-menu-item v-if="has('log:view')" index="/system/log">
            <el-icon><Document /></el-icon>
            <span>日志管理</span>
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item v-if="has('product:view')" index="/product">
          <el-icon><Goods /></el-icon>
          <span>商品管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item
              v-for="(item, index) in breadcrumbs"
              :key="index"
              :to="item.path ? { path: item.path } : undefined"
            >
              {{ item.label }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            <el-avatar :size="30" class="avatar">{{ nickname.charAt(0) }}</el-avatar>
            <span class="name">{{ nickname }}</span>
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人中心</el-dropdown-item>
              <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>

      <TagsView />

      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>

  <ProfileDialog v-model="profileVisible" />
</template>

<style scoped>
.layout {
  height: 100vh;
}
.aside {
  background: #001529;
  display: flex;
  flex-direction: column;
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.menu {
  border-right: none;
  flex: 1;
}
.header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e6e6e6;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #333;
}
.avatar {
  background: #409eff;
  color: #fff;
}
.main {
  background: #f0f2f5;
}
</style>
