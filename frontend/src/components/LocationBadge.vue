<template>
  <n-tag :bordered="false" :color="{ color: bgColor, textColor: textColor }" round size="small">
    <template #icon>
      <span class="location-emoji">{{ emoji }}</span>
    </template>
    {{ name }}
  </n-tag>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: { type: String, required: true },
})

const locationPalette = {
  '食堂':   { emoji: '🍽️', bg: '#e89970', text: '#1a3300' },
  '宿舍':   { emoji: '🏠', bg: '#f6d0ff', text: '#1a3300' },
  '图书馆': { emoji: '📚', bg: '#a8e5e5', text: '#1a3300' },
  '操场':   { emoji: '🏟️', bg: '#e8e0d5', text: '#1a3300' },
  '花园':   { emoji: '🌳', bg: '#d5f5c2', text: '#1a3300' },
}

const emoji = computed(() => locationPalette[props.name]?.emoji || '📍')
const bgColor = computed(() => locationPalette[props.name]?.bg || '#f5f5f5')
const textColor = computed(() => locationPalette[props.name]?.text || '#333')
</script>

<style scoped>
.location-emoji {
  font-size: 14px;
}
</style>
