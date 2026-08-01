import { defineStore } from 'pinia'

export const useTabsStore = defineStore('tabs', {
  state: () => ({
    tabs: []
  }),
  getters: {
    activeTab: (state) => state.tabs.find((t) => t.active)?.path || ''
  },
  actions: {
    /** 访问页面时更新标签(首页固定不可关闭) */
    addTab(route) {
      const path = route.path
      const exists = this.tabs.find((t) => t.path === path)
      if (exists) {
        exists.active = true
        return
      }
      const title = route.meta.title || path
      const closable = path !== '/dashboard'
      this.tabs.push({ path, title, closable, active: true })
      // 激活当前,去激活其他
      this.tabs.forEach((t) => (t.active = t.path === path))
    },
    setActive(path) {
      this.tabs.forEach((t) => (t.active = t.path === path))
    },
    closeTab(path) {
      const index = this.tabs.findIndex((t) => t.path === path)
      if (index === -1) return
      const wasActive = this.tabs[index].active
      this.tabs.splice(index, 1)
      if (wasActive && this.tabs.length) {
        const next = this.tabs[Math.min(index, this.tabs.length - 1)]
        next.active = true
        return next.path
      }
      return null
    }
  }
})
