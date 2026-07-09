<template>
  <div class="nav-wrapper">
    <div class="nav-pill">
      <div class="nav-brand" @click="$router.push('/')">
        <span class="brand-mark">🐾</span>
        <span class="brand-text">PawVigil</span>
      </div>
      <n-menu
        v-model:value="active"
        mode="horizontal"
        :options="menuOptions"
        @update:value="onChange"
      />
      <n-button
        text
        class="admin-link"
        @click="$router.push('/login')"
      >
        管理入口
      </n-button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const props = defineProps({ menuKey: { type: String, default: 'live' } })

const router = useRouter()
const route = useRoute()
const active = ref(props.menuKey)

const menuOptions = [
  { label: '实时大屏', key: 'live' },
  { label: '出没日历', key: 'calendar' },
  { label: '排行榜', key: 'rankings' },
  { label: '观测指南', key: 'guide' },
  { label: '安全提醒', key: 'safety' },
  { label: '社区分享', key: 'community' },
]

const routeMap = {
  live: '/', calendar: '/calendar', rankings: '/rankings',
  guide: '/guide', safety: '/safety', community: '/community',
}

function onChange(key) { router.push(routeMap[key]) }

watch(() => props.menuKey, (k) => { active.value = k })
</script>

<style scoped>
.nav-wrapper {
  display: flex;
  justify-content: center;
  padding: 16px 24px 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-pill {
  display: flex;
  align-items: center;
  width: 100%;
  max-width: var(--page-max-width);
  background: var(--color-cream-paper);
  border: 1px solid var(--color-pencil-gray);
  border-radius: var(--radius-nav);
  padding: 8px 20px;
  box-shadow: var(--shadow-glow);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  margin-right: 24px;
  flex-shrink: 0;
}

.brand-mark {
  font-size: 24px;
  line-height: 1;
}

.brand-text {
  font-family: var(--font-body);
  font-weight: var(--weight-bold);
  font-size: 18px;
  letter-spacing: 0.02em;
  color: var(--color-forest-ink);
}

.admin-link {
  margin-left: auto;
  flex-shrink: 0;
}

/* Horizontal menu: current page indicator */
:deep(.n-menu .n-menu-item-content) {
  font-weight: var(--weight-medium);
  font-size: 14px;
  padding: 6px 12px;
  border-radius: var(--radius-button);
  transition: background var(--transition-fast);
}
:deep(.n-menu .n-menu-item-content:hover) {
  background: rgba(26, 51, 0, 0.05);
}
:deep(.n-menu .n-menu-item--selected .n-menu-item-content) {
  background: var(--color-highlighter-yellow) !important;
  font-weight: var(--weight-semibold);
}
</style>
