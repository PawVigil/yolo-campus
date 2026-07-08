<template>
  <div class="safety-page">
    <!-- 导航 -->
    <PublicNav menu-key="safety" />

    <n-layout-content class="safety-content">
      <n-spin :show="loading">
        <n-empty v-if="!loading && error" description="数据加载失败，请稍后重试" class="error-state" />
        <template v-else-if="!loading && data">
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
import PublicNav from '@/components/PublicNav.vue'
import LocationBadge from '@/components/LocationBadge.vue'
import { getPublicSafetyTips } from '@/api/public.js'

const router = useRouter()
const loading = ref(true)
const data = ref({ items: [] })
const error = ref(false)



onMounted(async () => {
  error.value = false
  try {
    data.value = await getPublicSafetyTips()
  } catch (e) {
    console.error('获取安全提醒失败', e)
    error.value = true
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.safety-page { min-height: 100vh; background: var(--color-cream-paper); }
.safety-content { max-width: 800px; margin: 0 auto; padding: 24px 20px 60px; }
.page-title { text-align: center; font-size: 28px; margin-bottom: 4px; color: var(--color-forest-ink); }
.page-subtitle { text-align: center; color: var(--color-whisper-gray); margin-bottom: 32px; }
.empty-state { margin-top: 80px; }
.notice-list { display: flex; flex-direction: column; gap: 16px; }
.notice-card { transition: transform var(--transition-fast); border-left: 3px solid var(--color-terracotta); }
.notice-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-subtle-2); }
.notice-header { display: flex; align-items: center; gap: 12px; }
.notice-title { margin: 0; font-size: 17px; color: var(--color-forest-ink); }
.notice-content { font-size: 15px; line-height: 1.7; color: var(--color-forest-ink); margin: 8px 0; }
.notice-footer { margin-top: 8px; }
</style>
