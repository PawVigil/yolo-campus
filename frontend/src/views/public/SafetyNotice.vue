<template>
  <div class="safety-page">
    <!-- 导航 -->
    <PublicNav menu-key="safety" />

    <n-layout-content class="safety-content">
      <n-spin :show="loading">
        <n-empty v-if="!loading && error" description="数据加载失败 — 请检查网络连接后刷新页面" class="error-state" :show-icon="false" />
        <template v-else-if="!loading && data">
          <!-- 顶部警示横幅 -->
          <div class="safety-banner">
            <span class="banner-icon">!</span>
            <span class="banner-text">校园安全提醒 — 基于真实检测数据发布，请注意避让有攻击性的动物</span>
            <span class="banner-count">{{ data.items.length }} 条</span>
          </div>

          <h2 class="page-title">安全提醒公示</h2>
          <p class="page-subtitle">管理员基于真实检测数据发布，共 {{ data.items.length }} 条提醒</p>

          <n-empty v-if="data.items.length === 0" description="暂无安全提醒 — 管理员确认各地点安全后会在此公示" class="empty-state" :show-icon="false" />

          <div v-else class="notice-list">
            <div v-for="(tip, i) in data.items" :key="tip.id" class="notice-card">
              <div class="notice-ribbon">{{ i + 1 }}</div>
              <div class="notice-body">
                <div class="notice-header">
                  <LocationBadge :name="tip.location_name" />
                  <h3 class="notice-title">{{ tip.title }}</h3>
                </div>
                <p class="notice-content">{{ tip.content }}</p>
                <div class="notice-footer">
                  <span class="notice-date">{{ tip.published_at?.slice(0, 10) }}</span>
                </div>
              </div>
            </div>
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

/* Warning banner */
.safety-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  background: linear-gradient(135deg, rgba(232, 153, 112, 0.15), rgba(255, 235, 92, 0.12));
  border: 1px solid rgba(232, 153, 112, 0.3);
  border-radius: var(--radius-card);
  margin-bottom: 28px;
}
.banner-icon { font-size: 22px; flex-shrink: 0; }
.banner-text { flex: 1; font-size: 14px; font-weight: var(--weight-medium); color: var(--color-forest-ink); line-height: 1.5; }
.banner-count { flex-shrink: 0; font-family: var(--font-mono); font-size: 12px; font-weight: var(--weight-semibold); color: var(--color-terracotta); background: rgba(232,153,112,0.15); padding: 3px 10px; border-radius: var(--radius-full); }

.page-title { text-align: left; font-size: 28px; margin-bottom: 4px; color: var(--color-forest-ink); }
.page-subtitle { text-align: left; color: var(--color-whisper-gray); margin-bottom: 28px; }
.empty-state { margin-top: 80px; }

/* Notice list */
.notice-list { display: flex; flex-direction: column; gap: 14px; }

/* Notice card — left ribbon marker */
.notice-card {
  display: flex;
  gap: 0;
  background: var(--color-cream-paper);
  border: 1px solid var(--color-pencil-gray);
  border-radius: var(--radius-card);
  overflow: hidden;
  transition: all var(--transition-fast);
}
.notice-card:hover {
  box-shadow: var(--shadow-subtle-2);
  transform: translateY(-1px);
}

/* Number ribbon */
.notice-ribbon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  flex-shrink: 0;
  font-family: var(--font-mono);
  font-size: 16px;
  font-weight: var(--weight-bold);
  color: var(--color-cream-paper);
  background: var(--color-terracotta);
  writing-mode: vertical-rl;
  letter-spacing: 0.1em;
  padding: 12px 0;
}

.notice-body {
  flex: 1;
  padding: 18px 20px;
}

.notice-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}
.notice-title { margin: 0; font-size: 17px; color: var(--color-forest-ink); font-weight: var(--weight-semibold); }
.notice-content { font-size: 15px; line-height: 1.7; color: var(--color-forest-ink); margin: 0 0 10px; }
.notice-footer { display: flex; align-items: center; }
.notice-date { font-size: 12px; color: var(--color-whisper-gray); }
</style>
