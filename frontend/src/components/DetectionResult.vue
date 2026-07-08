<template>
  <div class="detection-result">
    <n-grid :cols="2" :x-gap="16" responsive="screen">
      <n-grid-item>
        <div class="image-panel">
          <div class="image-label">📷 原图</div>
          <n-image :src="imageUrl" :fallback-src="placeholderUrl" object-fit="contain" class="detect-image" />
        </div>
      </n-grid-item>
      <n-grid-item>
        <div class="image-panel">
          <div class="image-label">🔍 标注图</div>
          <n-image :src="annotatedUrl" :fallback-src="placeholderUrl" object-fit="contain" class="detect-image" />
        </div>
      </n-grid-item>
    </n-grid>

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
  if (conf >= 0.9) return '#18a058'
  if (conf >= 0.7) return '#f0a020'
  return '#d03050'
}
</script>

<style scoped>
.detection-result {
  width: 100%;
}
.image-panel {
  text-align: center;
}
.image-label {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
}
.detect-image {
  width: 100%;
  max-height: 300px;
  border-radius: 8px;
  border: 1px solid #eee;
}
.result-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.result-header h4 {
  margin: 0;
}
.breed-name {
  margin-left: 6px;
}
.box-coords {
  font-family: monospace;
  font-size: 12px;
  color: #909399;
}
</style>
