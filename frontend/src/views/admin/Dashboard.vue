<template>
  <div class="dashboard-page">
    <n-spin :show="loading">
      <template v-if="!loading && data">
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
            <StatCard icon="AlertCircleOutline" :value="data.stats.published_tips" label="已发布提醒" color="#2080f0" />
          </n-grid-item>
        </n-grid>

        <n-grid :cols="2" :x-gap="16" responsive="screen" class="charts-row">
          <!-- 地点排行：横向柱状图 -->
          <n-grid-item>
            <n-card :bordered="false" title="📍 各地点检测排行">
              <div ref="barChartRef" class="chart-box"></div>
            </n-card>
          </n-grid-item>
          <!-- 品种 TOP5 -->
          <n-grid-item>
            <n-card :bordered="false" title="🏅 品种出现次数 TOP5">
              <div class="top5-list">
                <div v-for="(item, idx) in data.breed_top5" :key="item.breed" class="top5-item">
                  <span class="top5-rank" :class="`rank-${idx + 1}`">#{{ idx + 1 }}</span>
                  <span class="top5-breed">{{ item.breed }}</span>
                  <n-progress type="line" :percentage="item.count / maxCount * 100" :height="24" :border-radius="4" :color="rankColor(idx)" :indicator-placement="'inside'">
                    {{ item.count }} 次
                  </n-progress>
                </div>
              </div>
            </n-card>
          </n-grid-item>
        </n-grid>

        <!-- 趋势图 -->
        <n-card :bordered="false" title="📈 近14天检测趋势" class="trend-card">
          <TrendChart :data="data.trend_14d" height="320px" color="#7c5ce7" />
        </n-card>
      </template>
    </n-spin>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { CameraOutline, PawOutline, LocationOutline, AlertCircleOutline } from '@vicons/ionicons5'
import StatCard from '@/components/StatCard.vue'
import TrendChart from '@/components/TrendChart.vue'
import { getAdminDashboard } from '@/api/admin.js'

const loading = ref(true)
const data = ref(null)
const barChartRef = ref(null)
let barChart = null

const maxCount = computed(() => {
  if (!data.value?.breed_top5?.length) return 1
  return Math.max(...data.value.breed_top5.map((b) => b.count))
})

function rankColor(idx) {
  const colors = ['#f0a020', '#c0c0c0', '#cd7f32', '#7c5ce7', '#2080f0']
  return colors[idx] || '#7c5ce7'
}

function initBarChart() {
  if (!barChartRef.value || !data.value?.location_ranking) return
  if (barChart) barChart.dispose()
  barChart = echarts.init(barChartRef.value)
  const names = data.value.location_ranking.map((l) => l.name)
  const counts = data.value.location_ranking.map((l) => l.count)

  barChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 10, right: 30, bottom: 10, left: 60 },
    xAxis: { type: 'value', minInterval: 1 },
    yAxis: { type: 'category', data: [...names].reverse(), axisLabel: { fontSize: 12 } },
    series: [
      {
        type: 'bar',
        data: [...counts].reverse(),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#7c5ce7' },
            { offset: 1, color: '#a78bfa' },
          ]),
          borderRadius: [0, 4, 4, 0],
        },
        barWidth: 20,
        label: { show: true, position: 'right', fontSize: 12 },
      },
    ],
  })
}

onMounted(async () => {
  try {
    data.value = await getAdminDashboard()
    await nextTick()
    setTimeout(() => initBarChart(), 200)
  } catch (e) {
    console.error('获取看板数据失败', e)
  } finally {
    loading.value = false
  }
  window.addEventListener('resize', () => barChart?.resize())
})

onUnmounted(() => {
  window.removeEventListener('resize', () => barChart?.resize())
  barChart?.dispose()
})

watch(() => data.value?.location_ranking, () => {
  nextTick(() => {
    barChart?.dispose()
    initBarChart()
  })
})
</script>

<style scoped>
.stats-row {
  margin-bottom: 24px;
}
.charts-row {
  margin-bottom: 24px;
}
.chart-box {
  width: 100%;
  height: 280px;
}
.trend-card {
  margin-bottom: 24px;
}
.top5-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 8px 0;
}
.top5-item {
  display: flex;
  align-items: center;
  gap: 12px;
}
.top5-rank {
  font-weight: 700;
  font-size: 16px;
  width: 36px;
}
.rank-1 { color: #f0a020; }
.rank-2 { color: #909399; }
.rank-3 { color: #cd7f32; }
.top5-breed {
  width: 80px;
  font-size: 14px;
  font-weight: 500;
  flex-shrink: 0;
}
</style>
