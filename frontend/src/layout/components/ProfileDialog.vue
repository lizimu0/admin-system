<script setup>
import { reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { changePassword, updateProfile } from '../../api/auth'
import { useUserStore } from '../../store/user'

const props = defineProps({
  modelValue: Boolean
})
const emit = defineEmits(['update:modelValue'])

const store = useUserStore()
const activeTab = ref('profile')

const profileFormRef = ref()
const pwdFormRef = ref()

const profileForm = reactive({
  nickname: '',
  email: '',
  phone: ''
})

const pwdForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const pwdRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (_, value, callback) => {
        if (value !== pwdForm.new_password) callback(new Error('两次输入的密码不一致'))
        else callback()
      },
      trigger: 'blur'
    }
  ]
}

// 每次打开弹窗时同步当前用户信息
watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      activeTab.value = 'profile'
      Object.assign(profileForm, {
        nickname: store.userInfo?.nickname || '',
        email: store.userInfo?.email || '',
        phone: store.userInfo?.phone || ''
      })
      Object.assign(pwdForm, { old_password: '', new_password: '', confirm_password: '' })
    }
  }
)

async function submitProfile() {
  await profileFormRef.value.validate()
  const data = await updateProfile(profileForm)
  store.userInfo = data
  ElMessage.success('资料修改成功')
  emit('update:modelValue', false)
}

async function submitPassword() {
  await pwdFormRef.value.validate()
  await changePassword({
    old_password: pwdForm.old_password,
    new_password: pwdForm.new_password
  })
  ElMessage.success('密码修改成功,请重新登录')
  emit('update:modelValue', false)
  store.logout()
}
</script>

<template>
  <el-dialog
    :model-value="props.modelValue"
    title="个人中心"
    width="460px"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <el-tabs v-model="activeTab">
      <el-tab-pane label="基本信息" name="profile">
        <el-form ref="profileFormRef" :model="profileForm" label-width="80px">
          <el-form-item label="用户名">
            <el-input :model-value="store.userInfo?.username" disabled />
          </el-form-item>
          <el-form-item label="昵称">
            <el-input v-model="profileForm.nickname" placeholder="显示名称" />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="profileForm.email" placeholder="邮箱地址" />
          </el-form-item>
          <el-form-item label="手机号">
            <el-input v-model="profileForm.phone" placeholder="手机号码" />
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="修改密码" name="password">
        <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="80px">
          <el-form-item label="原密码" prop="old_password">
            <el-input v-model="pwdForm.old_password" type="password" show-password placeholder="请输入原密码" />
          </el-form-item>
          <el-form-item label="新密码" prop="new_password">
            <el-input v-model="pwdForm.new_password" type="password" show-password placeholder="至少 6 位" />
          </el-form-item>
          <el-form-item label="确认密码" prop="confirm_password">
            <el-input v-model="pwdForm.confirm_password" type="password" show-password placeholder="再次输入新密码" />
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>

    <template #footer>
      <el-button @click="emit('update:modelValue', false)">取消</el-button>
      <el-button type="primary" @click="activeTab === 'profile' ? submitProfile() : submitPassword()">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>
