<template>
  <div
    class="sticky-note"
    :class="{ 'sticky-note--hoverable': hoverable }"
    :style="noteStyle"
  >
    <div class="sticky-note__tear"></div>
    <div class="sticky-note__content">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  color: { type: String, default: 'var(--surface-cream)' },
  rotate: { type: Number, default: 0 },
  hoverable: { type: Boolean, default: true },
})

const noteStyle = computed(() => ({
  background: props.color,
  transform: props.rotate ? `rotate(${props.rotate}deg)` : undefined,
}))
</script>

<style scoped>
.sticky-note {
  position: relative;
  border-radius: 10px 14px 12px 8px;
  padding: 20px 24px 24px;
  box-shadow:
    2px 2px 0 rgba(0, 0, 0, 0.04),
    0 1px 3px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.sticky-note--hoverable:hover {
  transform: rotate(0deg) translateY(-2px) !important;
  box-shadow:
    3px 3px 0 rgba(0, 0, 0, 0.06),
    0 4px 12px rgba(0, 0, 0, 0.08);
}

/* Torn top edge — subtle zigzag */
.sticky-note__tear {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 6px;
  background:
    linear-gradient(135deg, transparent 33.3%, rgba(0,0,0,0.03) 33.3%, rgba(0,0,0,0.03) 66.6%, transparent 66.6%) 0 0 / 8px 6px repeat-x;
  border-radius: 10px 14px 0 0;
  pointer-events: none;
}

.sticky-note__content {
  position: relative;
  z-index: 1;
}
</style>
