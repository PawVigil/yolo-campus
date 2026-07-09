<template>
  <div class="rankings-page">
    <!-- 导航 -->
    <PublicNav menu-key="rankings" />

    <n-layout-content class="rankings-content">
      <n-spin :show="loading">
        <n-empty v-if="!loading && error" description="数据加载失败 — 请检查网络连接后刷新页面" class="error-state" :show-icon="false" />
        <template v-else-if="!loading && data">
          <h2 class="page-title">趣味排行榜</h2>
          <p class="page-subtitle">所有数据基于真实检测记录统计，每日更新</p>

          <!-- 领奖台 — 冠亚季军 -->
          <div class="rankings-podium">
            <!-- 亚军 — 左 -->
            <div class="podium-item podium-side podium-left">
              <StickyNote color="var(--surface-mint)" :rotate="1.5">
                <div class="rk-card">
                  <img src="/rankings/homebody.svg" alt="" class="rk-bg-img" />
                  <div class="rk-content">
                    <div class="rk-head">
                      <span class="rk-medal">🥈</span>
                      <span class="rk-label">最佳宅猫</span>
                    </div>
                    <div class="rk-value-lg">{{ data.homebody?.breed || '暂无' }}</div>
                    <div class="rk-sub">最固定单一地点的动物</div>
                    <div class="rk-bar"><span class="rk-bar-fill" :style="{ width: ((data.homebody?.percentage ?? 0) * 100).toFixed(0) + '%' }"></span></div>
                    <div class="rk-foot">
                      <InkTag variant="mint">{{ ((data.homebody?.percentage ?? 0) * 100).toFixed(0) }}% 集中度</InkTag>
                      <LocationBadge v-if="data.homebody?.location" :name="data.homebody.location" />
                    </div>
                  </div>
                </div>
              </StickyNote>
            </div>

            <!-- 冠军 — 中 -->
            <div class="podium-item podium-champion">
              <StickyNote color="var(--surface-highlighter)">
                <div class="rk-card">
                  <img src="/rankings/most-seen.svg" alt="" class="rk-bg-img rk-bg-img--champion" />
                  <div class="rk-content">
                    <div class="rk-crown">👑</div>
                    <div class="rk-label">出镜之王</div>
                    <div class="rk-value-hero">{{ data.most_seen?.breed || '暂无' }}</div>
                    <div class="rk-sub">出现频率最高的动物</div>
                    <div class="rk-bar rk-bar--lg"><span class="rk-bar-fill" :style="{ width: ((data.most_seen?.percentage ?? 0) * 100).toFixed(0) + '%' }"></span></div>
                    <div class="rk-foot rk-foot--center">
                      <InkTag variant="ink">出现 {{ data.most_seen?.count ?? 0 }} 次</InkTag>
                      <span class="rk-pct-mono">{{ ((data.most_seen?.percentage ?? 0) * 100).toFixed(0) }}%</span>
                    </div>
                  </div>
                </div>
              </StickyNote>
            </div>

            <!-- 季军 — 右 -->
            <div class="podium-item podium-side podium-right">
              <StickyNote color="var(--surface-blush)" :rotate="-1.5">
                <div class="rk-card">
                  <img src="/rankings/rare.svg" alt="" class="rk-bg-img" />
                  <div class="rk-content">
                    <div class="rk-head">
                      <span class="rk-medal">🥉</span>
                      <span class="rk-label">独行侠</span>
                    </div>
                    <div class="rk-value-lg">{{ data.rare?.breed || '暂无' }}</div>
                    <div class="rk-sub">出现次数最少的品种</div>
                    <div class="rk-bar"><span class="rk-bar-fill rk-bar-fill--rare" :style="{ width: Math.min(((data.rare?.count ?? 0) / 5) * 100, 100) + '%' }"></span></div>
                    <div class="rk-foot">
                      <InkTag variant="terracotta">仅 {{ data.rare?.count ?? 0 }} 次</InkTag>
                      <span class="rk-rare-note">珍惜品种</span>
                    </div>
                  </div>
                </div>
              </StickyNote>
            </div>
          </div>

          <!-- 底部两卡 — 左窄右宽 -->
          <div class="rankings-bottom">
            <StickyNote color="var(--surface-teal)" :rotate="0.4">
              <div class="rk-card">
                <img src="/rankings/busiest.svg" alt="" class="rk-bg-img" />
                <div class="rk-content">
                  <div class="rk-head">
                    <span class="rk-medal">🔥</span>
                    <span class="rk-label">最热闹地点</span>
                  </div>
                  <div class="rk-value-lg">{{ data.busiest_place?.name || '暂无' }}</div>
                  <div class="rk-sub">检测量占比最高的地点</div>
                  <div class="rk-bar"><span class="rk-bar-fill" :style="{ width: ((data.busiest_place?.percentage ?? 0) * 100).toFixed(0) + '%' }"></span></div>
                  <div class="rk-foot">
                    <InkTag variant="teal">{{ data.busiest_place?.count ?? 0 }} 次检测</InkTag>
                    <span class="rk-pct-mono">{{ ((data.busiest_place?.percentage ?? 0) * 100).toFixed(0) }}%</span>
                  </div>
                </div>
              </div>
            </StickyNote>

            <StickyNote color="var(--surface-sand)" :rotate="-0.3" class="rank-wide">
              <div class="rk-card">
                <img src="/rankings/best-time.svg" alt="" class="rk-bg-img" />
                <div class="rk-content">
                  <div class="rk-head">
                    <span class="rk-medal">⏰</span>
                    <span class="rk-label">最佳观测时间</span>
                  </div>
                  <div class="rk-time-display">{{ data.best_time?.hour_range || '暂无' }}</div>
                  <div class="rk-sub">动物出现最密集的时段</div>
                  <div class="rk-foot">
                    <InkTag variant="ghost">平均 {{ data.best_time?.avg_count ?? 0 }} 次/小时</InkTag>
                    <span class="rk-tip">这个时间段最可能看到小动物</span>
                  </div>
                </div>
              </div>
            </StickyNote>
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
import LocationBadge from '@/components/LocationBadge.vue'
import StickyNote from '@/components/StickyNote.vue'
import InkTag from '@/components/InkTag.vue'
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
.page-title { text-align: left; font-size: 28px; margin-bottom: 4px; color: var(--color-forest-ink); }
.page-subtitle { text-align: left; color: var(--color-whisper-gray); margin-bottom: 32px; }

/* Podium */
.rankings-podium {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}
.podium-item { transition: transform var(--transition-normal); }
.podium-champion { flex: 1.1; z-index: 3; transform: scale(1.06); }
.podium-side { flex: 0.85; z-index: 1; transform: scale(0.92); }
.podium-left { margin-right: -20px; }
.podium-right { margin-left: -20px; }
.podium-champion:hover { transform: scale(1.1); }
.podium-side:hover { transform: scale(0.96); z-index: 4; }

/* Bottom row */
.rankings-bottom { display: flex; gap: 16px; align-items: stretch; }
.rankings-bottom > * { flex: 1; }
.rankings-bottom > .rank-wide { flex: 1.6; }

/* ================================
   rk-card — 带插图的卡片容器
   ================================ */

.rk-card {
  position: relative;
  overflow: hidden;
}

/* 背景插图 — 半透明嵌入 */
.rk-bg-img {
  position: absolute;
  bottom: -10px;
  right: -10px;
  width: 160px;
  height: auto;
  opacity: 0.6;
  pointer-events: none;
  filter: grayscale(0.2);
  mix-blend-mode: multiply;
  transition: opacity 0.3s ease;
}
.rk-bg-img--champion {
  width: 180px;
  bottom: -5px;
  right: -5px;
}
/* 悬停时插图更明显 */
.rk-card:hover .rk-bg-img {
  opacity: 0.8;
}

/* 文字内容层 — 保持在插图之上 */
.rk-content {
  position: relative;
  z-index: 2;
}

/* ================================
   卡片内容排版
   ================================ */

/* 卡片头部 */
.rk-head { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.rk-medal { font-size: 24px; line-height: 1; }
.rk-label { font-size: 14px; font-weight: var(--weight-semibold); color: var(--color-forest-ink); text-transform: uppercase; letter-spacing: 0.06em; }

/* 冠军皇冠 */
.rk-crown { font-size: 48px; text-align: center; line-height: 1; margin-bottom: 4px; }

/* 品种名 */
.rk-value-hero {
  font-family: var(--font-body);
  font-size: 36px;
  font-weight: var(--weight-extrabold);
  color: var(--color-forest-ink);
  text-align: center;
  line-height: 1.1;
  margin-bottom: 4px;
}
.rk-value-lg {
  font-family: var(--font-body);
  font-size: 26px;
  font-weight: var(--weight-bold);
  color: var(--color-forest-ink);
  line-height: 1.2;
  margin-bottom: 2px;
}

/* 时间显示 */
.rk-time-display {
  font-family: var(--font-mono);
  font-size: 28px;
  font-weight: var(--weight-bold);
  color: var(--color-forest-ink);
  line-height: 1.1;
  margin-bottom: 4px;
  font-feature-settings: 'tnum';
}

/* 副标题 */
.rk-sub { font-size: 12px; color: var(--color-whisper-gray); margin-bottom: 14px; }

/* 迷你数据条 */
.rk-bar {
  height: 6px;
  background: rgba(26, 51, 0, 0.08);
  border-radius: 3px;
  margin-bottom: 12px;
  overflow: hidden;
}
.rk-bar--lg { height: 8px; border-radius: 4px; }
.rk-bar-fill {
  display: block;
  height: 100%;
  background: var(--color-forest-ink);
  border-radius: inherit;
  transition: width 0.6s cubic-bezier(0.22, 0.61, 0.36, 1);
  min-width: 4px;
}
.rk-bar-fill--rare { background: var(--color-terracotta); }

/* 底部信息行 */
.rk-foot { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.rk-foot--center { justify-content: center; }
.rk-pct-mono { font-family: var(--font-mono); font-size: 13px; font-weight: var(--weight-semibold); color: var(--color-forest-ink); font-feature-settings: 'tnum'; }
.rk-rare-note { font-size: 12px; color: var(--color-terracotta); font-weight: var(--weight-medium); }
.rk-tip { font-size: 12px; color: var(--color-whisper-gray); }

@media (max-width: 768px) {
  .rankings-podium { flex-direction: column; gap: 16px; }
  .podium-left { margin-right: 0; }
  .podium-right { margin-left: 0; }
  .podium-champion, .podium-side { transform: none; flex: 1; }
  .rankings-bottom { flex-direction: column; }
  .rk-value-hero { font-size: 28px; }
  .rk-bg-img { width: 120px; }
  .rk-bg-img--champion { width: 140px; }
}
</style>
