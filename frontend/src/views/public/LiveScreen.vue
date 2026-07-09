<template>
  <div class="live-screen">
    <PublicNav menu-key="live" />

    <div class="live-content">
      <n-spin :show="loading">
        <n-empty v-if="!loading && error" description="数据加载失败 — 请检查网络连接后刷新页面" class="error-state" :show-icon="false" />
        <template v-else-if="!loading && data">
          <!-- Hero 区域 — 墨印头条 -->
          <div class="hero-section">
            <div class="hero-bg-number" aria-hidden="true">{{ data.stats.total_detections }}</div>
            <div class="hero-top">
              <div class="hero-title-col">
                <h1 class="hero-title">校园动物实时观测</h1>
                <p class="hero-subtitle">YOLOv8 智能检测 · 覆盖 {{ data.stats.locations_covered }} 个校园地点 · 近 14 天数据</p>
              </div>
              <div class="hero-stat-primary">
                <span class="hero-stat-number">{{ animatedNumber }}</span>
                <span class="hero-stat-label">总检测数</span>
              </div>
            </div>
            <div class="hero-divider"></div>
            <div class="hero-stats-secondary">
              <span class="stats-sec-item">{{ data.stats.with_animals }} <em>有动物</em></span>
              <span class="stats-sep">·</span>
              <span class="stats-sec-item">{{ data.stats.locations_covered }} <em>覆盖地点</em></span>
              <span class="stats-sep">·</span>
              <span class="stats-sec-item click-stat" @click="router.push('/breeds')">{{ data.stats.breed_count }} <em>品种数</em></span>
            </div>
          </div>

          <!-- 地点状态卡片 — pastel 满铺背景 -->
          <h3 class="section-title">各地点实时状态</h3>
          <div class="location-cards">
            <StickyNote
              v-for="(loc, i) in data.location_status"
              :key="loc.id"
              :color="locColors[loc.name] || 'var(--surface-cream)'"
              :rotate="rotations[i]"
            >
              <div class="loc-header">
                <span class="loc-emoji">{{ loc.emoji }}</span>
                <span class="loc-name">{{ loc.name }}</span>
                <span class="loc-status" :class="`status-${loc.status}`">
                  <span class="status-dot"></span>
                  {{ statusLabel(loc.status) }}
                </span>
              </div>
              <div class="loc-body">
                <div v-if="loc.recent_breeds?.length" class="loc-breeds">
                  <span v-for="b in loc.recent_breeds" :key="b" class="breed-tag">{{ b }}</span>
                </div>
                <div v-else class="loc-empty">暂无记录</div>
              </div>
              <div class="loc-time" v-if="loc.last_detect_time">
                最近：{{ formatTime(loc.last_detect_time) }}
              </div>
            </StickyNote>
          </div>

          <!-- 趋势图 -->
          <div class="chart-card">
            <TrendChart :data="data.trend_14d" title="近14天检测趋势" height="320px" />
          </div>

          <!-- 安全提醒滚动条 -->
          <SafetyTicker :tips="data.safety_tips" />
        </template>
      </n-spin>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import TrendChart from '@/components/TrendChart.vue'
import SafetyTicker from '@/components/SafetyTicker.vue'
import PublicNav from '@/components/PublicNav.vue'
import StickyNote from '@/components/StickyNote.vue'
import { getPublicDashboard } from '@/api/public.js'

const router = useRouter()
const loading = ref(true)
const data = ref(null)
const error = ref(false)
const animatedNumber = ref(0)
let timer = null
let animFrame = null

function animateCountUp(target) {
  if (animFrame) cancelAnimationFrame(animFrame)
  const duration = 1200
  const start = performance.now()
  const from = animatedNumber.value
  const diff = target - from
  function tick(now) {
    const elapsed = now - start
    const progress = Math.min(elapsed / duration, 1)
    // ease-out cubic
    const eased = 1 - Math.pow(1 - progress, 3)
    animatedNumber.value = Math.round(from + diff * eased)
    if (progress < 1) animFrame = requestAnimationFrame(tick)
  }
  animFrame = requestAnimationFrame(tick)
}

const locColors = {
  '食堂': 'var(--surface-terracotta)',
  '宿舍': 'var(--surface-blush)',
  '图书馆': 'var(--surface-teal)',
  '操场': 'var(--surface-sand)',
  '花园': 'var(--surface-mint)',
}
const rotations = [-0.8, 0.5, -0.4, 0.7, -0.3]

function statusLabel(status) {
  return status === 'active' ? '今天活跃' : status === 'resting' ? '昨天有记录' : '近期无记录'
}

function formatTime(t) {
  if (!t) return ''
  const d = new Date(t)
  const now = new Date()
  const diffMin = Math.floor((now - d) / 60000)
  if (diffMin < 60) return `${diffMin}分钟前`
  if (diffMin < 1440) return `${Math.floor(diffMin / 60)}小时前`
  return `${Math.floor(diffMin / 1440)}天前`
}

async function fetchData() {
  error.value = false
  try {
    data.value = await getPublicDashboard()
    animateCountUp(data.value.stats.total_detections)
  } catch (e) {
    console.error('获取大屏数据失败', e)
    error.value = true
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
  timer = setInterval(fetchData, 30000)
})

onUnmounted(() => {
  clearInterval(timer)
  if (animFrame) cancelAnimationFrame(animFrame)
})
</script>

<style scoped>
.live-screen {
  min-height: 100vh;
  background: var(--color-cream-paper);
}

.live-content {
  max-width: var(--page-max-width);
  margin: 0 auto;
  padding: 40px 20px 60px;
}

/* Hero section — ink-stamp headline */
.hero-section {
  position: relative;
  text-align: left;
  padding: 32px 0 48px;
  overflow: hidden;
}

/* Giant watermark number behind everything */
.hero-bg-number {
  position: absolute;
  right: -40px;
  top: -30px;
  font-family: var(--font-mono);
  font-weight: 900;
  font-size: 340px;
  line-height: 1;
  color: var(--color-forest-ink);
  opacity: 0.035;
  pointer-events: none;
  user-select: none;
  letter-spacing: -0.06em;
  z-index: 0;
}

.hero-top {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 40px;
  margin-bottom: 24px;
}
.hero-title-col {
  flex: 1;
}
.hero-title {
  font-family: var(--font-body);
  font-weight: var(--weight-semibold);
  font-size: 36px;
  line-height: 1.15;
  color: var(--color-forest-ink);
  margin: 0 0 8px;
  letter-spacing: -0.01em;
}
.hero-subtitle {
  font-family: var(--font-body);
  font-weight: var(--weight-regular);
  font-size: 15px;
  color: var(--color-whisper-gray);
  margin: 0;
  letter-spacing: 0.02em;
}

/* Primary stat — massive ink-stamp number */
.hero-stat-primary {
  text-align: right;
  flex-shrink: 0;
  position: relative;
}
.hero-stat-primary::before {
  content: '';
  position: absolute;
  inset: -12px -20px;
  background: radial-gradient(ellipse at 60% 50%, var(--color-forest-ink) 0%, transparent 70%);
  opacity: 0.03;
  border-radius: var(--radius-card);
  z-index: -1;
}
.hero-stat-number {
  display: block;
  font-family: var(--font-mono);
  font-weight: 900;
  font-size: 220px;
  line-height: 0.85;
  color: var(--color-forest-ink);
  font-feature-settings: 'tnum';
  letter-spacing: -0.05em;
  text-shadow: 2px 2px 0 rgba(0,0,0,0.03);
}
.hero-stat-label {
  display: block;
  font-family: var(--font-body);
  font-weight: var(--weight-medium);
  font-size: var(--text-caption);
  color: var(--color-whisper-gray);
  margin-top: 8px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

/* Divider — heavy rule like newspaper */
.hero-divider {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 2px;
  background: var(--color-forest-ink);
  margin-bottom: 16px;
}

/* Secondary stats row */
.hero-stats-secondary {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 16px;
  font-family: var(--font-body);
  font-size: var(--text-body);
  color: var(--color-forest-ink);
}
.stats-sec-item {
  font-weight: var(--weight-semibold);
  font-family: var(--font-mono);
  font-feature-settings: 'tnum';
}
.stats-sec-item em {
  font-style: normal;
  font-weight: var(--weight-regular);
  color: var(--color-whisper-gray);
  margin-left: 2px;
}
.stats-sep {
  color: var(--color-pencil-gray);
  font-weight: var(--weight-regular);
}
.click-stat {
  cursor: pointer;
  transition: color var(--transition-fast);
}
.click-stat:hover {
  color: var(--color-terracotta);
}

/* Section title */
.section-title {
  font-family: var(--font-body);
  font-weight: var(--weight-semibold);
  font-size: var(--text-subheading);
  color: var(--color-forest-ink);
  margin: 0 0 16px;
}

/* Location cards — uneven sized sticky notes */
.location-cards {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 32px;
}
/* Size differentiation */
.location-cards > :nth-child(1) { flex: 1.25; }
.location-cards > :nth-child(2),
.location-cards > :nth-child(3) { flex: 1; }
.location-cards > :nth-child(4),
.location-cards > :nth-child(5) { flex: 0.85; }
/* Vertical offset — staggered like real sticky notes */
.location-cards > :nth-child(even) {
  margin-top: 36px;
}

.loc-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.loc-emoji {
  font-size: 24px;
  line-height: 1;
}
.loc-name {
  font-family: var(--font-body);
  font-weight: var(--weight-semibold);
  font-size: var(--text-body);
  color: var(--color-forest-ink);
  flex: 1;
}

/* Status indicator */
.loc-status {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-family: var(--font-body);
  font-size: var(--text-caption);
  color: var(--color-forest-ink);
  background: var(--color-cream-paper);
  padding: 2px 10px;
  border-radius: var(--radius-full);
}
.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-pencil-gray);
}
.status-active .status-dot {
  background: var(--color-forest-ink);
}
.status-resting .status-dot {
  background: var(--color-terracotta);
}

.loc-breeds {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}
.breed-tag {
  font-family: var(--font-body);
  font-size: var(--text-caption);
  color: var(--color-forest-ink);
  background: var(--color-cream-paper);
  padding: 2px 8px;
  border-radius: var(--radius-full);
}
.loc-empty {
  font-family: var(--font-body);
  color: var(--color-whisper-gray);
  font-size: 13px;
}
.loc-time {
  margin-top: 12px;
  font-family: var(--font-body);
  font-size: var(--text-caption);
  color: var(--color-whisper-gray);
}

/* Chart */
.chart-card {
  background: var(--color-cream-paper);
  border: 1px solid var(--color-pencil-gray);
  border-radius: var(--radius-card);
  padding: var(--card-padding);
  margin: 32px 0;
}

.error-state {
  margin-top: 80px;
}

@media (max-width: 900px) {
  .hero-top {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  .hero-bg-number {
    font-size: 200px;
    right: -20px;
    top: -10px;
  }
  .hero-stat-number {
    font-size: 120px;
  }
  .location-cards {
    flex-wrap: wrap;
    gap: 12px;
  }
  .location-cards > * {
    flex: 1 1 160px !important;
  }
  .location-cards > :nth-child(even) {
    margin-top: 0;
  }
  .hero-stats-secondary {
    flex-wrap: wrap;
    gap: 8px;
  }
}
</style>
