<template>
  <span class="animal-emoji" :title="displayName">{{ emoji }}</span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  breedEn: { type: String, default: '' },
  fallback: { type: String, default: '🐾' },
})

// 品种 emoji 映射表
const emojiMap = {
  Abyssinian: '🐱', Bengal: '🐆', Birman: '🐱', Bombay: '🐈‍⬛',
  British_Shorthair: '🐱', Egyptian_Mau: '🐱', Maine_Coon: '🐱',
  Persian: '🐱', Ragdoll: '🐱', Russian_Blue: '🐱', Siamese: '🐱',
  Sphynx: '🐈‍⬛',
  american_bulldog: '🐕', american_pit_bull_terrier: '🐕',
  basset_hound: '🐕', beagle: '🐕', boxer: '🐕', chihuahua: '🐶',
  english_cocker_spaniel: '🐕', english_setter: '🐕',
  german_shorthaired: '🐕', great_pyrenees: '🦮', havanese: '🐶',
  japanese_chin: '🐶', keeshond: '🐕', leonberger: '🦮',
  miniature_pinscher: '🐶', newfoundland: '🦮', pomeranian: '🐶',
  pug: '🐶', saint_bernard: '🦮', samoyed: '🐕',
  scottish_terrier: '🐕', shiba_inu: '🐕',
  staffordshire_bull_terrier: '🐕', wheaten_terrier: '🐕',
  yorkshire_terrier: '🐶',
}

const emoji = computed(() => {
  // 尝试多种匹配方式
  const key = props.breedEn
  if (emojiMap[key]) return emojiMap[key]
  // 尝试 snake_case
  const snake = key.replace(/\s+/g, '_').toLowerCase()
  if (emojiMap[snake]) return emojiMap[snake]
  // 尝试 title case 匹配
  for (const [k, v] of Object.entries(emojiMap)) {
    if (k.toLowerCase() === key.toLowerCase()) return v
  }
  return props.fallback
})

const displayName = computed(() => props.breedEn || '未知品种')
</script>

<style scoped>
.animal-emoji {
  font-size: 1.2em;
}
</style>
