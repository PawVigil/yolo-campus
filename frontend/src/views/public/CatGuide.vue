<template>
  <div class="guide-page">
    <!-- 导航 -->
    <PublicNav menu-key="guide" />

    <n-layout-content class="guide-content">
      <n-spin :show="loading">
        <n-empty v-if="!loading && error" description="数据加载失败 — 请检查网络连接后刷新页面" class="error-state" :show-icon="false" />
        <template v-else-if="!loading && data">
          <h2 class="page-title">观测指南</h2>
          <p class="page-subtitle">基于各地点真实出没数据，帮你找到最佳观测时机</p>

          <div class="guide-cards">
            <div v-for="loc in data.locations" :key="loc.name" class="guide-card" :style="{ background: locBgColors[loc.name] || 'var(--surface-cream)' }">
              <div class="card-top">
                <div class="card-emoji">{{ loc.emoji }}</div>
                <div class="card-header">
                  <h3 class="card-name">{{ loc.name }}</h3>
                  <div class="card-stars">
                    <span v-for="s in 5" :key="s" class="star" :class="{ active: s <= loc.rating }">★</span>
                    <span class="rating-text">{{ ratingLabel(loc.rating) }}</span>
                  </div>
                </div>
                <InkTag variant="ink">
                  出没率 {{ (loc.appearance_rate * 100).toFixed(0) }}%
                </InkTag>
              </div>

              <div class="card-divider"></div>

              <div class="card-details">
                <div class="detail-breeds">
                  <div class="info-label">主要住户</div>
                  <div class="info-value">
                    <InkTag v-for="b in loc.main_breeds" :key="b.breed_cn" variant="mint" class="breed-tag">
                      {{ b.breed_cn }} ({{ b.count }})
                    </InkTag>
                    <n-empty v-if="!loc.main_breeds.length" description="暂无品种记录 — 多去逛逛，也许能发现新朋友" size="small" :show-icon="false" />
                  </div>
                </div>
                <div class="detail-meta">
                  <div class="info-block">
                    <div class="info-label">⏰ 最佳时段</div>
                    <div class="info-value time-range">{{ loc.best_time?.start || '--' }} - {{ loc.best_time?.end || '--' }}</div>
                  </div>
                  <div class="info-block">
                    <div class="info-label">出现规律</div>
                    <div class="info-value pattern-desc">{{ loc.pattern_desc }}</div>
                  </div>
                </div>
              </div>

              <div class="card-divider"></div>

              <div class="tip-block">
                <span class="tip-text">{{ loc.tip }}</span>
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
import InkTag from '@/components/InkTag.vue'
import { getGuide } from '@/api/public.js'

const router = useRouter()
const loading = ref(true)
const data = ref(null)
const error = ref(false)

const locBgColors = {
  '食堂': 'var(--surface-terracotta)',
  '宿舍': 'var(--surface-blush)',
  '图书馆': 'var(--surface-teal)',
  '操场': 'var(--surface-sand)',
  '花园': 'var(--surface-mint)',
}



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
.page-title { text-align: left; font-size: 28px; margin-bottom: 4px; color: var(--color-forest-ink); }
.page-subtitle { text-align: left; color: var(--color-whisper-gray); margin-bottom: 32px; }
.guide-cards { display: flex; flex-direction: column; gap: 24px; }
.guide-card {
  position: relative;
  padding: 20px 24px 24px;
  border-radius: 6px 14px 14px 6px;
  box-shadow:
    2px 2px 0 rgba(26, 51, 0, 0.04),
    0 1px 4px rgba(26, 51, 0, 0.05);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
  max-width: 95%;
}
.guide-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 10px;
  bottom: 10px;
  width: 4px;
  border-radius: 4px 0 0 4px;
  background: var(--color-forest-ink);
  opacity: 0.3;
}
/* Zig-zag: even cards shifted right + reversed */
.guide-card:nth-child(even) {
  margin-left: auto;
}
.guide-card:nth-child(even) .card-top {
  flex-direction: row-reverse;
}
.guide-card:nth-child(even) .card-details {
  flex-direction: row-reverse;
}
.guide-card:hover { transform: translateY(-2px); box-shadow: 3px 3px 0 rgba(26,51,0,0.06), 0 4px 12px rgba(26,51,0,0.08); }

.card-divider { height: 1px; background: rgba(26,51,0,0.1); margin: 14px 0; }

.card-top { display: flex; align-items: center; gap: 16px; }
.card-emoji { font-size: 40px; flex-shrink: 0; }
.card-header { flex: 1; }
.card-name { margin: 0 0 4px; font-size: 20px; color: var(--color-forest-ink); }
.star { color: var(--color-pencil-gray); font-size: 18px; }
.star.active { color: var(--color-forest-ink); }
.rating-text { font-size: 13px; color: var(--color-whisper-gray); margin-left: 8px; }

/* Card details — breeds wider, meta narrower (break 3-equal) */
.card-details {
  display: flex;
  gap: 20px;
}
.detail-breeds {
  flex: 1.5;
}
.detail-meta {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-block { padding: 4px 0; }
.info-label { font-size: 14px; font-weight: var(--weight-semibold); margin-bottom: 8px; color: var(--color-forest-ink); }
.info-value { display: flex; gap: 4px; flex-wrap: wrap; }
.time-range { font-family: var(--font-mono); font-size: 20px; font-weight: var(--weight-bold); color: var(--color-forest-ink); font-feature-settings: 'tnum'; }
.pattern-desc { font-size: 14px; color: var(--color-forest-ink); line-height: 1.6; }
.breed-tag { margin: 2px; }
.tip-block { background: var(--surface-highlighter); border-radius: var(--radius-card); padding: 12px 16px; display: flex; align-items: flex-start; gap: 8px; }
.tip-icon { flex-shrink: 0; font-size: 16px; }
.tip-text { font-size: 14px; color: var(--color-forest-ink); line-height: 1.6; }

@media (max-width: 768px) {
  .guide-card { max-width: 100%; }
  .guide-card:nth-child(even) { margin-left: 0; }
  .guide-card:nth-child(even) .card-top,
  .guide-card:nth-child(even) .card-details { flex-direction: row; }
  .card-details { flex-direction: column; }
}
</style>
