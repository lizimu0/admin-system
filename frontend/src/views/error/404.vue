<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <div class="error-page">
    <div class="code">404</div>
    <div class="desc">抱歉,你访问的页面不存在</div>
    <el-button type="primary" @click="router.push('/dashboard')">返回首页</el-button>
  </div>
</template>

<style scoped>
.error-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  background: #f0f2f5;
}
.code {
  font-size: 96px;
  font-weight: 700;
  color: #e6a23c;
  line-height: 1;
}
.desc {
  color: #666;
  font-size: 16px;
}
</style>
