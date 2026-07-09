<template>
  <div class="safety-page">
    <!-- 导航 -->
    <PublicNav menu-key="safety" />

    <div class="safety-content">
      <n-spin :show="loading">
        <n-empty v-if="!loading && error" description="数据加载失败 — 请检查网络连接后刷新页面" class="error-state" :show-icon="false" />
        <template v-else-if="!loading && data">
          <!-- 页面标题 -->
          <div class="page-header">
            <h1 class="page-header__title">公告栏</h1>
            <p class="page-header__sub">校园安全提醒 — 基于真实检测数据发布</p>
            <span class="page-header__count">{{ data.items.length }} 则公告</span>
          </div>

          <!-- 公告板 -->
          <div class="notice-board">
            <!-- 木板噪点层 -->
            <div class="board-noise"></div>
            <!-- 猫爪印 -->
            <div class="board-paw board-paw--tl"></div>
            <div class="board-paw board-paw--br"></div>

            <div class="board-inner">
              <n-empty v-if="data.items.length === 0" description="暂无安全提醒 — 管理员确认各地点安全后会在此公示" class="empty-state" :show-icon="false" />

              <div v-else class="notice-grid">
                <div
                  v-for="(tip, i) in data.items"
                  :key="tip.id"
                  class="wanted-card"
                  :style="{ '--card-rotate': rotations[i % 8] + 'deg', '--pin-x': pinOffsets[i % 8] + 'px' }"
                >
                  <!-- 图钉 -->
                  <div class="wanted-pin"></div>

                  <!-- 装饰边框 -->
                  <div class="wanted-border">
                    <!-- 顶部标题区：仿 WANTED 大字 -->
                    <div class="wanted-header">
                      <div class="wanted-header__line"></div>
                      <span class="wanted-header__text">公告</span>
                      <span class="wanted-header__en">NOTICE</span>
                      <div class="wanted-header__line"></div>
                    </div>

                    <!-- 内容区 -->
                    <div class="wanted-body">
                      <!-- 地点 -->
                      <div class="wanted-location">{{ tip.location_name }}</div>

                      <!-- 正文 -->
                      <p class="wanted-content">{{ tip.content }}</p>

                      <!-- 底部信息 -->
                      <div class="wanted-footer">
                        <span class="wanted-date">{{ tip.published_at?.slice(0, 10) }}</span>
                        <span class="wanted-seal">PawVigil</span>
                      </div>
                    </div>
                  </div>

                  <!-- 卷角 -->
                  <div class="wanted-curl"></div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </n-spin>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PublicNav from '@/components/PublicNav.vue'
import { getPublicSafetyTips } from '@/api/public.js'

const router = useRouter()
const loading = ref(true)
const data = ref({ items: [] })
const error = ref(false)

// 预设旋转角度（±3°~5°）和图钉偏移，按索引循环
const rotations = [-3.5, 2, -1.5, 4.5, -2.5, 3, -4, 1.5]
const pinOffsets = [-8, 5, -3, 10, -6, 3, -4, 7]

onMounted(async () => {
  error.value = false
  try {
    data.value = await getPublicSafetyTips()
  } catch (e) {
    console.error('获取安全提醒失败', e)
    error.value = true
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
/* ========================================
   SafetyNotice.vue — 海贼王悬赏令风格公告榜
   配色：复古羊皮纸 + 深棕木板 + 墨水印刷
   ======================================== */

/* ---- 页面底色 ---- */
.safety-page {
  min-height: 100vh;
  background: var(--color-cream-paper);
}

.safety-content {
  max-width: 1060px;
  margin: 0 auto;
  padding: 28px 24px 100px;
}

/* ---- 页面标题 ---- */
.page-header {
  text-align: center;
  margin-bottom: 32px;
  position: relative;
}

.page-header__title {
  font-family: 'Georgia', 'Noto Serif SC', serif;
  font-size: 42px;
  font-weight: 900;
  color: var(--color-forest-ink);
  letter-spacing: 0.15em;
  margin: 0;
  line-height: 1.2;
}

.page-header__sub {
  font-size: 14px;
  color: var(--color-ink-light);
  margin: 8px 0 0;
  opacity: 0.7;
  letter-spacing: 0.08em;
}

.page-header__count {
  display: inline-block;
  margin-top: 10px;
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: var(--weight-semibold);
  color: var(--color-notice-warning);
  background: rgba(201,138,45,0.1);
  border: 1px solid rgba(201,138,45,0.2);
  padding: 3px 14px;
  border-radius: var(--radius-full);
  letter-spacing: 0.05em;
}

/* ========================================
   公告板 — 深棕复古木纹
   ======================================== */
.notice-board {
  position: relative;
  /* 深棕木纹三层叠加 */
  background:
    /* 木纹细条纹 */
    repeating-linear-gradient(
      92deg,
      transparent,
      transparent 5px,
      rgba(0,0,0,0.06) 5px,
      rgba(0,0,0,0.06) 6px,
      transparent 6px,
      transparent 16px,
      rgba(0,0,0,0.04) 16px,
      rgba(0,0,0,0.04) 17px
    ),
    /* 木纹宽高光 */
    repeating-linear-gradient(
      87deg,
      transparent,
      transparent 50px,
      rgba(154,134,99,0.1) 50px,
      rgba(154,134,99,0.1) 53px,
      transparent 53px,
      transparent 110px
    ),
    /* 深棕渐变基底 */
    linear-gradient(
      178deg,
      #5a4435 0%,
      #4a3728 30%,
      #3d2d20 60%,
      #4a3728 100%
    );
  border: 14px solid #3a2a1f;
  border-radius: 2px;
  box-shadow:
    inset 0 3px 16px rgba(0,0,0,0.35),
    inset 0 -2px 8px rgba(0,0,0,0.15),
    0 16px 60px rgba(0,0,0,0.45),
    0 4px 20px rgba(0,0,0,0.25);
  padding: 36px 40px;
  min-height: 580px;
}

/* 木板噪点纹理 */
.board-noise {
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.06'/%3E%3C/svg%3E");
  pointer-events: none;
  z-index: 0;
  border-radius: inherit;
}

/* 猫爪印 */
.board-paw {
  position: absolute;
  width: 26px;
  height: 26px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' fill='%23201917'%3E%3Cellipse cx='50' cy='68' rx='22' ry='18'/%3E%3Ccircle cx='26' cy='38' r='10'/%3E%3Ccircle cx='50' cy='30' r='10'/%3E%3Ccircle cx='74' cy='38' r='10'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  pointer-events: none;
  z-index: 1;
}
.board-paw--tl {
  top: 14px;
  left: 18px;
  opacity: 0.08;
  transform: rotate(-12deg);
}
.board-paw--br {
  bottom: 16px;
  right: 20px;
  opacity: 0.05;
  transform: rotate(22deg);
}

.board-inner {
  position: relative;
  z-index: 2;
}

/* ========================================
   公告网格 — 错落张贴
   ======================================== */
.notice-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
  gap: 24px;
  align-items: start;
}

/* ========================================
   悬赏令卡片
   ======================================== */
.wanted-card {
  position: relative;
  /* 羊皮纸底色：中心亮 → 边缘暗黄 */
  background:
    radial-gradient(ellipse at 48% 38%, #e8ddc0, #d5c8a4 60%, #c0b08d 90%, #a89870 100%);
  padding: 0;
  transform: rotate(var(--card-rotate, 0deg));
  transition: transform 0.35s ease, box-shadow 0.35s ease;
  box-shadow:
    3px 4px 12px rgba(0,0,0,0.25),
    1px 1px 4px rgba(0,0,0,0.15),
    inset 0 0 30px rgba(164,142,104,0.1);
  cursor: default;
}

/* 做旧纸张纹理叠加 — 纯CSS渐变 */
.wanted-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse at 20% 25%, rgba(139,115,85,0.1), transparent 40%),
    radial-gradient(ellipse at 80% 70%, rgba(139,115,85,0.08), transparent 35%),
    radial-gradient(ellipse at 55% 90%, rgba(139,115,85,0.06), transparent 30%),
    linear-gradient(to right, rgba(139,115,85,0.12), transparent 12%, transparent 88%, rgba(139,115,85,0.12)),
    linear-gradient(to bottom, rgba(139,115,85,0.08), transparent 8%, transparent 92%, rgba(139,115,85,0.15));
  pointer-events: none;
  z-index: 0;
  border-radius: inherit;
}

/* 图钉 */
.wanted-pin {
  position: absolute;
  top: -7px;
  left: calc(50% + var(--pin-x, 0px));
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background:
    radial-gradient(circle at 36% 30%, #e8b860, #b87333 45%, #8b5e2a 100%);
  box-shadow:
    1px 3px 6px rgba(0,0,0,0.4),
    inset 0 1px 3px rgba(255,255,255,0.2);
  z-index: 20;
  transform: translateX(-50%);
}

/* 装饰边框 — 卷草纹点状线 */
.wanted-border {
  position: relative;
  z-index: 1;
  margin: 8px;
  border: 2px solid rgba(58,42,31,0.25);
  /* 点状装饰内边框 */
  outline: 1px dashed rgba(58,42,31,0.15);
  outline-offset: 4px;
}

/* ---- 顶部标题区 ---- */
.wanted-header {
  text-align: center;
  padding: 16px 16px 12px;
  border-bottom: 1px solid rgba(58,42,31,0.12);
  position: relative;
}

.wanted-header__line {
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, rgba(58,42,31,0.3) 20%, rgba(58,42,31,0.3) 80%, transparent 100%);
  margin: 0 10px;
}

.wanted-header__text {
  display: block;
  font-family: 'Georgia', 'Noto Serif SC', serif;
  font-size: 32px;
  font-weight: 900;
  color: #3a2a1f;
  letter-spacing: 0.2em;
  line-height: 1.2;
  text-shadow: 0 1px 2px rgba(0,0,0,0.08);
  /* 模拟油墨印刷质感 */
  -webkit-text-stroke: 0.3px rgba(58,42,31,0.3);
}

.wanted-header__en {
  display: block;
  font-family: 'Georgia', serif;
  font-size: 11px;
  font-weight: 400;
  color: rgba(58,42,31,0.45);
  letter-spacing: 0.35em;
  margin-top: 2px;
}

/* ---- 内容区 ---- */
.wanted-body {
  padding: 16px 20px 18px;
}

/* 地点 */
.wanted-location {
  font-family: 'Georgia', 'Noto Serif SC', serif;
  font-size: 20px;
  font-weight: 800;
  color: #3a2a1f;
  letter-spacing: 0.15em;
  margin-bottom: 12px;
  text-align: center;
}

/* 标题 */
.wanted-title {
  margin: 0 0 10px;
  font-family: 'Georgia', 'Noto Serif SC', serif;
  font-size: 17px;
  font-weight: 700;
  color: #3a2a1f;
  line-height: 1.45;
  letter-spacing: 0.03em;
}

/* 正文 */
.wanted-content {
  margin: 0 0 14px;
  font-size: 13.5px;
  font-weight: 400;
  color: #5c4734;
  line-height: 1.75;
}

/* 底部信息 */
.wanted-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 10px;
  border-top: 1px solid rgba(58,42,31,0.1);
}

.wanted-date {
  font-family: var(--font-mono);
  font-size: 11px;
  color: #7a6a55;
  letter-spacing: 0.04em;
}

.wanted-seal {
  font-family: 'Georgia', serif;
  font-size: 10px;
  font-weight: 700;
  color: rgba(160,61,43,0.35);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  border: 1.5px solid rgba(160,61,43,0.2);
  padding: 2px 8px;
  border-radius: 2px;
  /* 轻微旋转模拟盖章 */
  transform: rotate(-3deg);
}

/* 卷角 — 右下角 */
.wanted-curl {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 0;
  height: 0;
  border-style: solid;
  border-width: 0 0 18px 18px;
  border-color: transparent transparent #4a3728 transparent;
  z-index: 15;
  filter: drop-shadow(-1px -1px 2px rgba(0,0,0,0.2));
}
.wanted-curl::before {
  content: '';
  position: absolute;
  bottom: -18px;
  right: 0;
  width: 0;
  height: 0;
  border-style: solid;
  border-width: 18px 18px 0 0;
  border-color: #c8b890 transparent transparent transparent;
  filter: brightness(0.85);
}

/* ========================================
   Hover — 悬浮回正
   ======================================== */
.wanted-card:hover {
  transform: rotate(0deg) translateY(-6px) scale(1.01);
  box-shadow:
    5px 10px 30px rgba(0,0,0,0.35),
    2px 3px 8px rgba(0,0,0,0.2),
    inset 0 0 30px rgba(164,142,104,0.08);
  z-index: 20;
}

/* ========================================
   空状态
   ======================================== */
.empty-state {
  margin-top: 80px;
}
:deep(.empty-state .n-empty__description) {
  color: var(--color-paper-edge) !important;
  opacity: 0.7;
}

/* ========================================
   错误状态
   ======================================== */
.error-state {
  margin-top: 80px;
}

/* ========================================
   响应式
   ======================================== */
@media (max-width: 768px) {
  .notice-board {
    padding: 20px 16px;
    border-width: 10px;
    min-height: 400px;
  }
  .notice-grid {
    grid-template-columns: 1fr;
    gap: 18px;
  }
  .safety-content {
    padding: 16px 12px 60px;
  }
  .wanted-header__text {
    font-size: 26px;
  }
  .page-header__title {
    font-size: 32px;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .notice-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
