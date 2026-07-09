<template>
  <div class="live-screen">
    <PublicNav menu-key="live" />

    <div class="live-content">
      <n-spin :show="loading">
        <n-empty v-if="!loading && error" description="数据加载失败，请稍后重试" class="error-state" />
        <template v-else-if="!loading && data">
          <!-- Hero 区域 -->
          <div class="hero-section">
            <h1 class="hero-title">校园动物实时观测</h1>
            <p class="hero-subtitle">YOLOv8 智能检测 · 覆盖 5 个校园地点 · 近 14 天数据</p>
          </div>

          <!-- 统计数字 — 裸数字风格 -->
          <div class="stats-row">
            <StatCard variant="naked" :value="data.stats.total_detections" label="总检测数" />
            <div class="stats-divider" />
            <StatCard variant="naked" :value="data.stats.with_animals" label="有动物记录" />
            <div class="stats-divider" />
            <StatCard variant="naked" :value="data.stats.locations_covered" label="覆盖地点" />
            <div class="stats-divider" />
            <div class="click-stat" @click="router.push('/breeds')">
              <StatCard variant="naked" :value="data.stats.breed_count" label="品种数" />
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
import StatCard from '@/components/StatCard.vue'
import TrendChart from '@/components/TrendChart.vue'
import SafetyTicker from '@/components/SafetyTicker.vue'
import PublicNav from '@/components/PublicNav.vue'
import StickyNote from '@/components/StickyNote.vue'
import { getPublicDashboard } from '@/api/public.js'

const router = useRouter()
const loading = ref(true)
const data = ref(null)
const error = ref(false)
let timer = null

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

/* Hero section */
.hero-section {
  text-align: center;
  padding: 32px 0 48px;
}
.hero-title {
  font-family: var(--font-body);
  font-weight: var(--weight-bold);
  font-size: 40px;
  line-height: 1.15;
  color: var(--color-forest-ink);
  margin: 0 0 12px;
}
.hero-subtitle {
  font-family: var(--font-body);
  font-weight: var(--weight-regular);
  font-size: 16px;
  color: var(--color-whisper-gray);
  margin: 0;
}

/* Hero stats row */
.stats-row {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  gap: 0;
  margin-bottom: 56px;
}
.stats-divider {
  width: 1px;
  height: 60px;
  background: var(--color-pencil-gray);
  margin: 0 32px;
  align-self: center;
}
.click-stat {
  cursor: pointer;
}

/* Section title */
.section-title {
  font-family: var(--font-body);
  font-weight: var(--weight-semibold);
  font-size: var(--text-subheading);
  color: var(--color-forest-ink);
  margin: 0 0 16px;
}

/* Location cards — sticky notes grid */
.location-cards {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
  margin-bottom: 32px;
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
  .location-cards {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  }
  .stats-row {
    flex-wrap: wrap;
    gap: 16px;
  }
  .stats-divider {
    display: none;
  }
}
</style>
