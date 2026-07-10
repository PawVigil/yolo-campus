<template>
  <div class="notice-page">
    <PublicNav menu-key="safety" />

    <div class="notice-content">
      <n-spin :show="loading">
        <n-empty v-if="!loading && error" description="数据加载失败 — 请检查网络连接后刷新页面" class="error-state" :show-icon="false" />
        <template v-else-if="!loading && data">
          <!-- 页面标题 -->
          <div class="page-header">
            <h1 class="page-title">公告栏</h1>
            <p class="page-subtitle">校园安全提醒 — 基于真实检测数据发布</p>
            <div class="count-badge">
              <div class="count-pin"></div>
              <span>{{ data.items.length }} 则公告</span>
            </div>
          </div>

          <!-- 公告板 -->
          <div class="board-container">
            <div class="board">
              <n-empty v-if="data.items.length === 0" description="暂无公告 — 管理员确认各地点安全后会在此公示" class="empty-state" :show-icon="false" />

              <div v-else class="notice-grid">
                <div
                  v-for="(tip, i) in data.items"
                  :key="tip.id"
                  class="notice-card"
                >
                  <!-- 图钉 -->
                  <div class="pin"></div>

                  <!-- 装饰边框 -->
                  <div class="card-border">
                    <!-- 卡片头部：居中 -->
                    <div class="card-header">
                      <h2 class="card-title">公告</h2>
                      <span class="card-title-en">NOTICE</span>
                    </div>

                    <!-- 卡片内容：左对齐 -->
                    <div class="card-content">
                      <h3 class="area-name">{{ tip.location_name }}</h3>
                      <p class="notice-text">{{ tip.content }}</p>
                    </div>

                    <!-- 卡片底部 -->
                    <div class="card-footer">
                      <span class="notice-date">{{ tip.published_at?.slice(0, 10) }}</span>
                      <span class="stamp">PAWVIGIL</span>
                    </div>
                  </div>

                  <!-- 卷角 -->
                  <div class="corner-fold"></div>
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
import PublicNav from '@/components/PublicNav.vue'
import { getPublicSafetyTips } from '@/api/public.js'

const loading = ref(true)
const data = ref(null)
const error = ref(false)

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
   SafetyNotice.vue — 清爽校园版公告栏（打磨版）
   ======================================== */

.notice-page {
  min-height: 100vh;
  background: var(--color-page-bg);
}

.notice-content {
  max-width: 1060px;
  margin: 0 auto;
  padding: 28px 24px 100px;
}

/* ---- 页面标题 ---- */
.page-header {
  text-align: center;
  margin-bottom: 32px;
}

.page-title {
  font-size: 42px;
  color: var(--color-forest-ink);
  margin: 0 0 8px;
  font-weight: 600;
}

.page-subtitle {
  font-size: 14px;
  color: var(--color-ink-light);
  margin: 0 0 16px;
}

/* 顶部标签：迷你便签风格 */
.count-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  position: relative;
  background: var(--color-paper-main);
  border: 1px solid var(--color-divider);
  padding: 4px 16px 4px 12px;
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: var(--weight-semibold);
  color: var(--color-accent-red);
  box-shadow: 0 2px 6px rgba(80,60,40,0.1);
}
.count-pin {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, var(--color-pin-highlight), var(--color-pin-main), var(--color-pin-dark));
  box-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

/* ========================================
   公告板 — 浅橡木底板
   ======================================== */
.board-container {
  border-radius: 4px;
  border: 8px solid var(--color-board-frame);
  box-shadow: 0 8px 24px var(--shadow-board-deep);
  overflow: hidden;
}

.board {
  background-color: var(--color-board-bg);
  /* 竖纹护墙板分隔缝 */
  background-image: repeating-linear-gradient(
    90deg,
    transparent 0,
    transparent 120px,
    var(--color-board-line) 120px,
    var(--color-board-line) 121px
  );
  padding: 40px;
  min-height: 500px;
}

/* ========================================
   公告网格
   ======================================== */
.notice-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 28px;
  align-items: start;
}

/* ========================================
   公告卡片 — 奶白纸
   ======================================== */
.notice-card {
  position: relative;
  background: var(--color-paper-main);
  padding: 32px 28px;
  box-shadow: 0 4px 12px rgba(80,65,45,0.1);
  border-radius: 2px;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  cursor: default;
}
/* 微旋转：模拟手工钉便签 */
.notice-card:nth-child(1) { transform: rotate(-0.8deg); }
.notice-card:nth-child(2) { transform: rotate(0.6deg); }
.notice-card:nth-child(3) { transform: rotate(-0.5deg); }
.notice-card:nth-child(4) { transform: rotate(0.7deg); }
.notice-card:nth-child(5) { transform: rotate(-0.4deg); }

.notice-card:hover {
  transform: translateY(-4px) rotate(0deg);
  box-shadow: 0 8px 20px var(--shadow-board-deep);
}

/* 图钉 — 球体质感 */
.pin {
  position: absolute;
  top: -8px;
  left: 50%;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #E8B8A8, var(--color-stamp-red) 70%, #B07A6A 100%);
  box-shadow: 0 2px 3px rgba(0,0,0,0.2);
  transform: translateX(-50%);
  z-index: 10;
}

/* 装饰边框 */
.card-border {
  position: relative;
  margin: 6px;
  padding: 20px;
  border: 1.5px solid rgba(62,91,70,0.2);
  outline: 1px dashed rgba(62,91,70,0.12);
  outline-offset: 4px;
}

/* 卡片头部：居中 */
.card-header {
  text-align: center;
  padding-bottom: 14px;
}

/* 单条分割线，60% 宽度 */
.card-header::after {
  content: '';
  display: block;
  width: 60%;
  height: 1px;
  background: #E5DED0;
  margin: 14px auto 0;
  opacity: 0.6;
}

.card-title {
  font-size: 32px;
  color: var(--color-forest-ink);
  margin: 0;
  font-weight: 600;
  letter-spacing: 0.15em;
}

.card-title-en {
  display: block;
  font-size: 12px;
  font-weight: 400;
  color: var(--color-ink-light);
  letter-spacing: 0.3em;
  margin-top: 2px;
}

/* 卡片内容：左对齐 */
.card-content {
  text-align: left;
  min-height: 60px;
  padding: 14px 0;
}

.area-name {
  font-size: 22px;
  color: var(--color-ink-dark);
  margin: 0 0 12px;
  font-weight: 500;
}

.notice-text {
  font-size: 14px;
  color: var(--color-ink-dark);
  line-height: 1.6;
  margin: 0;
}

/* 卡片底部 */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0 0;
  border-top: 1px solid #E5DED0;
  font-size: 12px;
}

.notice-date {
  color: var(--color-ink-light);
  font-size: 12px;
}

.stamp {
  color: var(--color-accent-red);
  border: 1px solid var(--color-accent-red);
  padding: 2px 6px;
  font-size: 11px;
  letter-spacing: 1px;
  opacity: 0.7;
  transform: rotate(-3deg);
}

/* 卷角 — 渐变阴影 */
.corner-fold {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 20px;
  height: 20px;
  background: linear-gradient(135deg, transparent 50%, rgba(0,0,0,0.06) 50%, rgba(0,0,0,0.1) 100%);
  border-radius: 2px 0 0 0;
}

/* ========================================
   空状态 & 错误状态
   ======================================== */
.empty-state {
  margin-top: 80px;
}
:deep(.empty-state .n-empty__description) {
  color: var(--color-ink-light) !important;
  opacity: 0.7;
}

.error-state {
  margin-top: 80px;
}

/* ========================================
   响应式
   ======================================== */
@media (max-width: 768px) {
  .board {
    padding: 24px 16px;
    border-width: 6px;
  }
  .notice-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  .notice-content {
    padding: 16px 12px 60px;
  }
  .page-title {
    font-size: 32px;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .notice-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
