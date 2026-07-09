<template>
  <span class="ink-tag" :class="[`ink-tag--${variant}`, { 'ink-tag--round': round }]">
    <slot />
  </span>
</template>

<script setup>
defineProps({
  variant: { type: String, default: 'ink' },   // 'ink' | 'mint' | 'terracotta' | 'highlighter' | 'ghost'
  round: { type: Boolean, default: true },
})
</script>

<style scoped>
.ink-tag {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-family: var(--font-body);
  font-size: 12px;
  font-weight: var(--weight-medium);
  line-height: 1;
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.ink-tag--round {
  border-radius: var(--radius-full);
}

/* 墨色：深绿底白字 */
.ink-tag--ink {
  background: var(--color-forest-ink);
  color: var(--color-cream-paper);
}

/* 薄荷底 */
.ink-tag--mint {
  background: var(--surface-mint);
  color: var(--color-forest-ink);
}

/* 陶土底 */
.ink-tag--terracotta {
  background: var(--surface-terracotta);
  color: var(--color-forest-ink);
}

/* 荧光笔黄底 */
.ink-tag--highlighter {
  background: var(--surface-highlighter);
  color: var(--color-forest-ink);
}

/* 幽灵：线框 */
.ink-tag--ghost {
  background: transparent;
  color: var(--color-forest-ink);
  border: 1px solid var(--color-pencil-gray);
}
</style>
