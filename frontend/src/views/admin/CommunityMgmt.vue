<template>
  <div class="community-mgmt-page">
    <h2 class="page-title">📸 社区分享管理</h2>
    <p class="page-subtitle">管理所有用户的社区分享内容</p>

      <!-- 日期筛选 + 上传 -->
      <div class="top-bar">
        <n-date-picker v-model:value="filterDate" type="date" placeholder="选择日期筛选" clearable @update:value="onDateFilter" />
        <n-button type="primary" @click="showUpload = true">📤 上传分享</n-button>
      </div>

      <!-- 分享卡片列表 -->
      <n-spin :show="loading">
        <n-empty v-if="!loading && items.length === 0" description="今天还没有人分享" class="empty-state" />
        <div v-else class="community-grid">
          <n-card v-for="item in items" :key="item.id" :bordered="false" class="community-card" @click="openDetail(item)">
            <n-button text class="delete-share-btn" @click.stop="doDeleteShare(item.id)" title="删除此分享">
              <span style="color: #d03050; font-size: 18px;">🗑️</span>
            </n-button>
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
            <n-button text class="delete-comment-btn" @click="doDeleteComment(c.id)" title="删除此评论">
              <span style="color: #d03050;">🗑️</span>
            </n-button>
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
    <n-modal v-model:show="showUpload" preset="card" :title="shareImage ? '📸 从检测记录分享' : '📤 分享你的发现'" style="max-width: 560px" :mask-closable="true" @update:show="(v) => { if (!v) { shareImage = ''; shareLocation = ''; uploadFiles.value = []; } }">
      <n-form label-placement="top">
        <n-form-item v-if="!shareImage" label="选择照片（可多张）">
          <n-upload multiple accept="image/jpeg,image/png" :max="9" @change="onFilesChange">
            <n-button>选择照片（JPG/PNG）</n-button>
          </n-upload>
          <div v-if="uploadFiles.length > 0" class="upload-preview">
            <span v-for="(f, i) in uploadFiles" :key="i" class="preview-chip">{{ f.name }}</span>
          </div>
        </n-form-item>
        <n-form-item v-else label="检测图片">
          <img :src="shareImage" style="max-width: 100%; max-height: 200px; border-radius: 8px;" />
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
        <n-button type="primary" @click="doUpload" :loading="uploading" :disabled="!shareImage && uploadFiles.length === 0">
          {{ uploading ? '分享中...' : '确认分享' }}
        </n-button>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMessage } from 'naive-ui'
import LocationBadge from '@/components/LocationBadge.vue'
import { getCommunity, uploadCommunity, addComment, deleteCommunity, deleteComment, shareFromDetection, getPublicLocations } from '@/api/public.js'

const router = useRouter()
const route = useRoute()
const message = useMessage()
const shareImage = ref('')
const shareLocation = ref('')
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
    detailItem.value.comments = res.comments || []
    const idx = items.value.findIndex(i => i.id === detailItem.value.id)
    if (idx >= 0) items.value[idx].comments = res.comments || []
  } catch (e) { message.error('评论失败') }
}

async function doDeleteShare(id) {
  if (!window.confirm('确定要删除这条分享吗？所有评论也会被删除。')) return
  try {
    await deleteCommunity(id)
    message.success('分享已删除')
    items.value = items.value.filter(i => i.id !== id)
    if (detailItem.value?.id === id) showDetail.value = false
  } catch (e) { message.error('删除失败') }
}

async function doDeleteComment(commentId) {
  if (!window.confirm('确定要删除这条评论吗？')) return
  try {
    const res = await deleteComment(detailItem.value.id, commentId)
    detailItem.value.comments = res.comments || []
    const idx = items.value.findIndex(i => i.id === detailItem.value.id)
    if (idx >= 0) items.value[idx].comments = res.comments || []
    message.success('评论已删除')
  } catch (e) { message.error('删除失败') }
}

function onFilesChange({ fileList }) {
  uploadFiles.value = (fileList || []).map(f => f.file).filter(Boolean)
}

async function doUpload() {
  // 来自检测记录的分享（无需上传文件）
  if (shareImage.value) {
    uploading.value = true
    try {
      await shareFromDetection({
        image_url: shareImage.value,
        location_id: uploadForm.location_id || null,
        description: uploadForm.description || null,
        nickname: uploadForm.nickname || null,
        auto_detect: true,
      })
      message.success('分享成功！')
      showUpload.value = false
      shareImage.value = ''
      shareLocation.value = ''
      uploadForm.description = ''
      uploadForm.nickname = ''
      uploadForm.location_id = null
      fetchList()
    } catch (e) { message.error('分享失败') }
    finally { uploading.value = false }
    return
  }

  // 正常多图上传
  if (uploadFiles.value.length === 0) return
  uploading.value = true
  try {
    const fd = new FormData()
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
  // 检查是否从检测记录跳转过来
  if (route.query.share_image) {
    shareImage.value = decodeURIComponent(route.query.share_image)
    shareLocation.value = route.query.share_location || ''
    uploadForm.location_id = shareLocation.value ? parseInt(shareLocation.value) : null
    showUpload.value = true
  }
  await fetchList()
  try { const r = await getPublicLocations(); locationOptions.value = (r.items||[]).map(l => ({ label: l.name, value: l.id })) } catch {}
})
</script>

<style scoped>
.community-mgmt-page { max-width: 1100px; }
.page-title { text-align: center; font-size: 28px; margin-bottom: 4px; }
.page-subtitle { text-align: center; color: #909399; margin-bottom: 20px; }
.top-bar { display: flex; justify-content: center; gap: 16px; margin-bottom: 24px; align-items: center; }
.empty-state { margin-top: 80px; }
.community-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
.community-card { cursor: pointer; transition: all 0.3s; position: relative; }
.community-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.1); }
.delete-share-btn { position: absolute; top: 8px; right: 8px; z-index: 10; opacity: 0.6; }
.delete-share-btn:hover { opacity: 1; }
.cover-image { width: 100%; height: 300px; object-fit: cover; border-radius: 8px; display: block; }
.photo-count { color: #7c5ce7; font-size: 12px; font-weight: 600; margin-left: auto; }
.card-info { padding-top: 12px; }
.card-top-row { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 8px; }
.card-desc { font-size: 14px; color: #555; margin: 6px 0; }
.card-bottom { display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #999; }
.card-nickname { color: #7c5ce7; }
.card-comments { color: #aaa; }

.gallery { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
.gallery-img { width: 200px; height: 150px; object-fit: cover; border-radius: 8px; }
.detail-info p { color: #555; margin: 0 0 8px; }
.detail-meta { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; font-size: 13px; color: #999; }

.comments-section h4 { margin: 0 0 12px; }
.no-comments { color: #ccc; font-size: 13px; text-align: center; padding: 20px; }
.comment-item { padding: 8px 0; border-bottom: 1px solid #f0f0f0; display: flex; flex-wrap: wrap; gap: 8px; align-items: baseline; }
.comment-nick { font-weight: 600; color: #7c5ce7; font-size: 13px; }
.comment-text { font-size: 14px; color: #333; flex: 1; }
.comment-time { font-size: 11px; color: #ccc; }
.delete-comment-btn { margin-left: auto; flex-shrink: 0; opacity: 0.5; }
.delete-comment-btn:hover { opacity: 1; }
.comment-input { display: flex; gap: 8px; margin-top: 12px; align-items: center; }
.nick-input { width: 120px; flex-shrink: 0; }

.upload-preview { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.preview-chip { font-size: 12px; background: #f0ebff; color: #7c5ce7; padding: 2px 8px; border-radius: 4px; }
</style>
