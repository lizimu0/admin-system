import { createRouter, createWebHistory } from 'vue-router'

import Layout from '../layout/index.vue'
import { useUserStore } from '../store/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/login/index.vue'),
    meta: { public: true, title: '登录' }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/dashboard/index.vue'),
        meta: { title: '数据看板', perm: 'dashboard:view' }
      },
      {
        path: 'system/user',
        name: 'SystemUser',
        component: () => import('../views/system/user/index.vue'),
        meta: { title: '用户管理', perm: 'user:view' }
      },
      {
        path: 'system/role',
        name: 'SystemRole',
        component: () => import('../views/system/role/index.vue'),
        meta: { title: '角色管理', perm: 'role:view' }
      },
      {
        path: 'system/log',
        name: 'SystemLog',
        component: () => import('../views/system/log/index.vue'),
        meta: { title: '日志管理', perm: 'log:view' }
      },
      {
        path: 'product',
        name: 'Product',
        component: () => import('../views/product/index.vue'),
        meta: { title: '商品管理', perm: 'product:view' }
      }
    ]
  },
  { path: '/403', component: () => import('../views/error/403.vue'), meta: { title: '无权限', public: true } },
  { path: '/:pathMatch(.*)*', component: () => import('../views/error/404.vue'), meta: { title: '页面不存在', public: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to) => {
  const store = useUserStore()

  // 公开页面(登录/403/404)直接放行
  if (to.meta.public) return true

  // 未登录跳登录页
  if (!store.token) return { path: '/login', query: { redirect: to.fullPath } }

  // 已登录但信息未加载,先拉取用户信息
  if (!store.userInfo) {
    try {
      await store.fetchMe()
    } catch {
      store.logout()
      return { path: '/login' }
    }
  }

  // 页面级权限校验:无权限跳 403 页
  if (to.meta.perm && !store.hasPermission(to.meta.perm)) {
    return { path: '/403' }
  }

  return true
})

export default router
