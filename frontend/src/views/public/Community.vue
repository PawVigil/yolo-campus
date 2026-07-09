<template>
  <div class="community-page">
    <PublicNav menu-key="community" />

    <n-layout-content class="community-content">
      <h2 class="page-title">📸 社区分享</h2>
      <p class="page-subtitle">分享你在校园里发现的可爱动物吧！</p>

      <!-- 日期筛选 + 上传 -->
      <div class="top-bar">
        <n-date-picker v-model:value="filterDate" type="date" placeholder="选择日期筛选" clearable @update:value="onDateFilter" />
        <n-button type="primary" @click="showUpload = true">📤 上传分享</n-button>
      </div>

      <!-- 分享卡片列表 -->
      <n-spin :show="loading">
        <div v-if="!loading && items.length === 0" class="empty-state">
          <div class="empty-illustration">🐾</div>
          <p class="empty-title">今天还没有人分享</p>
          <p class="empty-hint">成为第一个分享校园可爱动物的人吧！</p>
        </div>
        <div v-else class="community-grid">
          <n-card v-for="item in items" :key="item.id" :bordered="false" class="community-card" @click="openDetail(item)">
            <img :src="item.images[0]" class="cover-image" height="300" />
            <div class="card-info">
              <div class="card-top-row">
                <LocationBadge v-if="item.location_name" :name="item.location_name" />
                <n-tag v-if="item.breed" type="info" size="small" round>{{ item.breed }}</n-tag>
                <span class="photo-count">{{ item.images.length }} 张</span>
              </div>
              <p v-if="item.description" class="card-desc">{{ item.description }}</p>
              <div class="card-bottom">
                <span v-if="item.nickname" class="card-nickname">{{ item.nickname }}</span>
                <span class="card-time">{{ fmtTime(item.created_at) }}</span>
                <span class="card-comments">💬 {{ item.comments?.length || 0 }}</span>
              </div>
            </div>
          </n-card>
        </div>
      </n-spin>
    </n-layout-content>

    <!-- 详情弹窗：多图+评论 -->
    <n-modal v-model:show="showDetail" preset="card" title="📸 分享详情" style="max-width: 680px" :mask-closable="true">
      <template v-if="detailItem">
        <!-- 图片轮播 -->
        <div class="gallery">
          <n-image v-for="(img, i) in detailItem.images" :key="i" :src="img" object-fit="contain" class="gallery-img" />
        </div>
        <div class="detail-info">
          <p v-if="detailItem.description">{{ detailItem.description }}</p>
          <div class="detail-meta">
            <LocationBadge v-if="detailItem.location_name" :name="detailItem.location_name" />
            <n-tag v-if="detailItem.breed" type="info" size="small">{{ detailItem.breed }}</n-tag>
            <span v-if="detailItem.nickname">by {{ detailItem.nickname }}</span>
            <span>{{ fmtTime(detailItem.created_at) }}</span>
          </div>
        </div>

        <n-divider />

        <!-- 评论区 -->
        <div class="comments-section">
          <h4>💬 评论（{{ detailItem.comments?.length || 0 }}）</h4>
          <div v-if="!detailItem.comments?.length" class="no-comments">暂无评论</div>
          <div v-for="c in detailItem.comments" :key="c.id" class="comment-item">
            <span class="comment-nick">{{ c.nickname || '匿名' }}</span>
            <span class="comment-text">{{ c.text }}</span>
            <span class="comment-time">{{ fmtTime(c.time) }}</span>
          </div>
          <div class="comment-input">
            <n-input v-model:value="commentNick" placeholder="昵称（选填）" size="small" class="nick-input" />
            <n-input v-model:value="commentText" placeholder="说点什么..." size="small" @keyup.enter="doComment" />
            <n-button size="small" type="primary" @click="doComment" :disabled="!commentText.trim()">发送</n-button>
          </div>
        </div>
      </template>
    </n-modal>

    <!-- 上传弹窗 -->
    <n-modal v-model:show="showUpload" preset="card" title="📤 分享你的发现" style="max-width: 560px" :mask-closable="true">
      <n-form label-placement="top">
        <n-form-item label="选择照片（可多张）">
          <n-upload multiple accept="image/jpeg,image/png" :max="9" @change="onFilesChange">
            <n-button>选择照片（JPG/PNG）</n-button>
          </n-upload>
          <div v-if="uploadFiles.length > 0" class="upload-preview">
            <span v-for="(f, i) in uploadFiles" :key="i" class="preview-chip">{{ f.name }}</span>
          </div>
        </n-form-item>
        <n-form-item label="地点（可选）">
          <n-select v-model:value="uploadForm.location_id" :options="locationOptions" placeholder="选择地点" clearable />
        </n-form-item>
        <n-form-item label="描述（可选）">
          <n-input v-model:value="uploadForm.description" type="textarea" placeholder="说说你发现了什么..." :rows="3" />
        </n-form-item>
        <n-form-item label="昵称（可选）">
          <n-input v-model:value="uploadForm.nickname" placeholder="你的昵称" maxlength="20" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-button @click="showUpload = false">取消</n-button>
        <n-button type="primary" @click="doUpload" :loading="uploading" :disabled="uploadFiles.length === 0">
          {{ uploading ? '上传中...' : '确认分享' }}
        </n-button>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PublicNav from '@/components/PublicNav.vue'
import { useMessage } from 'naive-ui'
import LocationBadge from '@/components/LocationBadge.vue'
import { getCommunity, uploadCommunity, addComment, getPublicLocations } from '@/api/public.js'

const router = useRouter()
const message = useMessage()
const loading = ref(false)
const items = ref([])
const filterDate = ref(Date.now())
const showDetail = ref(false)
const detailItem = ref(null)
const showUpload = ref(false)
const uploading = ref(false)
const uploadFiles = ref([])
const uploadForm = reactive({ location_id: null, description: '', nickname: '' })
const locationOptions = ref([])
const commentNick = ref('')
const commentText = ref('')


function fmtTime(t) {
  if (!t) return ''
  return t.slice(0, 16).replace('T', ' ')
}

function onDateFilter(d) {
  fetchList()
}

async function fetchList() {
  loading.value = true
  try {
    const params = {}
    if (filterDate.value) {
      const d = new Date(typeof filterDate.value === 'number' ? filterDate.value : filterDate.value)
      params.date = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
    }
    const res = await getCommunity(params)
    items.value = res.items || []
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

function openDetail(item) {
  detailItem.value = item
  showDetail.value = true
}

async function doComment() {
  if (!commentText.value.trim() || !detailItem.value) return
  try {
    const res = await addComment(detailItem.value.id, commentNick.value, commentText.value.trim())
    commentText.value = ''
    // 用后端返回的评论列表更新
    detailItem.value.comments = res.comments || []
    const idx = items.value.findIndex(i => i.id === detailItem.value.id)
    if (idx >= 0) items.value[idx].comments = res.comments || []
  } catch (e) { message.error('评论失败') }
}

function onFilesChange({ fileList }) {
  uploadFiles.value = (fileList || []).map(f => f.file).filter(Boolean)
}

async function doUpload() {
  if (uploadFiles.value.length === 0) return
  uploading.value = true
  try {
    const fd = new FormData()
    // 多图上传
    for (const f of uploadFiles.value) {
      fd.append('images', f)
    }
    if (uploadForm.location_id) fd.append('location_id', String(uploadForm.location_id))
    if (uploadForm.description) fd.append('description', uploadForm.description)
    if (uploadForm.nickname) fd.append('nickname', uploadForm.nickname)
    fd.append('auto_detect', 'true')
    await uploadCommunity(fd)
    message.success('分享成功！')
    showUpload.value = false
    uploadFiles.value = []
    uploadForm.description = ''
    uploadForm.nickname = ''
    uploadForm.location_id = null
    fetchList()
  } catch (e) { message.error('上传失败') }
  finally { uploading.value = false }
}

onMounted(async () => {
  await fetchList()
  try { const r = await getPublicLocations(); locationOptions.value = (r.items||[]).map(l => ({ label: l.name, value: l.id })) } catch {}
})
</script>

<style scoped>
.community-page { min-height: 100vh; background: var(--color-cream-paper); }
.community-content { max-width: 1100px; margin: 0 auto; padding: 24px 20px 60px; }
.page-title { text-align: center; font-size: 28px; margin-bottom: 4px; color: var(--color-forest-ink); }
.page-subtitle { text-align: center; color: var(--color-whisper-gray); margin-bottom: 20px; }
.top-bar { display: flex; justify-content: center; gap: 16px; margin-bottom: 24px; align-items: center; }
.empty-state { margin-top: 80px; text-align: center; }
.empty-illustration { font-size: 64px; opacity: 0.5; margin-bottom: 16px; }
.empty-title { font-family: var(--font-body); font-size: 18px; font-weight: var(--weight-semibold); color: var(--color-forest-ink); margin: 0 0 8px; }
.empty-hint { font-family: var(--font-body); font-size: 14px; color: var(--color-whisper-gray); margin: 0; }
.community-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
.community-card { cursor: pointer; transition: transform var(--transition-fast); position: relative; }
.community-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-subtle-2); }
.cover-image { width: 100%; height: 300px; object-fit: cover; border-radius: var(--radius-image); display: block; border: 1px solid var(--color-pencil-gray); }
.photo-count { color: var(--color-forest-ink); font-size: 12px; font-weight: 600; margin-left: auto; }
.card-info { padding-top: 12px; }
.card-top-row { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 8px; }
.card-desc { font-size: 14px; color: var(--color-forest-ink); margin: 6px 0; }
.card-bottom { display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: var(--color-whisper-gray); }
.card-nickname { color: var(--color-forest-ink); font-weight: var(--weight-medium); }
.card-comments { color: var(--color-pencil-gray); }

.gallery { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
.gallery-img { width: 200px; height: 150px; object-fit: cover; border-radius: var(--radius-image); }
.detail-info p { color: var(--color-forest-ink); margin: 0 0 8px; }
.detail-meta { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; font-size: 13px; color: var(--color-whisper-gray); }

.comments-section h4 { margin: 0 0 12px; color: var(--color-forest-ink); }
.no-comments { color: var(--color-pencil-gray); font-size: 13px; text-align: center; padding: 20px; }
.comment-item { padding: 8px 0; border-bottom: 1px solid var(--color-pencil-gray); display: flex; flex-wrap: wrap; gap: 8px; align-items: baseline; }
.comment-nick { font-weight: 600; color: var(--color-forest-ink); font-size: 13px; }
.comment-text { font-size: 14px; color: var(--color-forest-ink); flex: 1; }
.comment-time { font-size: 11px; color: var(--color-pencil-gray); }
.comment-input { display: flex; gap: 8px; margin-top: 12px; align-items: center; }
.nick-input { width: 120px; flex-shrink: 0; }

.upload-preview { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.preview-chip { font-size: 12px; background: var(--surface-mint); color: var(--color-forest-ink); padding: 2px 8px; border-radius: var(--radius-sm); }
</style>
