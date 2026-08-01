<script setup>
import { useRoute, useRouter } from 'vue-router'
import { Close } from '@element-plus/icons-vue'
import { useTabsStore } from '../../store/tabs'

const route = useRoute()
const router = useRouter()
const tabsStore = useTabsStore()

function handleClick(path) {
  if (route.path === path) return
  tabsStore.setActive(path)
  router.push(path)
}

function handleClose(path) {
  const next = tabsStore.closeTab(path)
  if (route.path === path && next) {
    router.push(next)
  } else if (route.path === path) {
    router.push('/dashboard')
  }
}
</script>

<template>
  <div class="tags-view">
    <div
      v-for="tab in tabsStore.tabs"
      :key="tab.path"
      class="tag"
      :class="{ active: tab.active }"
      @click="handleClick(tab.path)"
    >
      <span>{{ tab.title }}</span>
      <el-icon v-if="tab.closable" class="close" @click.stop="handleClose(tab.path)">
        <Close />
      </el-icon>
    </div>
  </div>
</template>

<style scoped>
.tags-view {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  overflow-x: auto;
}
.tag {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  font-size: 13px;
  border-radius: 3px;
  border: 1px solid #dcdfe6;
  background: #fff;
  color: #666;
  cursor: pointer;
  white-space: nowrap;
  user-select: none;
}
.tag:hover {
  color: #409eff;
}
.tag.active {
  background: #409eff;
  border-color: #409eff;
  color: #fff;
}
.close {
  font-size: 12px;
}
.close:hover {
  opacity: 0.8;
}
</style>
