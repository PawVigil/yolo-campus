<template>
  <div class="live-screen">
    <!-- 顶部导航 -->
    <PublicNav menu-key="live" />

    <!-- 正文 -->
    <n-layout-content class="live-content">
      <n-spin :show="loading">
        <template v-if="!loading && data">
          <div class="time-range-badge">
            <span class="badge-text">📅 近 14 天数据</span>
          </div>

          <!-- 统计卡片 -->
          <n-grid :cols="4" :x-gap="16" :y-gap="16" responsive="screen" class="stats-row">
            <n-grid-item>
              <StatCard icon="CameraOutline" :value="data.stats.total_detections" label="总检测数" color="#7c5ce7" />
            </n-grid-item>
            <n-grid-item>
              <StatCard icon="PawOutline" :value="data.stats.with_animals" label="有动物记录" color="#18a058" />
            </n-grid-item>
            <n-grid-item>
              <StatCard icon="LocationOutline" :value="data.stats.locations_covered" label="覆盖地点" color="#f0a020" />
            </n-grid-item>
            <n-grid-item>
              <div class="click-stat" @click="router.push('/breeds')">
                <StatCard icon="GitBranchOutline" :value="data.stats.breed_count" label="品种数" color="#2080f0" />
              </div>
            </n-grid-item>
          </n-grid>

          <!-- 地点状态卡片 -->
          <h3 class="section-title">📍 各地点实时状态</h3>
          <n-grid :cols="5" :x-gap="16" :y-gap="16" responsive="screen" class="location-cards">
            <n-grid-item v-for="loc in data.location_status" :key="loc.id">
              <n-card :bordered="false" class="location-card" :class="`status-${loc.status}`">
                <div class="loc-header">
                  <span class="loc-emoji">{{ loc.emoji }}</span>
                  <span class="loc-name">{{ loc.name }}</span>
                  <n-tag :type="statusType(loc.status)" size="small" round>{{ statusLabel(loc.status) }}</n-tag>
                </div>
                <div class="loc-body">
                  <div v-if="loc.recent_breeds.length > 0" class="loc-breeds">
                    <n-tag v-for="b in loc.recent_breeds" :key="b" size="tiny" round class="breed-tag">{{ b }}</n-tag>
                  </div>
                  <div v-else class="loc-empty">暂无记录</div>
                </div>
                <div class="loc-time" v-if="loc.last_detect_time">
                  最近：{{ formatTime(loc.last_detect_time) }}
                </div>
              </n-card>
            </n-grid-item>
          </n-grid>

          <!-- 趋势图 -->
          <n-card :bordered="false" class="chart-card">
            <TrendChart :data="data.trend_14d" title="📈 近14天检测趋势" height="320px" color="#7c5ce7" />
          </n-card>

          <!-- 安全提醒滚动条 -->
          <SafetyTicker :tips="data.safety_tips" />
        </template>
      </n-spin>
    </n-layout-content>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { CameraOutline, PawOutline, LocationOutline, GitBranchOutline } from '@vicons/ionicons5'
import StatCard from '@/components/StatCard.vue'
import TrendChart from '@/components/TrendChart.vue'
import SafetyTicker from '@/components/SafetyTicker.vue'
import PublicNav from '@/components/PublicNav.vue'
import { getPublicDashboard } from '@/api/public.js'

const loading = ref(true)
const data = ref(null)
let timer = null

function statusType(status) {
  return status === 'active' ? 'success' : status === 'resting' ? 'warning' : 'default'
}

function statusLabel(status) {
  return status === 'active' ? '🟢 当天' : status === 'resting' ? '🟡 昨天' : '⚪ 更早'
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
  try {
    data.value = await getPublicDashboard()
  } catch (e) {
    console.error('获取大屏数据失败', e)
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
  background: linear-gradient(180deg, #f5f3ff 0%, #f5f7fa 100%);
}
.time-range-badge {
  margin-bottom: 16px;
  text-align: center;
}
.badge-text {
  display: inline-block;
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(135deg, #667eea, #764ba2);
  padding: 8px 28px;
  border-radius: 999px;
  letter-spacing: 1px;
}
.live-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 20px;
}
.stats-row {
  margin-bottom: 24px;
}
.click-stat {
  cursor: pointer;
  transition: transform 0.2s;
}
.click-stat:hover {
  transform: scale(1.03);
}
.section-title {
  margin: 24px 0 16px;
  font-size: 18px;
}
.location-card {
  transition: all 0.3s;
  min-height: 140px;
}
.location-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}
.location-card.status-active {
  border-left: 4px solid #18a058;
}
.location-card.status-resting {
  border-left: 4px solid #f0a020;
}
.location-card.status-no_record {
  border-left: 4px solid #d0d0d0;
}
.loc-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.loc-emoji {
  font-size: 24px;
}
.loc-name {
  font-weight: 600;
  flex: 1;
}
.loc-breeds {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}
.loc-empty {
  color: #909399;
  font-size: 13px;
}
.loc-time {
  margin-top: 12px;
  font-size: 12px;
  color: #909399;
}
.chart-card {
  margin: 24px 0;
}
</style>
