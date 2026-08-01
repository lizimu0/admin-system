import { useUserStore } from '../store/user'

/**
 * 按钮级权限指令
 * 用法: <el-button v-permission="'user:add'">新增</el-button>
 * 无权限时移除该元素。
 */
export const permission = {
  mounted(el, binding) {
    const store = useUserStore()
    const code = binding.value
    if (code && !store.hasPermission(code)) {
      el.parentNode?.removeChild(el)
    }
  }
}
