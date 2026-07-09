<template>
  <n-modal v-model:show="showModal" preset="card" title="🐾 分享卡片预览" style="max-width: 640px" :mask-closable="true">
    <div class="share-card-preview">
      <div class="card-body">
        <div class="card-header">
          <div class="card-emoji">{{ emoji }}</div>
          <div class="card-breed">我遇到了 {{ breedCn }}！</div>
        </div>
        <div class="card-info">
          <div class="info-item">
            <div class="info-label">📍 地点</div>
            <div class="info-value">{{ locationName }}</div>
          </div>
          <div class="info-item">
            <div class="info-label">🕐 时间</div>
            <div class="info-value">{{ detectTime?.slice(0, 10) }}</div>
          </div>
          <div class="info-item">
            <div class="info-label">🎯 置信度</div>
            <div class="info-value">{{ confidencePercent }}%</div>
          </div>
        </div>
        <div v-if="funFact" class="card-fun-fact">💡 {{ funFact }}</div>
        <div class="card-footer">🐾 PawVigil · 校园流浪动物观测关爱系统</div>
      </div>
    </div>
    <template #footer>
      <n-button @click="openCard">在新窗口打开</n-button>
    </template>
  </n-modal>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  show: { type: Boolean, default: false },
  breedCn: { type: String, default: '未知' },
  breedEn: { type: String, default: '' },
  emoji: { type: String, default: '🐾' },
  locationName: { type: String, default: '' },
  detectTime: { type: String, default: '' },
  confidence: { type: Number, default: 0 },
  funFact: { type: String, default: '' },
  detectionId: { type: [Number, String], default: 0 },
})

const emit = defineEmits(['update:show'])

const showModal = computed({
  get: () => props.show,
  set: (v) => emit('update:show', v),
})

const confidencePercent = computed(() => Math.round(props.confidence * 100))
const shareUrl = computed(() => `/api/public/share-card/${props.detectionId}`)

function openCard() {
  window.open(shareUrl.value, '_blank')
}
</script>

<style scoped>
.share-card-preview {
  width: 100%;
}
.card-body {
  background: var(--color-cream-paper);
  color: var(--color-forest-ink);
  border: 1px solid var(--color-pencil-gray);
  border-radius: var(--radius-card);
  padding: 32px;
  text-align: center;
}
.card-emoji {
  font-size: 64px;
}
.card-breed {
  font-family: var(--font-body);
  font-size: 24px;
  font-weight: var(--weight-bold);
  margin-top: 8px;
}
.card-info {
  display: flex;
  justify-content: space-around;
  margin: 20px 0;
}
.info-label {
  font-size: 12px;
  color: var(--color-whisper-gray);
}
.info-value {
  font-size: 18px;
  font-weight: var(--weight-bold);
}
.card-fun-fact {
  font-size: 14px;
  line-height: 1.5;
  margin-top: 15px;
}
.card-footer {
  margin-top: 20px;
  font-size: 12px;
  color: var(--color-whisper-gray);
}
</style>
