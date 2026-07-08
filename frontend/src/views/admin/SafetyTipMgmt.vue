<template>
  <div class="safety-page">
    <h2 class="page-title">⚠️ 安全提醒管理</h2>

    <!-- 自动建议面板 -->
    <n-card :bordered="false" title="🤖 AI 自动建议" class="suggestion-card">
      <n-spin :show="suggestionLoading">
        <n-empty v-if="!suggestionLoading && suggestions.length === 0" description="暂无需要生成建议的地点（各地点近7天检测量均不足）" />

        <div v-else class="suggestion-list">
          <n-alert
            v-for="s in suggestions"
            :key="s.location_id"
            :type="suggestionType(s.count)"
            class="suggestion-item"
          >
            <div class="suggestion-row">
              <div class="suggestion-body">
                <div class="suggestion-header">
                  <LocationBadge :name="s.location_name" />
                  <span class="suggestion-text">{{ s.suggestion_text }}</span>
                  <span class="suggestion-basis">（{{ s.data_basis }}）</span>
                </div>
                <p class="suggestion-content">{{ s.suggestion_content }}</p>
              </div>
              <n-button size="small" type="primary" @click="adoptSuggestion(s)" class="adopt-btn">采纳建议</n-button>
            </div>
          </n-alert>
        </div>
      </n-spin>
    </n-card>

    <!-- 新建/编辑表单 -->
    <n-card :bordered="false" title="✏️ 手动管理提醒" class="form-card">
      <n-form :model="editForm" label-placement="top">
        <n-grid :cols="2" :x-gap="12" responsive="screen">
          <n-grid-item>
            <n-form-item label="地点" required>
              <n-select v-model:value="editForm.location_id" :options="locationOptions" placeholder="选择地点" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="状态">
              <n-select v-model:value="editForm.status" :options="statusOptions" />
            </n-form-item>
          </n-grid-item>
        </n-grid>
        <n-form-item label="标题" required>
          <n-input v-model:value="editForm.title" placeholder="提醒标题" />
        </n-form-item>
        <n-form-item label="正文" required>
          <n-input v-model:value="editForm.content" type="textarea" :rows="4" placeholder="提醒正文内容..." />
        </n-form-item>
      </n-form>
      <div class="form-actions">
        <n-button v-if="editingId" @click="resetForm">取消编辑</n-button>
        <n-button type="primary" @click="doSave">
          {{ editingId ? '更新提醒' : '新建提醒' }}
        </n-button>
      </div>
    </n-card>

    <!-- 提醒列表 -->
    <n-card :bordered="false" title="📋 提醒列表" class="list-card">
      <n-spin :show="listLoading">
        <n-empty v-if="!listLoading && tips.length === 0" description="暂无提醒" />

        <n-table v-else :single-line="false" :bordered="false" size="small">
          <thead>
            <tr>
              <th style="width:80px">地点</th>
              <th style="min-width:120px">标题</th>
              <th style="width:100px">状态</th>
              <th style="width:140px">创建时间</th>
              <th style="width:160px">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="tip in tips" :key="tip.id">
              <td><LocationBadge :name="tip.location_name" /></td>
              <td class="title-cell">{{ tip.title }}</td>
              <td><n-tag :type="statusTagType(tip.status)" round size="small">{{ statusLabel(tip.status) }}</n-tag></td>
              <td class="time-cell">{{ tip.created_at?.slice(0, 10) }}</td>
              <td>
                <n-button-group>
                  <n-button v-if="tip.status === 'draft'" size="tiny" type="success" @click="doPublish(tip.id)">发布</n-button>
                  <n-button v-if="tip.status === 'published'" size="tiny" type="warning" @click="doArchive(tip.id)">下架</n-button>
                  <n-button size="tiny" type="info" @click="startEdit(tip)">编辑</n-button>
                  <n-button v-if="tip.status !== 'published'" size="tiny" type="error" @click="doDelete(tip.id)">删除</n-button>
                </n-button-group>
              </td>
            </tr>
          </tbody>
        </n-table>
      </n-spin>
    </n-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import LocationBadge from '@/components/LocationBadge.vue'
import { getSafetyTips, createSafetyTip, updateSafetyTip, updateSafetyTipStatus, deleteSafetyTip, getSuggestions, getLocations } from '@/api/admin.js'

const message = useMessage()
const suggestionLoading = ref(false)
const listLoading = ref(false)
const suggestions = ref([])
const tips = ref([])
const editingId = ref(null)
const locationOptions = ref([])

const defaultForm = { location_id: null, title: '', content: '', status: 'draft' }
const editForm = reactive({ ...defaultForm })

const statusOptions = [
  { label: '📝 草稿', value: 'draft' },
  { label: '✅ 已发布', value: 'published' },
  { label: '📦 已下架', value: 'archived' },
]

function suggestionType(count) {
  if (count >= 20) return 'error'
  if (count >= 10) return 'warning'
  return 'info'
}

function statusTagType(status) {
  if (status === 'published') return 'success'
  if (status === 'draft') return 'warning'
  return 'default'
}

function statusLabel(status) {
  if (status === 'published') return '✅ 已发布'
  if (status === 'draft') return '📝 草稿'
  return '📦 已下架'
}

async function fetchSuggestions() {
  suggestionLoading.value = true
  try {
    const res = await getSuggestions()
    suggestions.value = res.suggestions || []
  } catch (e) {
    console.error('获取建议失败', e)
  } finally {
    suggestionLoading.value = false
  }
}

async function fetchTips() {
  listLoading.value = true
  try {
    const res = await getSafetyTips()
    tips.value = res.items || []
  } catch (e) {
    console.error('获取提醒列表失败', e)
  } finally {
    listLoading.value = false
  }
}

function adoptSuggestion(s) {
  editingId.value = null
  editForm.location_id = s.location_id
  editForm.title = s.suggestion_text
  editForm.content = s.suggestion_content || `${s.location_name}区域${s.suggestion_text}。${s.data_basis}。`
  editForm.status = 'draft'
}

async function doSave() {
  if (!editForm.location_id || !editForm.title || !editForm.content) {
    message.warning('请填写完整信息')
    return
  }
  try {
    if (editingId.value) {
      await updateSafetyTip(editingId.value, {
        title: editForm.title,
        content: editForm.content,
        status: editForm.status,
        location_id: editForm.location_id,
      })
      message.success('更新成功')
    } else {
      await createSafetyTip({
        location_id: editForm.location_id,
        title: editForm.title,
        content: editForm.content,
        status: editForm.status,
      })
      message.success('创建成功')
    }
    resetForm()
    fetchTips()
    fetchSuggestions()
  } catch (e) {
    console.error('保存失败', e)
    message.error('保存失败')
  }
}

function startEdit(tip) {
  editingId.value = tip.id
  editForm.location_id = tip.location_id
  editForm.title = tip.title
  editForm.content = tip.content
  editForm.status = tip.status
}

function resetForm() {
  editingId.value = null
  Object.assign(editForm, defaultForm)
}

async function doPublish(id) {
  try {
    await updateSafetyTipStatus(id, 'published')
    message.success('已发布')
    fetchTips()
  } catch (e) {
    console.error('发布失败', e)
    message.error('发布失败')
  }
}

async function doArchive(id) {
  try {
    await updateSafetyTipStatus(id, 'archived')
    message.success('已下架')
    fetchTips()
  } catch (e) {
    console.error('下架失败', e)
    message.error('下架失败')
  }
}

async function doDelete(id) {
  if (!window.confirm('确定要删除该提醒吗？')) return
  try {
    await deleteSafetyTip(id)
    message.success('已删除')
    fetchTips()
  } catch (e) {
    console.error('删除失败', e)
    message.error('删除失败')
  }
}

onMounted(async () => {
  await Promise.all([fetchSuggestions(), fetchTips()])
  try {
    const res = await getLocations()
    locationOptions.value = (res.items || []).map((l) => ({ label: l.name, value: l.id }))
  } catch { /* ignore */ }
})
</script>

<style scoped>
.safety-page { max-width: 1100px; }
.page-title { margin-bottom: 20px; font-size: 22px; }
.suggestion-card { margin-bottom: 16px; }
.suggestion-list { display: flex; flex-direction: column; gap: 12px; }
.form-card { margin-bottom: 16px; }
.form-actions { display: flex; gap: 8px; margin-top: 12px; }
.list-card { margin-bottom: 16px; }
.title-cell { font-weight: 500; }
.time-cell { font-size: 13px; color: #666; }
.suggestion-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; }
.suggestion-body { flex: 1; }
.suggestion-header { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 6px; }
.suggestion-text { font-weight: 600; font-size: 15px; }
.suggestion-basis { font-size: 12px; color: #999; }
.suggestion-content { font-size: 14px; color: #555; line-height: 1.6; margin: 0; }
.adopt-btn { flex-shrink: 0; margin-top: 2px; }
</style>
