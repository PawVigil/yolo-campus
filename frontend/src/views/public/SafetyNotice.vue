<template>
  <div class="safety-page">
    <!-- 导航 -->
    <n-layout-header class="public-nav" bordered>
      <div class="nav-content">
        <div class="nav-brand" @click="$router.push('/')">
          <span class="brand-icon">🐾</span>
          <span class="brand-text">PawVigil</span>
        </div>
        <n-menu v-model:value="activeMenu" mode="horizontal" :options="menuOptions" @update:value="onMenuChange" />
        <n-button text @click="$router.push('/login')" class="admin-link">🔧 管理入口</n-button>
      </div>
    </n-layout-header>

    <n-layout-content class="safety-content">
      <n-spin :show="loading">
        <template v-if="!loading && data">
          <h2 class="page-title">⚠️ 安全提醒公示</h2>
          <p class="page-subtitle">管理员基于真实检测数据发布，共 {{ data.items.length }} 条提醒</p>

          <n-empty v-if="data.items.length === 0" description="暂无安全提醒" class="empty-state" />

          <div v-else class="notice-list">
            <n-card v-for="tip in data.items" :key="tip.id" :bordered="false" class="notice-card">
              <div class="notice-header">
                <LocationBadge :name="tip.location_name" />
                <h3 class="notice-title">{{ tip.title }}</h3>
              </div>
              <n-divider />
              <p class="notice-content">{{ tip.content }}</p>
              <div class="notice-footer">
                <n-tag type="warning" size="small" round>📅 {{ tip.published_at?.slice(0, 10) }}</n-tag>
              </div>
            </n-card>
          </div>
        </template>
      </n-spin>
    </n-layout-content>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import LocationBadge from '@/components/LocationBadge.vue'
import { getPublicSafetyTips } from '@/api/public.js'

const router = useRouter()
const activeMenu = ref('safety')
const loading = ref(true)
const data = ref({ items: [] })

const menuOptions = [
  { label: '🏠 实时大屏', key: 'live' },
  { label: '📅 出没日历', key: 'calendar' },
  { label: '🏆 排行榜', key: 'rankings' },
  { label: '🐱 撸猫指南', key: 'guide' },
  { label: '⚠️ 安全提醒', key: 'safety' },
  { label: '📸 社区分享', key: 'community' },
]

function onMenuChange(key) {
  const routeMap = { live: '/', calendar: '/calendar', rankings: '/rankings', guide: '/guide', safety: '/safety', community: '/community' }
  router.push(routeMap[key])
}

onMounted(async () => {
  try {
    data.value = await getPublicSafetyTips()
  } catch (e) {
    console.error('获取安全提醒失败', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.safety-page { min-height: 100vh; background: #f5f7fa; }
.public-nav { background: rgba(255,255,255,0.9); backdrop-filter: blur(10px); position: sticky; top: 0; z-index: 100; }
.nav-content { max-width: 1200px; margin: 0 auto; display: flex; align-items: center; padding: 0 20px; height: 56px; }
.nav-brand { display: flex; align-items: center; gap: 8px; cursor: pointer; margin-right: 24px; }
.brand-icon { font-size: 24px; }
.brand-text { font-size: 18px; font-weight: 700; color: #7c5ce7; }
.admin-link { margin-left: auto; }
.safety-content { max-width: 800px; margin: 0 auto; padding: 24px 20px; }
.page-title { text-align: center; font-size: 28px; margin-bottom: 4px; }
.page-subtitle { text-align: center; color: #909399; margin-bottom: 32px; }
.empty-state { margin-top: 80px; }
.notice-list { display: flex; flex-direction: column; gap: 16px; }
.notice-card { transition: transform 0.2s; border-left: 4px solid #f0a020; }
.notice-card:hover { transform: translateY(-2px); }
.notice-header { display: flex; align-items: center; gap: 12px; }
.notice-title { margin: 0; font-size: 17px; }
.notice-content { font-size: 15px; line-height: 1.7; color: #444; margin: 8px 0; }
.notice-footer { margin-top: 8px; }
</style>
