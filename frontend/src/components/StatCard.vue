<template>
  <n-card :bordered="false" class="stat-card" :style="{ borderLeft: `4px solid ${color}` }">
    <div class="stat-content">
      <div class="stat-icon" :style="{ color }">
        <n-icon :size="28">
          <component :is="icon" />
        </n-icon>
      </div>
      <div class="stat-info">
        <div class="stat-value">{{ formattedValue }}</div>
        <div class="stat-label">{{ label }}</div>
      </div>
    </div>
  </n-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  icon: { type: Object, required: true },
  value: { type: [Number, String], required: true },
  label: { type: String, required: true },
  color: { type: String, default: '#7c5ce7' },
})

const formattedValue = computed(() => {
  if (typeof props.value === 'number' && props.value >= 1000) {
    return (props.value / 1000).toFixed(1) + 'k'
  }
  return String(props.value)
})
</script>

<style scoped>
.stat-card {
  transition: transform 0.2s;
}
.stat-card:hover {
  transform: translateY(-2px);
}
.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}
.stat-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: currentColor;
  color: #fff !important;
}
.stat-icon :deep(.n-icon) {
  color: #fff;
}
.stat-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
}
.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 2px;
}
</style>
