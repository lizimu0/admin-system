import { defineStore } from 'pinia'
import { login as loginApi, getMe } from '../api/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: null
  }),
  getters: {
    permissions: (state) => state.userInfo?.role?.permissions || [],
    roleCode: (state) => state.userInfo?.role?.code || '',
    isAdmin: (state) => state.userInfo?.role?.code === 'admin'
  },
  actions: {
    async login(username, password, captchaId = '', captchaCode = '') {
      const res = await loginApi({ username, password, captcha_id: captchaId, captcha_code: captchaCode })
      this.token = res.access_token
      localStorage.setItem('token', this.token)
      await this.fetchMe()
    },
    async fetchMe() {
      this.userInfo = await getMe()
    },
    logout() {
      this.token = ''
      this.userInfo = null
      localStorage.removeItem('token')
    },
    hasPermission(code) {
      return this.isAdmin || this.permissions.includes(code)
    }
  }
})
