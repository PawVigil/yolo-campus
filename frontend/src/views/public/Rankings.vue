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
            <n-grid-item>
              <StickyNote color="var(--surface-highlighter)">
                <div class="rank-icon">👑</div>
                <div class="rank-title">出镜之王</div>
                <div class="rank-desc">出现频率最高的动物</div>
                <div class="rank-value">{{ data.most_seen?.breed || '暂无' }}</div>
                <div class="rank-stat">
                  <span class="rank-tag">出现 {{ data.most_seen?.count ?? 0 }} 次</span>
                </div>
                <div class="rank-pct">占比 {{ ((data.most_seen?.percentage ?? 0) * 100).toFixed(0) }}%</div>
              </StickyNote>
            </n-grid-item>

            <n-grid-item>
              <StickyNote color="var(--surface-mint)" :rotate="0.6">
                <div class="rank-icon">🏠</div>
                <div class="rank-title">最佳宅猫</div>
                <div class="rank-desc">最固定单一地点的动物</div>
                <div class="rank-value">{{ data.homebody?.breed || '暂无' }}</div>
                <div class="rank-stat">
                  <LocationBadge :name="data.homebody?.location || '暂无'" />
                </div>
                <div class="rank-pct">{{ ((data.homebody?.percentage ?? 0) * 100).toFixed(0) }}% 集中度</div>
              </StickyNote>
            </n-grid-item>

            <n-grid-item>
              <StickyNote color="var(--surface-blush)" :rotate="-0.5">
                <div class="rank-icon">🦸</div>
                <div class="rank-title">独行侠</div>
                <div class="rank-desc">出现次数最少的品种</div>
                <div class="rank-value">{{ data.rare?.breed || '暂无' }}</div>
                <div class="rank-stat">
                  <span class="rank-tag">仅出现 {{ data.rare?.count ?? 0 }} 次</span>
                </div>
                <div class="rank-pct">珍惜品种！</div>
              </StickyNote>
            </n-grid-item>

            <n-grid-item>
              <StickyNote color="var(--surface-teal)" :rotate="0.4">
                <div class="rank-icon">🔥</div>
                <div class="rank-title">最热闹地点</div>
                <div class="rank-desc">检测量占比最高的地点</div>
                <div class="rank-value">{{ data.busiest_place?.name || '暂无' }}</div>
                <div class="rank-stat">
                  <span class="rank-tag">{{ data.busiest_place?.count ?? 0 }} 次检测</span>
                </div>
                <div class="rank-pct">占比 {{ ((data.busiest_place?.percentage ?? 0) * 100).toFixed(0) }}%</div>
              </StickyNote>
            </n-grid-item>

            <n-grid-item span="2">
              <StickyNote color="var(--surface-sand)" :rotate="-0.3">
                <div class="rank-icon">⏰</div>
                <div class="rank-title">最佳观测时间</div>
                <div class="rank-desc">动物出现最密集的时段</div>
                <div class="rank-value">{{ data.best_time?.hour_range || '暂无' }}</div>
                <div class="rank-stat">
                  <span class="rank-tag">平均 {{ data.best_time?.avg_count ?? 0 }} 次/小时</span>
                </div>
                <div class="rank-pct">这个时间段最有可能看到小动物！</div>
              </StickyNote>
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
import StickyNote from '@/components/StickyNote.vue'
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
.rankings-page { min-height: 100vh; background: var(--color-cream-paper); }
.rankings-content { max-width: 1100px; margin: 0 auto; padding: 24px 20px 60px; }
.page-title { text-align: center; font-size: 28px; margin-bottom: 4px; color: var(--color-forest-ink); }
.page-subtitle { text-align: center; color: var(--color-whisper-gray); margin-bottom: 32px; }
.rank-icon { font-size: 40px; margin-bottom: 8px; }
.rank-title { font-size: 18px; font-weight: var(--weight-bold); color: var(--color-forest-ink); margin-bottom: 4px; }
.rank-desc { font-size: 13px; color: var(--color-whisper-gray); margin-bottom: 12px; }
.rank-value { font-size: 28px; font-weight: var(--weight-bold); color: var(--color-forest-ink); margin-bottom: 8px; }
.rank-stat { margin-bottom: 8px; }
.rank-pct { font-size: 14px; color: var(--color-forest-ink); }
.rank-tag { display: inline-block; font-size: 12px; padding: 2px 10px; background: var(--color-cream-paper); color: var(--color-forest-ink); border: 1px solid var(--color-pencil-gray); border-radius: var(--radius-full); }
</style>
