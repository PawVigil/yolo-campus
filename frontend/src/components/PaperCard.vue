<template>
  <div
    class="paper-card"
    :class="{
      'paper-card--hoverable': hoverable,
      [`paper-card--stripe-${stripe}`]: stripe && stripe !== 'none',
    }"
    :style="cardStyle"
  >
    <!-- 撕边装饰线 -->
    <div v-if="stripe && stripe !== 'none'" class="paper-card__stripe"></div>
    <!-- 内容 -->
    <div class="paper-card__body">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  /** 'none' | 'ink' | 'mint' | 'terracotta' | 'teal' | 'blush' | 'sand' | 'highlighter' */
  stripe: { type: String, default: 'none' },
  /** 微旋转角度（度），模拟便签 */
  tilt: { type: Number, default: 0 },
  hoverable: { type: Boolean, default: true },
  /** 'sm' | 'md' | 'lg' */
  padding: { type: String, default: 'md' },
})

const padMap = { sm: '14px 18px', md: '20px 24px', lg: '28px 32px' }

const cardStyle = computed(() => ({
  padding: padMap[props.padding] || padMap.md,
  transform: props.tilt ? `rotate(${props.tilt}deg)` : undefined,
}))
</script>

<style scoped>
/* ================================
   Paper Card — 纸张卡片
   替代 n-card 的通用白底阴影
   ================================ */

.paper-card {
  position: relative;
  background: var(--color-cream-paper);
  border-radius: 4px 12px 12px 4px;
  /* 单侧光阴影 — 不是通用 box-shadow */
  box-shadow:
    2px 2px 0 rgba(26, 51, 0, 0.04),
    0 1px 4px rgba(26, 51, 0, 0.05);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

/* 纸质纹理 */
.paper-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background:
    url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
  pointer-events: none;
  z-index: 0;
}

.paper-card__body {
  position: relative;
  z-index: 1;
}

/* ---- 色条（左边缘）---- */
.paper-card__stripe {
  position: absolute;
  left: 0;
  top: 8px;
  bottom: 8px;
  width: 4px;
  border-radius: 4px 0 0 4px;
  z-index: 2;
}
.paper-card--stripe-ink .paper-card__stripe {
  background: var(--color-forest-ink);
}
.paper-card--stripe-mint .paper-card__stripe {
  background: var(--color-mint);
}
.paper-card--stripe-terracotta .paper-card__stripe {
  background: var(--color-terracotta);
}
.paper-card--stripe-teal .paper-card__stripe {
  background: var(--color-teal);
}
.paper-card--stripe-blush .paper-card__stripe {
  background: var(--color-blush);
}
.paper-card--stripe-sand .paper-card__stripe {
  background: var(--color-sand);
}
.paper-card--stripe-highlighter .paper-card__stripe {
  background: var(--color-highlighter-yellow);
}

/* ---- 悬停 ---- */
.paper-card--hoverable:hover {
  transform: rotate(0deg) translateY(-2px) !important;
  box-shadow:
    3px 3px 0 rgba(26, 51, 0, 0.06),
    0 4px 12px rgba(26, 51, 0, 0.08);
}
</style>
