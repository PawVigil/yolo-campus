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
            <div class="podium-item podium-side podium-left" @click="openHomebody">
              <StickyNote color="var(--surface-mint)" :rotate="1.5">
                <div class="rk-card" style="cursor:pointer">
                  <img src="/rankings/homebody.svg" alt="" class="rk-bg-img" />
                  <div class="rk-content">
                    <div class="rk-head">
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
            <div class="podium-item podium-champion" @click="openBreedTop5">
              <StickyNote color="var(--surface-highlighter)">
                <div class="rk-card" style="cursor:pointer">
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
            <div class="podium-item podium-side podium-right" @click="openRareTop5">
              <StickyNote color="var(--surface-blush)" :rotate="-1.5">
                <div class="rk-card" style="cursor:pointer">
                  <img src="/rankings/rare.svg" alt="" class="rk-bg-img" />
                  <div class="rk-content">
                    <div class="rk-head">
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

          <!-- 底部两卡 — 左窄右宽（禁自带旋转hover，改纯上浮防抖动） -->
          <div class="rankings-bottom">
            <StickyNote color="var(--surface-teal)" :hoverable="false" class="rk-bottom-card">
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

            <StickyNote color="var(--surface-sand)" :hoverable="false" class="rk-bottom-card rank-wide">
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

      <!-- 品种 TOP5 弹窗（出镜之王 / 独行侠 共用） -->
      <n-modal v-model:show="showBreedModal" preset="card" :title="breedModalTitle" style="max-width: 560px" :mask-closable="true">
        <n-spin :show="breedLoading">
          <n-empty v-if="!breedLoading && breedTop5.length === 0" description="暂无数据" />
          <template v-else-if="breedTop5.length > 0">
            <!-- #1 冠军 -->
            <div class="bt5-hero">
              <img v-if="getBreedImage(breedTop5[0].breed)" :src="getBreedImage(breedTop5[0].breed)" class="bt5-hero-photo" />
              <span v-else class="bt5-hero-emoji">{{ breedModalTitle.includes('稀有') ? '🦸' : '👑' }}</span>
              <div>
                <div class="bt5-hero-breed">{{ breedTop5[0].breed }}</div>
                <div class="bt5-hero-stat">出现 {{ breedTop5[0].count }} 次</div>
              </div>
            </div>
            <div class="home-divider"></div>
            <!-- TOP5 列表 -->
            <div class="breed-top5-list">
              <div v-for="(item, idx) in breedTop5" :key="item.breed" class="bt5-item">
                <span class="bt5-rank" :class="`bt5-r${idx + 1}`">#{{ idx + 1 }}</span>
                <span class="bt5-name">{{ item.breed }}</span>
                <div class="bt5-bar-wrap">
                  <div class="bt5-bar" :class="`bt5-b${idx + 1}`" :style="{ width: (item.count / breedMax * 100) + '%' }">
                    <span class="bt5-label">{{ item.count }} 次</span>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </n-spin>
      </n-modal>

      <!-- 最佳宅猫详情弹窗 -->
      <n-modal v-model:show="showHomeModal" preset="card" title="🏠 最佳宅猫 TOP5" style="max-width: 560px" :mask-closable="true">
        <div v-if="data?.homebody" class="home-detail">
          <div class="home-hero">
            <img v-if="getBreedImage(data.homebody.breed)" :src="getBreedImage(data.homebody.breed)" class="bt5-hero-photo" />
            <span v-else class="home-emoji">🐱</span>
            <div>
              <div class="home-breed">{{ data.homebody.breed }}</div>
              <div class="home-loc">📍 常驻 {{ data.homebody.location }} · 集中度 {{ ((data.homebody.percentage ?? 0) * 100).toFixed(0) }}%</div>
            </div>
          </div>
          <div class="home-divider"></div>
        </div>
        <div class="breed-top5-list">
          <div v-for="(item, idx) in (data?.homebody_top5 || [])" :key="item.breed" class="bt5-item">
            <span class="bt5-rank" :class="`bt5-r${idx + 1}`">#{{ idx + 1 }}</span>
            <span class="bt5-name">{{ item.breed }}</span>
            <span class="bt5-loc">{{ item.location }}</span>
            <div class="bt5-bar-wrap">
              <div class="bt5-bar" :class="`bt5-b${idx + 1}`" :style="{ width: ((item.percentage ?? 0) * 100).toFixed(0) + '%' }">
                <span class="bt5-label">{{ ((item.percentage ?? 0) * 100).toFixed(0) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </n-modal>
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
import { getRankings, getBreedStats } from '@/api/public.js'

const router = useRouter()
const loading = ref(true)
const data = ref(null)
const error = ref(false)

// 品种 TOP5 弹窗（复用于出镜之王 / 独行侠）
const showBreedModal = ref(false)
const breedLoading = ref(false)
const breedTop5 = ref([])
const breedMax = ref(1)
const breedModalTitle = ref('')

function pickTop5(stats, asc = false) {
  const sorted = Object.entries(stats)
    .filter(([, c]) => c > 0)
    .sort((a, b) => asc
      ? (a[1] - b[1] || a[0].localeCompare(b[0], 'zh'))
      : (b[1] - a[1] || a[0].localeCompare(b[0], 'zh')))
  return sorted.slice(0, 5).map(([breed, count]) => ({ breed, count }))
}

async function openBreedTop5() {
  breedModalTitle.value = '🏅 品种出现次数 TOP5'
  showBreedModal.value = true
  breedLoading.value = true
  try {
    const res = await getBreedStats()
    breedTop5.value = pickTop5(res.stats || {}, false)
    breedMax.value = breedTop5.value[0]?.count || 1
  } catch (e) { console.error(e) }
  finally { breedLoading.value = false }
}

// 最佳宅猫详情弹窗 — 集中度 TOP5
const showHomeModal = ref(false)
function openHomebody() { showHomeModal.value = true }

// 品种图片查找
const breedImages = ref({})
function getBreedImage(name) { return breedImages.value[name] || '' }

// 独行侠弹窗 — 稀有品种 TOP5
async function openRareTop5() {
  breedModalTitle.value = '🦸 稀有品种 TOP5'
  showBreedModal.value = true
  breedLoading.value = true
  try {
    const res = await getBreedStats()
    breedTop5.value = pickTop5(res.stats || {}, true)
    breedMax.value = breedTop5.value[breedTop5.value.length - 1]?.count || 1
  } catch (e) { console.error(e) }
  finally { breedLoading.value = false }
}

onMounted(async () => {
  error.value = false
  try {
    const [rankings, breedInfo] = await Promise.all([
      getRankings(),
      fetch('/breed_info.json').then(r => r.json()).catch(() => ({})),
    ])
    data.value = rankings
    const imgs = {}
    for (const [key, info] of Object.entries(breedInfo)) {
      if (info.name_cn && info.image_url) {
        imgs[info.name_cn] = info.image_url
      }
    }
    breedImages.value = imgs
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
.page-subtitle { text-align: left; color: #888; margin-bottom: 32px; }

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
.rk-bottom-card { transition: transform 0.2s ease, box-shadow 0.2s ease; }
.rk-bottom-card:hover { transform: translateY(-6px); box-shadow: 3px 6px 0 rgba(0,0,0,0.06), 0 8px 24px rgba(0,0,0,0.1); }

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
.rk-sub { font-size: 12px; color: #888; margin-bottom: 14px; }

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
.rk-tip { font-size: 12px; color: #888; }

/* ================================
   品种 TOP5 弹窗
   ================================ */
.breed-top5-list { display: flex; flex-direction: column; gap: 14px; padding: 4px 0; }
.bt5-item { display: flex; align-items: center; gap: 10px; }
.bt5-rank { font-weight: 800; font-size: 15px; width: 34px; }
.bt5-r1 { color: #e8a840; } .bt5-r2 { color: #9a9a9a; } .bt5-r3 { color: #c08040; }
.bt5-name { font-size: 14px; font-weight: 600; color: var(--color-forest-ink); width: 80px; flex-shrink: 0; }
.bt5-loc { font-size: 12px; color: #888; width: 48px; flex-shrink: 0; text-align: right; }
.bt5-bar-wrap { flex: 1; height: 24px; background: var(--surface-cream); border-radius: 4px; overflow: hidden; }
.bt5-bar { height: 100%; border-radius: 4px; display: flex; align-items: center; justify-content: flex-end; padding-right: 8px; transition: width 0.6s cubic-bezier(0.16,1,0.3,1); min-width: 40px; }
.bt5-b1 { background: linear-gradient(90deg, #e8a840, #f5c76a); }
.bt5-b2 { background: linear-gradient(90deg, #9a9a9a, #c0c0c0); }
.bt5-b3 { background: linear-gradient(90deg, #c08040, #d4a060); }
.bt5-b4 { background: linear-gradient(90deg, #2d5016, #4a7a2e); }
.bt5-b5 { background: linear-gradient(90deg, #3a6020, #558a32); }
.bt5-label { font-size: 12px; font-weight: 600; color: #fff; text-shadow: 0 1px 2px rgba(0,0,0,0.2); }
.bt5-hero { display: flex; align-items: center; gap: 16px; margin-bottom: 4px; }
.bt5-hero-emoji { font-size: 48px; flex-shrink: 0; }
.bt5-hero-photo { width: 72px; height: 72px; border-radius: 12px; object-fit: cover; flex-shrink: 0; }
.bt5-hero-breed { font-size: 24px; font-weight: 800; color: var(--color-forest-ink); }
.bt5-hero-stat { font-size: 14px; color: #888; margin-top: 2px; }

/* 最佳宅猫弹窗 */
.home-detail { padding: 4px 0; }
.home-hero { display: flex; align-items: center; gap: 16px; margin-bottom: 12px; }
.home-emoji { font-size: 48px; }
.home-breed { font-size: 24px; font-weight: 800; color: var(--color-forest-ink); }
.home-loc { font-size: 14px; color: #888; margin-top: 2px; }
.home-divider { height: 1px; background: var(--color-pencil-gray); margin: 12px 0 18px; }

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
