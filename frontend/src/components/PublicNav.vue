<template>
  <n-layout-header class="public-nav" bordered>
    <div class="nav-content">
      <div class="nav-brand" @click="$router.push('/')">
        <span class="brand-icon">🐾</span>
        <span class="brand-text">PawVigil</span>
      </div>
      <n-menu v-model:value="active" mode="horizontal" :options="menuOptions" @update:value="onChange" />
      <n-button text @click="$router.push('/login')" class="admin-link">🔧 管理入口</n-button>
    </div>
  </n-layout-header>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const props = defineProps({ menuKey: { type: String, default: 'live' } })

const router = useRouter()
const route = useRoute()
const active = ref(props.menuKey)

const menuOptions = [
  { label: '🏠 实时大屏', key: 'live' },
  { label: '📅 出没日历', key: 'calendar' },
  { label: '🏆 排行榜', key: 'rankings' },
  { label: '🐱 观测指南', key: 'guide' },
  { label: '⚠️ 安全提醒', key: 'safety' },
  { label: '📸 社区分享', key: 'community' },
]

const routeMap = {
  live: '/', calendar: '/calendar', rankings: '/rankings',
  guide: '/guide', safety: '/safety', community: '/community',
}

function onChange(key) { router.push(routeMap[key]) }

watch(() => props.menuKey, (k) => { active.value = k })
</script>

<style scoped>
.public-nav { background: rgba(255,255,255,0.9); backdrop-filter: blur(10px); position: sticky; top: 0; z-index: 100; }
.nav-content { max-width: 1300px; margin: 0 auto; display: flex; align-items: center; padding: 0 20px; height: 56px; }
.nav-brand { display: flex; align-items: center; gap: 8px; cursor: pointer; margin-right: 24px; }
.brand-icon { font-size: 24px; }
.brand-text { font-size: 18px; font-weight: 700; color: #7c5ce7; }
.admin-link { margin-left: auto; }
</style>
