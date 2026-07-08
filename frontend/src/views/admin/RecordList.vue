<template>
  <div class="records-page">
    <h2 class="page-title">📋 检测记录管理</h2>

    <!-- 筛选条件 -->
    <n-card :bordered="false" class="filter-card">
      <n-grid :cols="5" :x-gap="12" :y-gap="12" responsive="screen">
        <n-grid-item>
          <n-select v-model:value="filters.location_id" :options="locationOptions" placeholder="选择地点" clearable />
        </n-grid-item>
        <n-grid-item>
          <n-input v-model:value="filters.breed" placeholder="品种名称" clearable />
        </n-grid-item>
        <n-grid-item>
          <n-date-picker v-model:value="filters.date_from" type="date" placeholder="开始日期" clearable />
        </n-grid-item>
        <n-grid-item>
          <n-date-picker v-model:value="filters.date_to" type="date" placeholder="结束日期" clearable />
        </n-grid-item>
        <n-grid-item>
          <n-button type="primary" @click="doSearch">🔍 搜索</n-button>
          <n-button @click="resetFilters" class="ml-8">重置</n-button>
        </n-grid-item>
      </n-grid>
    </n-card>

    <!-- 数据表格 -->
    <n-card :bordered="false" class="table-card">
      <n-spin :show="loading">
        <n-empty v-if="!loading && items.length === 0" description="暂无检测记录" />

        <n-table v-else :single-line="false" :bordered="false" size="small">
          <thead>
            <tr>
              <th style="width:60px">ID</th>
              <th style="width:80px">地点</th>
              <th style="min-width:100px">品种摘要</th>
              <th style="width:80px">数量</th>
              <th style="width:160px">检测时间</th>
              <th style="width:100px">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.id" class="table-row">
              <td>{{ item.id }}</td>
              <td><LocationBadge :name="item.location_name" /></td>
              <td>
                <n-tag v-for="b in parseBreeds(item.breed_summary)" :key="b" size="tiny" round class="breed-tag">{{ b }}</n-tag>
              </td>
              <td>{{ item.total_animals }}</td>
              <td class="time-cell">{{ item.detect_time }}</td>
              <td>
                <n-button-group>
                  <n-button size="tiny" type="info" @click="openDetail(item.id)">详情</n-button>
                  <n-button size="tiny" type="error" @click="doDelete(item.id)">删除</n-button>
                </n-button-group>
              </td>
            </tr>
          </tbody>
        </n-table>

        <!-- 分页 -->
        <div class="pagination-row">
          <n-pagination
            v-model:page="page"
            :page-size="pageSize"
            :item-count="total"
            :page-sizes="[10, 15, 20, 50]"
            show-size-picker
            @update:page="fetchRecords"
            @update:page-size="onPageSizeChange"
          />
        </div>
      </n-spin>
    </n-card>

    <!-- 详情弹窗 -->
    <n-modal v-model:show="showDetail" preset="card" title="📋 检测记录详情" style="max-width: 900px" :mask-closable="true">
      <n-spin :show="detailLoading">
        <template v-if="!detailLoading && detailData">
          <DetectionResult
            :image-url="detailData.image_url"
            :annotated-url="detailData.annotated_url"
            :animals="detailData.animals || []"
          />
          <n-divider />
          <div class="detail-meta">
            <LocationBadge :name="detailData.location_name" />
            <n-tag type="info" round>检测时间：{{ detailData.detect_time }}</n-tag>
            <n-tag type="success" round>总计 {{ detailData.total_animals }} 只</n-tag>
            <n-tag round>记录编号：#{{ detailData.id }}</n-tag>
          </div>
          <n-divider />
          <n-text depth="3">完整 JSON：</n-text>
          <n-code :code="JSON.stringify(detailData.animals || [], null, 2)" language="json" word-wrap />
        </template>
      </n-spin>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import LocationBadge from '@/components/LocationBadge.vue'
import DetectionResult from '@/components/DetectionResult.vue'
import { getDetections, getDetectionById, deleteDetection, getLocations } from '@/api/admin.js'

const message = useMessage()
const loading = ref(false)
const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(15)
const showDetail = ref(false)
const detailLoading = ref(false)
const detailData = ref(null)
const locationOptions = ref([])

const filters = reactive({
  location_id: null,
  breed: '',
  date_from: null,
  date_to: null,
})

function formatDate(d) {
  if (!d) return null
  if (typeof d === 'number') {
    const dt = new Date(d)
    return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')}`
  }
  return d
}

async function fetchRecords() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (filters.location_id) params.location_id = filters.location_id
    if (filters.breed) params.breed = filters.breed
    if (filters.date_from) params.date_from = formatDate(filters.date_from)
    if (filters.date_to) params.date_to = formatDate(filters.date_to)

    const res = await getDetections(params)
    items.value = res.items || []
    total.value = res.total || 0
  } catch (e) {
    console.error('获取记录失败', e)
    message.error('获取检测记录失败')
  } finally {
    loading.value = false
  }
}

function doSearch() {
  page.value = 1
  fetchRecords()
}

function resetFilters() {
  filters.location_id = null
  filters.breed = ''
  filters.date_from = null
  filters.date_to = null
  page.value = 1
  fetchRecords()
}

function onPageSizeChange(size) {
  pageSize.value = size
  page.value = 1
  fetchRecords()
}

async function openDetail(id) {
  showDetail.value = true
  detailLoading.value = true
  detailData.value = null
  try {
    detailData.value = await getDetectionById(id)
  } catch (e) {
    console.error('获取详情失败', e)
    message.error('获取记录详情失败')
  } finally {
    detailLoading.value = false
  }
}

async function doDelete(id) {
  if (!window.confirm(`确定要删除检测记录 #${id} 吗？此操作不可恢复。`)) return
  try {
    await deleteDetection(id)
    message.success('删除成功')
    fetchRecords()
  } catch (e) {
    console.error('删除失败', e)
    message.error('删除失败')
  }
}

function parseBreeds(summary) {
  if (!summary) return []
  return summary.split(',').map((s) => s.trim()).filter(Boolean)
}

onMounted(async () => {
  await fetchRecords()
  try {
    const res = await getLocations()
    locationOptions.value = (res.items || []).map((l) => ({ label: l.name, value: l.id }))
  } catch { /* ignore */ }
})
</script>

<style scoped>
.records-page { max-width: 1200px; }
.page-title { margin-bottom: 20px; font-size: 22px; }
.filter-card { margin-bottom: 16px; }
.ml-8 { margin-left: 8px; }
.table-card { margin-bottom: 16px; }
.table-row { cursor: pointer; }
.table-row:hover { background: #f8f7ff; }
.breed-tag { margin: 1px; }
.time-cell { font-size: 13px; font-family: monospace; color: #666; }
.pagination-row { display: flex; justify-content: center; margin-top: 16px; }
.detail-meta { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
</style>
