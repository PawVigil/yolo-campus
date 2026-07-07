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
  background: linear-gradient(90deg, #fff3e0, #ffe0b2);
  border: 1px solid #ffcc80;
  border-radius: 8px;
  padding: 10px 16px;
  overflow: hidden;
  width: 100%;
}
.ticker-label {
  flex-shrink: 0;
  font-weight: 700;
  font-size: 14px;
  color: #e65100;
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
  color: #5d4037;
}
.ticker-sep {
  color: #ffcc80;
  margin: 0 16px;
}
@keyframes ticker-scroll {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}
</style>
