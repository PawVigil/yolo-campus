<template>
  <div class="dashboard-page">
    <n-spin :show="loading">
      <template v-if="!loading && data">
        <!-- 统计卡片 -->
        <n-grid :cols="4" :x-gap="16" :y-gap="16" responsive="screen" class="stats-row">
          <n-grid-item>
            <StatCard :icon="CameraOutline" :value="data.stats.total_detections" label="总检测数" />
          </n-grid-item>
          <n-grid-item>
            <StatCard :icon="PawOutline" :value="data.stats.with_animals" label="有动物记录" color="#18a058" />
          </n-grid-item>
          <n-grid-item>
            <StatCard :icon="LocationOutline" :value="data.stats.locations_covered" label="覆盖地点" color="#f0a020" />
          </n-grid-item>
          <n-grid-item>
            <StatCard :icon="AlertCircleOutline" :value="data.stats.published_tips" label="已发布提醒" color="#2080f0" />
          </n-grid-item>
        </n-grid>

        <n-grid :cols="2" :x-gap="16" responsive="screen" class="charts-row">
          <!-- 地点排行 -->
          <n-grid-item>
            <n-card :bordered="false" title="📍 各地点检测排行">
              <div class="top5-list">
                <div v-for="(item, idx) in data.location_ranking" :key="item.name" class="top5-item">
                  <span class="top5-rank" :class="`rank-${idx + 1}`">#{{ idx + 1 }}</span>
                  <span class="top5-breed">{{ item.name }}</span>
                  <div class="top5-bar-wrap">
                    <div class="top5-bar" :class="`bar-${idx + 1}`" :style="{ width: (item.count / maxLocCount * 100) + '%' }">
                      <span class="top5-bar-label">{{ item.count }} 次</span>
                    </div>
                  </div>
                </div>
              </div>
            </n-card>
          </n-grid-item>
          <!-- 品种 TOP5 -->
          <n-grid-item>
            <n-card :bordered="false" title="🏅 品种出现次数 TOP5">
              <div class="top5-list">
                <div v-for="(item, idx) in data.breed_top5" :key="item.breed" class="top5-item">
                  <span class="top5-rank" :class="`rank-${idx + 1}`">#{{ idx + 1 }}</span>
                  <span class="top5-breed">{{ item.breed }}</span>
                  <div class="top5-bar-wrap">
                    <div class="top5-bar" :class="`bar-${idx + 1}`" :style="{ width: (item.count / maxCount * 100) + '%' }">
                      <span class="top5-bar-label">{{ item.count }} 次</span>
                    </div>
                  </div>
                </div>
              </div>
            </n-card>
          </n-grid-item>
        </n-grid>

        <!-- 趋势图 -->
        <n-card :bordered="false" title="📈 近14天检测趋势" class="trend-card">
          <TrendChart :data="data.trend_14d" height="320px" />
        </n-card>
      </template>
    </n-spin>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { CameraOutline, PawOutline, LocationOutline, AlertCircleOutline } from '@vicons/ionicons5'
import StatCard from '@/components/StatCard.vue'
import TrendChart from '@/components/TrendChart.vue'
import { getAdminDashboard } from '@/api/admin.js'

const loading = ref(true)
const data = ref(null)

const maxCount = computed(() => {
  if (!data.value?.breed_top5?.length) return 1
  return Math.max(...data.value.breed_top5.map((b) => b.count))
})

const maxLocCount = computed(() => {
  if (!data.value?.location_ranking?.length) return 1
  return Math.max(...data.value.location_ranking.map((l) => l.count))
})

onMounted(async () => {
  try {
    data.value = await getAdminDashboard()
  } catch (e) {
    console.error('获取看板数据失败', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.stats-row {
  margin-bottom: 24px;
}
.charts-row {
  margin-bottom: 24px;
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
  font-weight: var(--weight-bold);
  font-size: 16px;
  width: 36px;
  color: var(--color-forest-ink);
}
.top5-breed {
  width: 80px;
  font-size: 14px;
  font-weight: var(--weight-medium);
  flex-shrink: 0;
  color: var(--color-forest-ink);
}
.top5-bar-wrap {
  flex: 1;
  height: 24px;
  background: var(--surface-cream);
  border-radius: 4px;
  overflow: hidden;
}
.top5-bar {
  height: 100%;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 8px;
  transition: width 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}
.bar-1 { background: linear-gradient(90deg, #e8a840, #f5c76a); }
.bar-2 { background: linear-gradient(90deg, #9a9a9a, #c0c0c0); }
.bar-3 { background: linear-gradient(90deg, #c08040, #d4a060); }
.bar-4 { background: linear-gradient(90deg, #2d5016, #4a7a2e); }
.bar-5 { background: linear-gradient(90deg, #3a6020, #558a32); }
.top5-bar-label {
  font-size: 12px;
  font-weight: var(--weight-semibold);
  color: #fff;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}
</style>
