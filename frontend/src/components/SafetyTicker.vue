<template>
  <div class="safety-ticker" v-if="tips.length > 0">
    <div class="ticker-label">⚠️ 安全提醒</div>
    <div class="ticker-content">
      <div class="ticker-scroll" :style="{ animationDuration: `${tips.length * 6}s` }">
        <span v-for="(tip, i) in tips" :key="i" class="ticker-item">
          <LocationBadge :name="tip.location_name" />
          {{ tip.content }}
          <span v-if="i < tips.length - 1" class="ticker-sep">｜</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import LocationBadge from './LocationBadge.vue'

defineProps({
  tips: { type: Array, default: () => [] },
})
</script>

<style scoped>
.safety-ticker {
  display: flex;
  align-items: center;
  background: var(--color-cream-paper);
  border: 1px solid var(--color-pencil-gray);
  border-left: 3px solid var(--color-terracotta);
  border-radius: var(--radius-card);
  padding: 12px 16px;
  overflow: hidden;
  width: 100%;
}
.ticker-label {
  flex-shrink: 0;
  font-family: var(--font-body);
  font-weight: var(--weight-semibold);
  font-size: 14px;
  color: var(--color-terracotta);
  margin-right: 16px;
  white-space: nowrap;
}
.ticker-content {
  flex: 1;
  overflow: hidden;
  position: relative;
}
.ticker-scroll {
  display: inline-block;
  white-space: nowrap;
  animation: ticker-scroll linear infinite;
}
.ticker-item {
  font-size: 14px;
  color: var(--color-forest-ink);
}
.ticker-sep {
  color: var(--color-pencil-gray);
  margin: 0 16px;
}
@keyframes ticker-scroll {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}
</style>
