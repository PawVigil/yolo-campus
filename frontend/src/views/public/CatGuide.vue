<template>
  <div class="guide-page">
    <!-- 导航 -->
    <PublicNav menu-key="guide" />

    <n-layout-content class="guide-content">
      <n-spin :show="loading">
        <n-empty v-if="!loading && error" description="数据加载失败，请稍后重试" class="error-state" />
        <template v-else-if="!loading && data">
          <h2 class="page-title">🐱 观测指南</h2>
          <p class="page-subtitle">基于各地点真实出没数据，帮你找到最佳观测时机</p>

          <div class="guide-cards">
            <n-card v-for="loc in data.locations" :key="loc.name" :bordered="false" class="guide-card">
              <div class="card-top">
                <div class="card-emoji">{{ loc.emoji }}</div>
                <div class="card-header">
                  <h3 class="card-name">{{ loc.name }}</h3>
                  <div class="card-stars">
                    <span v-for="s in 5" :key="s" class="star" :class="{ active: s <= loc.rating }">★</span>
                    <span class="rating-text">{{ ratingLabel(loc.rating) }}</span>
                  </div>
                </div>
                <n-tag :type="rateColor(loc.appearance_rate)" round>
                  出没率 {{ (loc.appearance_rate * 100).toFixed(0) }}%
                </n-tag>
              </div>

              <n-divider />

              <n-grid :cols="3" :x-gap="16" responsive="screen">
                <n-grid-item>
                  <div class="info-block">
                    <div class="info-label">🏠 主要住户</div>
                    <div class="info-value">
                      <n-tag v-for="b in loc.main_breeds" :key="b.breed_cn" size="small" round class="breed-tag">
                        {{ b.breed_cn }} ({{ b.count }})
                      </n-tag>
                      <n-empty v-if="!loc.main_breeds.length" description="暂无数据" size="small" />
                    </div>
                  </div>
                </n-grid-item>
                <n-grid-item>
                  <div class="info-block">
                    <div class="info-label">⏰ 最佳时段</div>
                    <div class="info-value time-range">{{ loc.best_time?.start || '--' }} - {{ loc.best_time?.end || '--' }}</div>
                  </div>
                </n-grid-item>
                <n-grid-item>
                  <div class="info-block">
                    <div class="info-label">📝 出现规律</div>
                    <div class="info-value pattern-desc">{{ loc.pattern_desc }}</div>
                  </div>
                </n-grid-item>
              </n-grid>

              <n-divider />

              <div class="tip-block">
                <span class="tip-icon">💡</span>
                <span class="tip-text">{{ loc.tip }}</span>
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
import { getGuide } from '@/api/public.js'

const router = useRouter()
const loading = ref(true)
const data = ref(null)
const error = ref(false)



function ratingLabel(r) {
  const map = { 5: '极高', 4: '很高', 3: '一般', 2: '较低', 1: '很低' }
  return map[r] || ''
}

function rateColor(rate) {
  if (rate >= 0.8) return 'success'
  if (rate >= 0.6) return 'info'
  if (rate >= 0.4) return 'warning'
  return 'default'
}

onMounted(async () => {
  error.value = false
  try {
    data.value = await getGuide()
  } catch (e) {
    console.error('获取指南失败', e)
    error.value = true
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.guide-page { min-height: 100vh; background: var(--color-cream-paper); }
.guide-content { max-width: 1100px; margin: 0 auto; padding: 24px 20px 60px; }
.page-title { text-align: center; font-size: 28px; margin-bottom: 4px; color: var(--color-forest-ink); }
.page-subtitle { text-align: center; color: var(--color-whisper-gray); margin-bottom: 32px; }
.guide-cards { display: flex; flex-direction: column; gap: 20px; }
.guide-card { transition: transform var(--transition-fast); border-radius: var(--radius-card); }
.guide-card:hover { transform: translateY(-2px); }
.card-top { display: flex; align-items: center; gap: 16px; }
.card-emoji { font-size: 40px; }
.card-header { flex: 1; }
.card-name { margin: 0 0 4px; font-size: 20px; color: var(--color-forest-ink); }
.star { color: var(--color-pencil-gray); font-size: 18px; }
.star.active { color: var(--color-forest-ink); }
.rating-text { font-size: 13px; color: var(--color-whisper-gray); margin-left: 8px; }
.info-block { padding: 8px 0; }
.info-label { font-size: 14px; font-weight: var(--weight-semibold); margin-bottom: 8px; color: var(--color-forest-ink); }
.info-value { display: flex; gap: 4px; flex-wrap: wrap; }
.time-range { font-size: 20px; font-weight: var(--weight-bold); color: var(--color-forest-ink); }
.pattern-desc { font-size: 14px; color: var(--color-forest-ink); line-height: 1.6; }
.breed-tag { margin: 2px; }
.tip-block { background: var(--surface-highlighter); border-radius: var(--radius-card); padding: 12px 16px; display: flex; align-items: flex-start; gap: 8px; }
.tip-icon { flex-shrink: 0; font-size: 16px; }
.tip-text { font-size: 14px; color: var(--color-forest-ink); line-height: 1.6; }
</style>
