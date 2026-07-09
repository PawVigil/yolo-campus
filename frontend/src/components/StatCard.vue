<template>
  <!-- Naked variant: bare numbers, no card wrapper -->
  <div v-if="variant === 'naked'" class="stat-naked">
    <div class="stat-naked-value">{{ formattedValue }}</div>
    <div class="stat-naked-label">{{ label }}</div>
  </div>

  <!-- Sticky variant (default): pastel-filled sticky note -->
  <StickyNote v-else :color="surfaceColor" :hoverable="true">
    <div class="stat-sticky-icon" v-if="icon">
      <n-icon :size="24"><component :is="icon" /></n-icon>
    </div>
    <div class="stat-sticky-value">{{ formattedValue }}</div>
    <div class="stat-sticky-label">{{ label }}</div>
  </StickyNote>
</template>

<script setup>
import { computed } from 'vue'
import StickyNote from './StickyNote.vue'

const props = defineProps({
  icon: { type: Object, default: null },
  value: { type: [Number, String], required: true },
  label: { type: String, required: true },
  color: { type: String, default: '#1a3300' },
  variant: { type: String, default: 'sticky' },  // 'sticky' | 'naked'
})

const formattedValue = computed(() => {
  if (typeof props.value === 'number' && props.value >= 1000) {
    return (props.value / 1000).toFixed(1) + 'k'
  }
  return String(props.value)
})

const surfaceColor = computed(() => {
  const map = {
    '#7c5ce7': 'var(--surface-mint)',
    '#18a058': 'var(--surface-teal)',
    '#f0a020': 'var(--surface-highlighter)',
    '#2080f0': 'var(--surface-blush)',
    '#1a3300': 'var(--surface-mint)',
  }
  return map[props.color] || 'var(--surface-cream)'
})
</script>

<style scoped>
/* ===== Naked variant ===== */
.stat-naked {
  text-align: center;
}

.stat-naked-value {
  font-family: var(--font-mono);
  font-weight: var(--weight-bold);
  font-size: var(--text-display);
  line-height: var(--leading-display);
  color: var(--color-forest-ink);
  font-feature-settings: 'tnum';
}

.stat-naked-label {
  font-family: var(--font-body);
  font-weight: var(--weight-regular);
  font-size: var(--text-body-sm);
  color: var(--color-whisper-gray);
  margin-top: 4px;
}

/* ===== Sticky variant (StickyNote handles the card) ===== */
.stat-sticky-icon {
  margin-bottom: 8px;
  color: var(--color-forest-ink);
  text-align: center;
}
.stat-sticky-value {
  font-family: var(--font-mono);
  font-weight: var(--weight-bold);
  font-size: 32px;
  color: var(--color-forest-ink);
  text-align: center;
  font-feature-settings: 'tnum';
}
.stat-sticky-label {
  font-family: var(--font-body);
  font-weight: var(--weight-medium);
  font-size: var(--text-body-sm);
  color: var(--color-forest-ink);
  text-align: center;
  margin-top: 4px;
}
</style>
