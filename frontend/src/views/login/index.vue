<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Lock, User } from '@element-plus/icons-vue'
import { useUserStore } from '../../store/user'
import { getCaptcha } from '../../api/auth'

const router = useRouter()
const route = useRoute()
const store = useUserStore()

const formRef = ref()
const loading = ref(false)
const captchaImage = ref('')
const captchaId = ref('')

const form = reactive({
  username: 'admin',
  password: 'admin123',
  captcha_code: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  captcha_code: [{ required: true, message: '请输入验证码', trigger: 'blur' }]
}

async function refreshCaptcha() {
  const data = await getCaptcha()
  captchaId.value = data.captcha_id
  captchaImage.value = `data:image/png;base64,${data.image}`
  form.captcha_code = ''
}

async function handleLogin() {
  await formRef.value.validate()
  loading.value = true
  try {
    await store.login(form.username, form.password, captchaId.value, form.captcha_code)
    ElMessage.success('登录成功')
    router.push(route.query.redirect || '/')
  } catch (e) {
    // 登录失败后刷新验证码(密码错/验证码错都刷新)
    refreshCaptcha()
  } finally {
    loading.value = false
  }
}

onMounted(refreshCaptcha)
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <h2 class="title">后台管理系统</h2>
      <p class="subtitle">Vue 3 + Element Plus + FastAPI</p>
      <el-form ref="formRef" :model="form" :rules="rules" size="large" @keyup.enter="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" :prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" show-password :prefix-icon="Lock" />
        </el-form-item>
        <el-form-item prop="captcha_code">
          <div class="captcha-row">
            <el-input v-model="form.captcha_code" placeholder="验证码" class="captcha-input" />
            <img
              v-if="captchaImage"
              :src="captchaImage"
              alt="验证码"
              title="点击刷新"
              class="captcha-img"
              @click="refreshCaptcha"
            />
          </div>
        </el-form-item>
        <el-button type="primary" class="login-btn" :loading="loading" @click="handleLogin">
          登 录
        </el-button>
      </el-form>
      <div class="tips">
        演示账号: admin / admin123(管理员)· test / test123(普通用户)
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1f3a93 0%, #409eff 100%);
}
.login-card {
  width: 400px;
  background: #fff;
  border-radius: 8px;
  padding: 40px 36px 24px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
}
.title {
  text-align: center;
  margin: 0 0 4px;
  color: #333;
}
.subtitle {
  text-align: center;
  color: #999;
  font-size: 13px;
  margin: 0 0 28px;
}
.captcha-row {
  display: flex;
  gap: 10px;
  width: 100%;
}
.captcha-input {
  flex: 1;
}
.captcha-img {
  height: 40px;
  width: 120px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  cursor: pointer;
}
.login-btn {
  width: 100%;
}
.tips {
  margin-top: 16px;
  text-align: center;
  font-size: 12px;
  color: #aaa;
}
</style>
