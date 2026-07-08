<template>
  <div class="upload-page">
    <h2 class="page-title">📤 上传图片检测</h2>

    <n-grid :cols="2" :x-gap="16" responsive="screen">
      <!-- 左侧：上传区域 -->
      <n-grid-item>
        <n-card :bordered="false" title="1️⃣ 选择地点并上传图片">
          <n-form label-placement="top">
            <n-form-item label="拍摄地点" required>
              <n-select
                v-model:value="selectedLocation"
                :options="locationOptions"
                placeholder="选择拍摄地点"
                :loading="loadingLocations"
              />
            </n-form-item>
          </n-form>

          <n-upload
            ref="uploadRef"
            :multiple="false"
            accept="image/jpeg,image/png"
            :max="1"
            @change="onFileChange"
            :show-file-list="false"
          >
            <n-upload-dragger>
              <div class="upload-dragger-content">
                <n-icon size="48" class="upload-icon">📷</n-icon>
                <p class="upload-text">点击或拖拽图片到此处</p>
                <p class="upload-hint">支持 JPG / PNG，单文件 ≤ 10MB</p>
              </div>
            </n-upload-dragger>
          </n-upload>

          <div v-if="uploadFile" class="file-info">
            <n-tag type="info" round>{{ uploadFile.name }} ({{ formatSize(uploadFile.size) }})</n-tag>
          </div>

          <n-button
            type="primary"
            block
            size="large"
            :loading="detecting"
            :disabled="!uploadFile || !selectedLocation"
            @click="doDetect"
            class="detect-btn"
          >
            {{ detecting ? '🔍 AI 检测中...' : '🔍 开始检测' }}
          </n-button>
        </n-card>
      </n-grid-item>

      <!-- 右侧：检测进度/状态提示 -->
      <n-grid-item>
        <n-card :bordered="false" title="ℹ️ 操作提示">
          <n-empty v-if="!detecting && !detectResult" description="等待上传...">
            <template #extra>
              <ul class="tip-list">
                <li>选择一个拍摄地点</li>
                <li>上传一张 JPG 或 PNG 图片</li>
                <li>点击"开始检测"按钮</li>
                <li>查看检测结果，确认后保存</li>
              </ul>
            </template>
          </n-empty>
          <div v-if="detecting" class="detecting-status">
            <n-spin size="large" />
            <p>正在使用 YOLOv8 模型检测中...</p>
            <p class="sub-text">CPU 模式下单张约需 3-10 秒</p>
          </div>
        </n-card>
      </n-grid-item>
    </n-grid>

    <!-- 检测结果 -->
    <div v-if="detectResult" class="result-section">
      <n-divider />
      <h3>📊 检测结果预览</h3>
      <DetectionResult
        :image-url="detectResult.image_url"
        :annotated-url="detectResult.annotated_url"
        :animals="detectResult.animals"
      />

      <div class="result-actions">
        <n-button type="primary" size="large" :loading="saving" @click="doSave">
          💾 保存检测记录
        </n-button>
        <n-button size="large" @click="resetDetect">
          🔄 重新上传
        </n-button>
        <n-button size="large" @click="shareToCommunity" v-if="saveSuccess && detectResult.animals.length > 0">
          📸 分享到社区
        </n-button>
      </div>

      <n-alert v-if="saveSuccess" type="success" title="保存成功" class="save-alert">
        检测记录已保存到数据库，可在「记录管理」中查看。
        <template #footer>
          <n-button size="small" @click="$router.push('/admin/records')">前往记录管理 →</n-button>
        </template>
      </n-alert>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import DetectionResult from '@/components/DetectionResult.vue'
import { uploadImage, saveDetection, getLocations } from '@/api/admin.js'

const router = useRouter()
const message = useMessage()

const selectedLocation = ref(null)
const locationOptions = ref([])
const loadingLocations = ref(false)
const uploadFile = ref(null)
const uploadRef = ref(null)
const detecting = ref(false)
const saving = ref(false)
const saveSuccess = ref(false)
const savedId = ref(null)
const detectResult = ref(null)

const locationName = computed(() => {
  const loc = locationOptions.value.find((l) => l.value === selectedLocation.value)
  return loc?.label || ''
})

const emojiMap = {
  Abyssinian: '🐱', Bengal: '🐆', Birman: '🐱', Bombay: '🐈‍⬛',
  British_Shorthair: '🐱', Egyptian_Mau: '🐱', Maine_Coon: '🐱',
  Persian: '🐱', Ragdoll: '🐱', Russian_Blue: '🐱', Siamese: '🐱', Sphynx: '🐈‍⬛',
}

function getEmoji(breedEn) {
  if (!breedEn) return '🐾'
  const key = breedEn.replace(/\s+/g, '_')
  return emojiMap[key] || (breedEn.toLowerCase().includes('dog') || breedEn.toLowerCase().includes('bulldog') || breedEn.toLowerCase().includes('terrier') ? '🐕' : '🐱')
}

function getLocalTime() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}:${String(d.getSeconds()).padStart(2,'0')}`
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + 'B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + 'KB'
  return (bytes / 1024 / 1024).toFixed(1) + 'MB'
}

function onFileChange({ file }) {
  if (file && file.file) {
    const f = file.file
    if (f.size > 10 * 1024 * 1024) {
      message.error('文件大小超过 10MB 限制')
      return
    }
    uploadFile.value = f
  }
}

async function doDetect() {
  if (!uploadFile.value || !selectedLocation.value) return
  detecting.value = true
  saveSuccess.value = false
  try {
    const res = await uploadImage(uploadFile.value, selectedLocation.value)
    detectResult.value = res
    message.success(`检测完成！发现 ${res.total} 只动物`)
  } catch (e) {
    console.error('检测失败', e)
    message.error(e?.response?.data?.detail || '检测失败，请检查图片格式或网络连接')
  } finally {
    detecting.value = false
  }
}

async function doSave() {
  if (!detectResult.value) return
  saving.value = true
  try {
    const res = await saveDetection({
      location_id: selectedLocation.value,
      image_path: detectResult.value.image_url,
      annotated_path: detectResult.value.annotated_url,
      detect_time: getLocalTime(),
      result_json: JSON.stringify(detectResult.value.animals),
      total_animals: detectResult.value.total,
    })
    savedId.value = res.id
    saveSuccess.value = true
    message.success('记录已保存！')
  } catch (e) {
    console.error('保存失败', e)
    message.error('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

function resetDetect() {
  detectResult.value = null
  uploadFile.value = null
  uploadRef.value?.clear()
  saveSuccess.value = false
  savedId.value = null
}

function shareToCommunity() {
  if (!detectResult.value) return
  const img = encodeURIComponent(detectResult.value.image_url || '')
  const loc = selectedLocation.value || ''
  router.push(`/admin/community?share_image=${img}&share_location=${loc}`)
}

onMounted(async () => {
  loadingLocations.value = true
  try {
    const res = await getLocations()
    locationOptions.value = (res.items || []).map((l) => ({ label: l.name, value: l.id }))
  } catch (e) {
    console.error('获取地点失败', e)
  } finally {
    loadingLocations.value = false
  }
})
</script>

<style scoped>
.upload-page { max-width: 1100px; margin: 0 auto; }
.page-title { margin-bottom: 20px; font-size: 22px; color: var(--color-forest-ink); }
.upload-dragger-content { padding: 20px; }
.upload-icon { opacity: 0.5; }
.upload-text { font-size: 16px; margin: 10px 0 4px; color: var(--color-forest-ink); }
.upload-hint { font-size: 13px; color: var(--color-whisper-gray); }
.file-info { margin-top: 12px; }
.detect-btn { margin-top: 20px; }
.tip-list { text-align: left; color: var(--color-forest-ink); font-size: 14px; }
.tip-list li { margin-bottom: 6px; }
.detecting-status { text-align: center; padding: 40px; }
.detecting-status p { font-size: 16px; margin-top: 16px; color: var(--color-forest-ink); }
.sub-text { font-size: 13px !important; color: var(--color-whisper-gray) !important; }
.result-section { margin-top: 24px; }
.result-actions { display: flex; gap: 12px; margin-top: 20px; }
.save-alert { margin-top: 16px; }
</style>
