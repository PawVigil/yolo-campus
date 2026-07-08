<template>
  <div class="rankings-page">
    <!-- 导航 -->
    <PublicNav menu-key="rankings" />

    <n-layout-content class="rankings-content">
      <n-spin :show="loading">
        <n-empty v-if="!loading && error" description="数据加载失败，请稍后重试" class="error-state" />
        <template v-else-if="!loading && data">
          <h2 class="page-title">🏆 趣味排行榜</h2>
          <p class="page-subtitle">所有数据基于真实检测记录统计，每日更新</p>

          <n-grid :cols="3" :x-gap="16" :y-gap="16" responsive="screen">
            <!-- 出镜之王 -->
            <n-grid-item>
              <n-card :bordered="false" class="rank-card card-gold">
                <div class="rank-icon">👑</div>
                <div class="rank-title">出镜之王</div>
                <div class="rank-desc">出现频率最高的动物</div>
                <div class="rank-value">{{ data.most_seen?.breed || '暂无' }}</div>
                <div class="rank-stat">
                  <n-tag type="warning" round>出现 {{ data.most_seen?.count ?? 0 }} 次</n-tag>
                </div>
                <div class="rank-pct">占比 {{ ((data.most_seen?.percentage ?? 0) * 100).toFixed(0) }}%</div>
              </n-card>
            </n-grid-item>

            <!-- 最佳宅猫 -->
            <n-grid-item>
              <n-card :bordered="false" class="rank-card card-blue">
                <div class="rank-icon">🏠</div>
                <div class="rank-title">最佳宅猫</div>
                <div class="rank-desc">最固定单一地点的动物</div>
                <div class="rank-value">{{ data.homebody?.breed || '暂无' }}</div>
                <div class="rank-stat">
                  <LocationBadge :name="data.homebody?.location || '暂无'" />
                </div>
                <div class="rank-pct">{{ ((data.homebody?.percentage ?? 0) * 100).toFixed(0) }}% 集中度</div>
              </n-card>
            </n-grid-item>

            <!-- 独行侠 -->
            <n-grid-item>
              <n-card :bordered="false" class="rank-card card-green">
                <div class="rank-icon">🦸</div>
                <div class="rank-title">独行侠</div>
                <div class="rank-desc">出现次数最少的品种</div>
                <div class="rank-value">{{ data.rare?.breed || '暂无' }}</div>
                <div class="rank-stat">
                  <n-tag type="info" round>仅出现 {{ data.rare?.count ?? 0 }} 次</n-tag>
                </div>
                <div class="rank-pct">珍惜品种！</div>
              </n-card>
            </n-grid-item>

            <!-- 最热闹地点 -->
            <n-grid-item>
              <n-card :bordered="false" class="rank-card card-red">
                <div class="rank-icon">🔥</div>
                <div class="rank-title">最热闹地点</div>
                <div class="rank-desc">检测量占比最高的地点</div>
                <div class="rank-value">{{ data.busiest_place?.name || '暂无' }}</div>
                <div class="rank-stat">
                  <n-tag type="error" round>{{ data.busiest_place?.count ?? 0 }} 次检测</n-tag>
                </div>
                <div class="rank-pct">占比 {{ ((data.busiest_place?.percentage ?? 0) * 100).toFixed(0) }}%</div>
              </n-card>
            </n-grid-item>

            <!-- 最佳观测时间 -->
            <n-grid-item span="2">
              <n-card :bordered="false" class="rank-card card-purple">
                <div class="rank-icon">⏰</div>
                <div class="rank-title">最佳观测时间</div>
                <div class="rank-desc">动物出现最密集的时段</div>
                <div class="rank-value">{{ data.best_time?.hour_range || '暂无' }}</div>
                <div class="rank-stat">
                  <n-tag type="info" round>平均 {{ data.best_time?.avg_count ?? 0 }} 次/小时</n-tag>
                </div>
                <div class="rank-pct">这个时间段最有可能看到小动物！</div>
              </n-card>
            </n-grid-item>
          </n-grid>
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
import { getRankings } from '@/api/public.js'

const router = useRouter()
const loading = ref(true)
const data = ref(null)
const error = ref(false)



onMounted(async () => {
  error.value = false
  try {
    data.value = await getRankings()
  } catch (e) {
    console.error('获取排行榜失败', e)
    error.value = true
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.rankings-page { min-height: 100vh; background: #f5f7fa; }
.public-nav { background: rgba(255,255,255,0.9); backdrop-filter: blur(10px); position: sticky; top: 0; z-index: 100; }
.nav-content { max-width: 1200px; margin: 0 auto; display: flex; align-items: center; padding: 0 20px; height: 56px; }
.nav-brand { display: flex; align-items: center; gap: 8px; cursor: pointer; margin-right: 24px; }
.brand-icon { font-size: 24px; }
.brand-text { font-size: 18px; font-weight: 700; color: #7c5ce7; }
.admin-link { margin-left: auto; }
.rankings-content { max-width: 1100px; margin: 0 auto; padding: 24px 20px; }
.page-title { text-align: center; font-size: 28px; margin-bottom: 4px; }
.page-subtitle { text-align: center; color: #909399; margin-bottom: 32px; }
.rank-card { text-align: center; padding: 20px; min-height: 220px; transition: transform 0.2s; }
.rank-card:hover { transform: translateY(-3px); }
.card-gold { border-top: 4px solid #f0a020; }
.card-blue { border-top: 4px solid #2080f0; }
.card-green { border-top: 4px solid #18a058; }
.card-red { border-top: 4px solid #d03050; }
.card-purple { border-top: 4px solid #7c5ce7; }
.rank-icon { font-size: 40px; margin-bottom: 8px; }
.rank-title { font-size: 18px; font-weight: 700; margin-bottom: 4px; }
.rank-desc { font-size: 13px; color: #909399; margin-bottom: 12px; }
.rank-value { font-size: 22px; font-weight: 700; color: #333; margin-bottom: 8px; }
.rank-stat { margin-bottom: 8px; }
.rank-pct { font-size: 14px; color: #666; }
</style>
