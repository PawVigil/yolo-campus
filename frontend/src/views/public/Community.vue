<template>
  <div class="community-page">
    <!-- 导航 -->
    <n-layout-header class="public-nav" bordered>
      <div class="nav-content">
        <div class="nav-brand" @click="$router.push('/')">
          <span class="brand-icon">🐾</span>
          <span class="brand-text">PawVigil</span>
        </div>
        <n-menu v-model:value="activeMenu" mode="horizontal" :options="menuOptions" @update:value="onMenuChange" />
        <n-button text @click="$router.push('/login')" class="admin-link">🔧 管理入口</n-button>
      </div>
    </n-layout-header>

    <n-layout-content class="community-content">
      <h2 class="page-title">📸 社区分享</h2>
      <p class="page-subtitle">分享你在校园里发现的可爱动物吧！</p>

      <!-- 上传区域 -->
      <n-card :bordered="false" class="upload-card">
        <n-button type="primary" @click="showUpload = true" block>
          📤 上传我的发现
        </n-button>
      </n-card>

      <n-spin :show="loading">
        <n-empty v-if="!loading && items.length === 0" description="还没有人分享，来做第一个吧！" class="empty-state" />

        <!-- 瀑布流卡片列表 -->
        <div v-else class="community-grid">
          <n-card v-for="item in items" :key="item.id" :bordered="false" class="community-card">
            <n-image :src="item.image_url" object-fit="cover" height="200" class="card-image" />
            <div class="card-info">
              <div class="card-top-row">
                <LocationBadge v-if="item.location_name" :name="item.location_name" />
                <n-tag v-if="item.breed" type="info" size="small" round>{{ item.breed }}</n-tag>
              </div>
              <p v-if="item.description" class="card-desc">{{ item.description }}</p>
              <div class="card-bottom">
                <span v-if="item.nickname" class="card-nickname">来自 {{ item.nickname }}</span>
                <span class="card-time">{{ formatDate(item.created_at) }}</span>
              </div>
            </div>
          </n-card>
        </div>
      </n-spin>

      <!-- 分页 -->
      <div v-if="total > pageSize" class="pagination-row">
        <n-pagination v-model:page="page" :page-size="pageSize" :item-count="total" @update:page="fetchList" />
      </div>

      <!-- 上传弹窗 -->
      <n-modal v-model:show="showUpload" preset="card" title="📤 上传我的发现" style="max-width: 560px" :mask-closable="true">
        <n-form label-placement="top">
          <n-form-item label="上传照片">
            <n-upload accept="image/jpeg,image/png" :max="1" @change="onFileChange">
              <n-button>选择图片（JPG/PNG, ≤10MB）</n-button>
            </n-upload>
          </n-form-item>
          <n-form-item label="选择地点（可选）">
            <n-select v-model:value="uploadForm.location_id" :options="locationOptions" placeholder="选择地点" clearable />
          </n-form-item>
          <n-form-item label="描述（可选）">
            <n-input v-model:value="uploadForm.description" type="textarea" placeholder="说说你发现了什么..." :rows="3" />
          </n-form-item>
          <n-form-item label="昵称（可选）">
            <n-input v-model:value="uploadForm.nickname" placeholder="你的昵称" maxlength="20" />
          </n-form-item>
          <n-form-item>
            <n-checkbox v-model:checked="uploadForm.auto_detect">🤖 调用 AI 识别品种</n-checkbox>
          </n-form-item>
        </n-form>
        <template #footer>
          <n-button @click="showUpload = false">取消</n-button>
          <n-button type="primary" @click="doUpload" :loading="uploading" :disabled="!uploadFile">
            {{ uploading ? '上传中...' : '确认上传' }}
          </n-button>
        </template>
      </n-modal>

      <!-- 品种小资料卡弹窗 -->
      <n-modal v-model:show="showBreedCard" preset="card" title="📋 品种小资料" style="max-width: 400px" :mask-closable="true">
        <div v-if="breedCardData" class="breed-info-card">
          <div class="breed-emoji">{{ breedCardData.emoji }}</div>
          <h3>{{ breedCardData.name_cn }}</h3>
          <n-descriptions :column="1" label-placement="left" size="small" bordered>
            <n-descriptions-item label="体型">{{ breedCardData.size }}</n-descriptions-item>
            <n-descriptions-item label="性格">{{ breedCardData.temperament }}</n-descriptions-item>
            <n-descriptions-item label="趣味知识">{{ breedCardData.fun_fact }}</n-descriptions-item>
          </n-descriptions>
        </div>
      </n-modal>
    </n-layout-content>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import LocationBadge from '@/components/LocationBadge.vue'
import { getCommunity, uploadCommunity } from '@/api/public.js'
import { getLocations } from '@/api/admin.js'

const router = useRouter()
const message = useMessage()
const activeMenu = ref('community')
const loading = ref(true)
const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 12
const showUpload = ref(false)
const showBreedCard = ref(false)
const breedCardData = ref(null)
const uploading = ref(false)
const uploadFile = ref(null)
const uploadForm = reactive({
  location_id: null,
  description: '',
  nickname: '',
  auto_detect: false,
})
const locationOptions = ref([])

const menuOptions = [
  { label: '🏠 实时大屏', key: 'live' },
  { label: '📅 出没日历', key: 'calendar' },
  { label: '🏆 排行榜', key: 'rankings' },
  { label: '🐱 撸猫指南', key: 'guide' },
  { label: '⚠️ 安全提醒', key: 'safety' },
  { label: '📸 社区分享', key: 'community' },
]

function onMenuChange(key) {
  const routeMap = { live: '/', calendar: '/calendar', rankings: '/rankings', guide: '/guide', safety: '/safety', community: '/community' }
  router.push(routeMap[key])
}

function formatDate(d) {
  if (!d) return ''
  const dt = new Date(d)
  const now = new Date()
  const diff = now - dt
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return d.slice(0, 10)
}

async function fetchList() {
  loading.value = true
  try {
    const res = await getCommunity({ page: page.value, page_size: pageSize })
    items.value = res.items || []
    total.value = res.total || 0
  } catch (e) {
    console.error('获取社区分享失败', e)
  } finally {
    loading.value = false
  }
}

async function fetchLocations() {
  try {
    const res = await getLocations()
    locationOptions.value = (res.items || []).map((l) => ({ label: l.name, value: l.id }))
  } catch (e) { /* ignore */ }
}

function onFileChange({ file }) {
  if (file && file.file) {
    uploadFile.value = file.file
  }
}

async function doUpload() {
  if (!uploadFile.value) {
    message.warning('请先选择照片')
    return
  }
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('image', uploadFile.value)
    if (uploadForm.location_id) fd.append('location_id', uploadForm.location_id)
    if (uploadForm.description) fd.append('description', uploadForm.description)
    if (uploadForm.nickname) fd.append('nickname', uploadForm.nickname)
    fd.append('auto_detect', String(uploadForm.auto_detect))

    const result = await uploadCommunity(fd)

    if (result.breed_card) {
      breedCardData.value = result.breed_card
      showBreedCard.value = true
    }

    message.success('上传成功！')
    showUpload.value = false
    uploadFile.value = null
    uploadForm.description = ''
    uploadForm.nickname = ''
    uploadForm.location_id = null
    uploadForm.auto_detect = false

    page.value = 1
    await fetchList()
  } catch (e) {
    console.error('上传失败', e)
    message.error('上传失败，请重试')
  } finally {
    uploading.value = false
  }
}

onMounted(() => {
  fetchList()
  fetchLocations()
})
</script>

<style scoped>
.community-page { min-height: 100vh; background: #f5f7fa; }
.public-nav { background: rgba(255,255,255,0.9); backdrop-filter: blur(10px); position: sticky; top: 0; z-index: 100; }
.nav-content { max-width: 1200px; margin: 0 auto; display: flex; align-items: center; padding: 0 20px; height: 56px; }
.nav-brand { display: flex; align-items: center; gap: 8px; cursor: pointer; margin-right: 24px; }
.brand-icon { font-size: 24px; }
.brand-text { font-size: 18px; font-weight: 700; color: #7c5ce7; }
.admin-link { margin-left: auto; }
.community-content { max-width: 1100px; margin: 0 auto; padding: 24px 20px; }
.page-title { text-align: center; font-size: 28px; margin-bottom: 4px; }
.page-subtitle { text-align: center; color: #909399; margin-bottom: 24px; }
.upload-card { margin-bottom: 24px; }
.empty-state { margin-top: 80px; }
.community-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }
.community-card { transition: transform 0.2s; }
.community-card:hover { transform: translateY(-3px); }
.card-image { width: 100%; border-radius: 8px; }
.card-info { padding-top: 12px; }
.card-top-row { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 8px; }
.card-desc { font-size: 14px; color: #555; line-height: 1.5; margin: 8px 0; }
.card-bottom { display: flex; justify-content: space-between; font-size: 12px; color: #909399; }
.card-nickname { color: #7c5ce7; }
.pagination-row { display: flex; justify-content: center; margin-top: 24px; }
.breed-info-card { text-align: center; }
.breed-emoji { font-size: 64px; margin-bottom: 12px; }
</style>
