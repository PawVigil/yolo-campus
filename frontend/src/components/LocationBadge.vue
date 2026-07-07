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
  '食堂': { emoji: '🍽️', bg: '#fff3e0', text: '#e65100' },
  '宿舍': { emoji: '🏠', bg: '#e8f5e9', text: '#2e7d32' },
  '图书馆': { emoji: '📚', bg: '#e3f2fd', text: '#1565c0' },
  '操场': { emoji: '🏟️', bg: '#fce4ec', text: '#c62828' },
  '花园': { emoji: '🌳', bg: '#e8eaf6', text: '#283593' },
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
