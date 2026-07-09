<template>
  <div class="detection-result">
    <div class="image-row">
      <div class="image-panel">
        <div class="image-label">📷 原图</div>
        <n-image :src="imageUrl" :fallback-src="placeholderUrl" class="detect-image" />
      </div>
      <div class="image-panel">
        <div class="image-label">🔍 标注图</div>
        <n-image :src="annotatedUrl" :fallback-src="placeholderUrl" class="detect-image" />
      </div>
    </div>

    <n-divider />

    <div class="result-header">
      <h4>检测结果（共 {{ animals.length }} 只动物）</h4>
      <n-tag v-if="animals.length > 0" type="success" round>YOLOv8 检测</n-tag>
      <n-tag v-else type="warning" round>未检测到动物</n-tag>
    </div>

    <n-table v-if="animals.length > 0" :single-line="false" :bordered="false" size="small">
      <thead>
        <tr>
          <th>品种</th>
          <th>英文名</th>
          <th>置信度</th>
          <th>位置 (x1, y1, x2, y2)</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(a, i) in animals" :key="i">
          <td>
            <AnimalEmoji :breed-en="a.breed_en" />
            <span class="breed-name">{{ a.breed_cn }}</span>
          </td>
          <td>{{ a.breed_en }}</td>
          <td>
            <n-progress type="line" :percentage="Math.round(a.confidence * 100)" :height="20" :border-radius="4" :color="confColor(a.confidence)" :indicator-placement="'inside'" />
          </td>
          <td class="box-coords">({{ a.box.x1 }}, {{ a.box.y1 }}) → ({{ a.box.x2 }}, {{ a.box.y2 }})</td>
        </tr>
      </tbody>
    </n-table>

    <n-empty v-else description="未检测到动物" />
  </div>
</template>

<script setup>
import AnimalEmoji from './AnimalEmoji.vue'

const props = defineProps({
  imageUrl: { type: String, default: '' },
  annotatedUrl: { type: String, default: '' },
  animals: { type: Array, default: () => [] },
})

const placeholderUrl = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"><rect fill="%23f0f0f0" width="400" height="300"/><text x="200" y="150" text-anchor="middle" fill="%23ccc" font-size="16">暂无图片</text></svg>'

function confColor(conf) {
  if (conf >= 0.9) return '#1a3300'
  if (conf >= 0.7) return '#4a6a2a'
  return '#e89970'
}
</script>

<style scoped>
.detection-result {
  width: 100%;
}
.image-row {
  display: flex;
  gap: 16px;
  width: 100%;
}
.image-panel {
  flex: 1;
  min-width: 0;
}
.image-label {
  font-family: var(--font-body);
  font-size: 14px;
  font-weight: var(--weight-medium);
  color: var(--color-forest-ink);
  margin-bottom: 8px;
}
.detect-image {
  width: 100%;
  max-height: 400px;
  border-radius: var(--radius-image);
  border: 1px solid var(--color-pencil-gray);
}
.detect-image :deep(img) {
  width: 100%;
  max-height: 400px;
  object-fit: contain;
}
.result-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.result-header h4 {
  margin: 0;
  font-family: var(--font-body);
  font-weight: var(--weight-semibold);
  color: var(--color-forest-ink);
}
.breed-name {
  margin-left: 6px;
}
.box-coords {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--color-pencil-gray);
}
</style>
