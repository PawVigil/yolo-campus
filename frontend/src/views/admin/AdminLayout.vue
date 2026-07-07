<template>
  <n-layout class="admin-layout" has-sider>
    <!-- 侧边栏 -->
    <n-layout-sider
      bordered
      collapse-mode="width"
      :collapsed-width="64"
      :width="220"
      :collapsed="collapsed"
      @update:collapsed="collapsed = $event"
      class="admin-sider"
    >
      <div class="sider-header">
        <span class="sider-logo">🐾</span>
        <span v-if="!collapsed" class="sider-title">PawVigil</span>
      </div>
      <n-menu
        v-model:value="activeMenu"
        :collapsed="collapsed"
        :options="menuOptions"
        @update:value="onMenuChange"
      />
      <div class="sider-footer">
        <n-button text @click="toggleCollapsed" class="collapse-btn">
          {{ collapsed ? '▶' : '◀' }}
        </n-button>
      </div>
    </n-layout-sider>

    <!-- 主区域 -->
    <n-layout>
      <n-layout-header bordered class="admin-header">
        <div class="header-content">
          <div class="header-left">
            <span class="header-title">{{ pageTitle }}</span>
          </div>
          <div class="header-right">
            <span class="header-user">👤 {{ authStore.username }}</span>
            <n-button text type="warning" @click="goPublic">🏠 公共端</n-button>
            <n-button text type="error" @click="doLogout">🚪 退出</n-button>
          </div>
        </div>
      </n-layout-header>
      <n-layout-content class="admin-content">
        <router-view />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authStore } from '@/stores/auth.js'

const router = useRouter()
const route = useRoute()
const collapsed = ref(false)
const activeMenu = ref('dashboard')

const menuOptions = [
  { label: '📊 总览看板', key: 'dashboard' },
  { label: '📤 上传检测', key: 'upload' },
  { label: '📋 记录管理', key: 'records' },
  { label: '⚠️ 安全提醒管理', key: 'safety-tips' },
  { label: '📥 数据导出', key: 'export' },
]

const pageTitle = computed(() => route.meta.title || '管理端')

// 根据当前路由初始化菜单高亮
watch(
  () => route.path,
  (path) => {
    const seg = path.split('/').pop()
    activeMenu.value = seg || 'dashboard'
  },
  { immediate: true }
)

function onMenuChange(key) {
  router.push(`/admin/${key}`)
}

function toggleCollapsed() {
  collapsed.value = !collapsed.value
}

function goPublic() {
  router.push('/')
}

function doLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
}
.admin-sider {
  background: #001529;
  display: flex;
  flex-direction: column;
}
.sider-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.sider-logo {
  font-size: 28px;
}
.sider-title {
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  white-space: nowrap;
}
.sider-footer {
  margin-top: auto;
  padding: 12px;
  text-align: center;
}
.collapse-btn {
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
}
.admin-header {
  background: #fff;
}
.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 56px;
}
.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.header-user {
  font-size: 14px;
  color: #666;
}
.admin-content {
  padding: 24px;
  background: #f5f7fa;
  min-height: calc(100vh - 56px);
}
</style>
