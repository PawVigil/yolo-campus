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

          <div class="card-fan" @mouseleave="hoveredIndex = -1">
            <div
              v-for="(loc, i) in data.locations"
              :key="loc.name"
              class="fan-card"
              :class="{ 'fan-card--active': hoveredIndex === i }"
              :style="fanCardStyle(i)"
              @mouseenter="hoveredIndex = i"
            >
              <div class="fan-card__front">
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
                      <n-empty v-if="!loc.main_breeds.length" description="暂无品种记录" size="small" :show-icon="false" />
                    </div>
                  </div>
                  <div class="detail-meta">
                    <div class="info-block">
                      <div class="info-label">最佳时段</div>
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
const hoveredIndex = ref(-1)

const locBgColors = {
  '食堂': 'linear-gradient(135deg, #fdf5f0 0%, #f9e4d8 40%, #f0c9b3 100%)',
  '宿舍': 'linear-gradient(135deg, #fdf5f5 0%, #f8dce0 40%, #f0c4cc 100%)',
  '图书馆': 'linear-gradient(135deg, #f0f7f5 0%, #d5eae4 40%, #b8ddd3 100%)',
  '操场': 'linear-gradient(135deg, #faf7f0 0%, #f0e6d0 40%, #e4d4b4 100%)',
  '花园': 'linear-gradient(135deg, #f0f7f0 0%, #d8edd8 40%, #bfe0bf 100%)',
}

const fanRotations = [-10, -5, 0, 5, 10]

function fanCardStyle(i) {
  const total = data.value?.locations?.length || 5
  const angle = fanRotations[i] ?? (i - Math.floor(total / 2)) * 5
  const offsetY = Math.abs(angle) * 1.2
  const rad = (angle * Math.PI) / 180
  const flyX = Math.sin(rad) * 30  // 沿旋转方向的水平偏移
  const locName = data.value.locations[i]?.name
  return {
    '--fan-rotate': `${angle}deg`,
    '--fan-offset-y': `${offsetY}px`,
    '--fan-fly-x': `${flyX}px`,
    zIndex: hoveredIndex.value === i ? 50 : total - i,
    background: locBgColors[locName] || 'linear-gradient(135deg, #fdfcfa 0%, #f4f0e8 100%)',
  }
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
.guide-page { min-height: 100vh; background: var(--color-cream-paper); overflow: visible; }
.guide-page :deep(.n-layout-scroll-container) { overflow: visible !important; }
.guide-page :deep(.n-layout-content) { overflow: visible !important; }
.guide-content { max-width: 1200px; margin: 0 auto; padding: 24px 20px 60px; overflow: visible; }
.page-title { text-align: left; font-size: 28px; margin-bottom: 4px; color: var(--color-forest-ink); }
.page-subtitle { text-align: left; color: var(--color-whisper-gray); margin-bottom: 32px; }
/* ================================
   Card Fan — 扑克牌扇形展开
   ================================ */
.card-fan {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 420px;
  padding: 40px 0 60px;
  perspective: 1200px;
  overflow: visible;
}

.fan-card {
  position: relative;
  flex-shrink: 0;
  width: 300px;
  padding: 20px 24px 24px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.7),
    2px 3px 0 rgba(26, 51, 0, 0.03),
    0 4px 12px rgba(26, 51, 0, 0.08);
  transform:
    rotate(var(--fan-rotate))
    translateY(var(--fan-offset-y));
  transform-origin: bottom center;
  transition:
    transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1),
    box-shadow 0.3s ease,
    border-color 0.3s ease,
    z-index 0s;
  cursor: pointer;
  margin-left: -120px;
}
.fan-card:first-child {
  margin-left: 0;
}

/* 左侧色条 */
.fan-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 10px;
  bottom: 10px;
  width: 4px;
  border-radius: 4px 0 0 4px;
  background: var(--color-forest-ink);
  opacity: 0.2;
}

/* Hover: 沿扇形方向往外飞 */
.fan-card--active {
  transform:
    rotate(var(--fan-rotate))
    translateY(calc(var(--fan-offset-y) - 28px))
    translateX(var(--fan-fly-x, 0px)) !important;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.9),
    4px 8px 0 rgba(26, 51, 0, 0.04),
    0 12px 28px rgba(26, 51, 0, 0.1);
}

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

@media (max-width: 900px) {
  .card-fan {
    flex-direction: column;
    align-items: stretch;
    min-height: auto;
    padding: 20px 0 40px;
    perspective: none;
  }
  .fan-card {
    width: 100%;
    margin-left: 0 !important;
    transform: none !important;
    border-radius: 6px;
  }
  .fan-card--active {
    transform: translateY(-4px) !important;
  }
  .card-details { flex-direction: column; }
}
</style>
