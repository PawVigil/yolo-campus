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
        <router-view :key="route.fullPath" />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authStore } from '@/stores/auth.js'

const router = useRouter()
const route = useRoute()
const collapsed = ref(false)

const menuOptions = [
  { label: '总览看板', key: 'dashboard' },
  { label: '上传检测', key: 'upload' },
  { label: '记录管理', key: 'records' },
  { label: '安全提醒管理', key: 'safety-tips' },
  { label: '社区分享管理', key: 'community' },
  { label: '数据导出', key: 'export' },
]

const activeMenu = computed(() => {
  const seg = route.path.replace('/admin/', '').split('/')[0].split('?')[0]
  return seg || 'dashboard'
})

const pageTitle = computed(() => route.meta.title || '管理端')

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
  background: var(--color-cream-paper);
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--color-pencil-gray);
}
.sider-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px;
  border-bottom: 1px solid var(--color-pencil-gray);
}
.sider-logo {
  font-size: 28px;
}
.sider-title {
  color: var(--color-forest-ink);
  font-size: 16px;
  font-weight: var(--weight-bold);
  white-space: nowrap;
  letter-spacing: 0.02em;
}
.sider-footer {
  margin-top: auto;
  padding: 12px;
  text-align: center;
}
.collapse-btn {
  color: var(--color-pencil-gray);
  font-size: 14px;
}
.admin-header {
  background: var(--color-cream-paper);
  border-bottom: 1px solid var(--color-pencil-gray);
}
.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 56px;
}
.header-title {
  font-family: var(--font-body);
  font-size: 16px;
  font-weight: var(--weight-semibold);
  color: var(--color-forest-ink);
}
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.header-user {
  font-size: 14px;
  color: var(--color-forest-ink);
}
.admin-content {
  padding: 24px;
  background: var(--color-cream-paper);
  min-height: calc(100vh - 56px);
}
</style>
