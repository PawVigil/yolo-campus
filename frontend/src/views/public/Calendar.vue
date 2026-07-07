<template>
  <div class="calendar-page">
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

    <n-layout-content class="cal-content">
      <n-spin :show="loading">
        <!-- 月份切换 -->
        <div class="month-header">
          <n-button-group>
            <n-button @click="prevMonth" :disabled="loading">◀ 上月</n-button>
            <n-button @click="goToday">本月</n-button>
            <n-button @click="nextMonth" :disabled="loading">下月 ▶</n-button>
          </n-button-group>
          <h2 class="month-title">{{ currentMonth }}</h2>
        </div>

        <!-- 日历网格 -->
        <n-card :bordered="false" v-if="!loading">
          <div class="weekday-row">
            <div v-for="d in weekDays" :key="d" class="weekday-cell">{{ d }}</div>
          </div>
          <div class="cal-grid">
            <div
              v-for="(day, idx) in calendarDays"
              :key="idx"
              class="cal-cell"
              :class="{
                'is-today': day.isToday,
                'has-animals': day.hasAnimals,
                'is-other-month': !day.inMonth,
              }"
              @click="day.hasAnimals && day.inMonth && openDayDetail(day)"
            >
              <div class="day-num">{{ day.dayNum }}</div>
              <div v-if="day.hasAnimals && day.inMonth" class="day-breeds">
                <span v-for="breed in day.allBreeds.slice(0, 3)" :key="breed" class="breed-chip">{{ breed }}</span>
                <span v-if="day.allBreeds.length > 3" class="more-chip">+{{ day.allBreeds.length - 3 }}</span>
              </div>
            </div>
          </div>
        </n-card>
      </n-spin>

      <!-- 日详情弹窗 -->
      <n-modal v-model:show="showDetail" preset="card" :title="`📅 ${selectedDate} 检测详情`" style="max-width: 800px" :mask-closable="true">
        <n-spin :show="detailLoading">
          <n-empty v-if="!detailLoading && detailItems.length === 0" description="当天暂无检测记录" />
          <div v-else class="detail-list">
            <n-card v-for="item in detailItems" :key="item.id" :bordered="false" size="small" class="detail-card">
              <n-grid :cols="2" :x-gap="12">
                <n-grid-item>
                  <n-image :src="item.image_url" object-fit="contain" height="150" />
                </n-grid-item>
                <n-grid-item>
                  <n-image :src="item.annotated_url" object-fit="contain" height="150" />
                </n-grid-item>
              </n-grid>
              <div class="detail-info">
                <LocationBadge :name="item.location_name" />
                <span class="detail-time">{{ item.detect_time }}</span>
                <span class="detail-count">{{ item.total_animals }} 只动物</span>
              </div>
              <div class="detail-breeds">
                <n-tag v-for="a in item.animals" :key="a.breed_cn" size="small" round>{{ a.breed_cn }} {{ (a.confidence * 100).toFixed(0) }}%</n-tag>
              </div>
            </n-card>
          </div>
        </n-spin>
      </n-modal>
    </n-layout-content>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import LocationBadge from '@/components/LocationBadge.vue'
import { getCalendar, getPublicDetections } from '@/api/public.js'

const router = useRouter()
const activeMenu = ref('calendar')
const loading = ref(true)
const showDetail = ref(false)
const detailLoading = ref(false)
const detailItems = ref([])
const selectedDate = ref('')
const calendarData = ref(null)

const weekDays = ['日', '一', '二', '三', '四', '五', '六']
const now = new Date()
let viewYear = now.getFullYear()
let viewMonth = now.getMonth() + 1

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

const currentMonth = computed(() => `${viewYear}年${viewMonth}月`)

const calendarDays = computed(() => {
  const firstDay = new Date(viewYear, viewMonth - 1, 1)
  const lastDay = new Date(viewYear, viewMonth, 0)
  const daysInMonth = lastDay.getDate()
  const startWeekDay = firstDay.getDay()
  const today = new Date()
  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`

  // 上月补位
  const prevLastDay = new Date(viewYear, viewMonth - 1, 0)
  const days = []
  for (let i = startWeekDay - 1; i >= 0; i--) {
    const d = prevLastDay.getDate() - i
    const m = viewMonth === 1 ? 12 : viewMonth - 1
    const y = viewMonth === 1 ? viewYear - 1 : viewYear
    days.push({
      dayNum: d,
      date: `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`,
      inMonth: false,
      hasAnimals: false,
      allBreeds: [],
      isToday: false,
    })
  }

  // 当月
  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${viewYear}-${String(viewMonth).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    const dayData = calendarData.value?.days?.find((x) => x.date === dateStr)
    const allBreeds = []
    if (dayData?.locations) {
      dayData.locations.forEach((loc) => loc.breeds?.forEach((b) => allBreeds.push(b)))
    }
    const uniqueBreeds = [...new Set(allBreeds)]
    days.push({
      dayNum: d,
      date: dateStr,
      inMonth: true,
      hasAnimals: dayData?.has_animals || false,
      allBreeds: uniqueBreeds,
      isToday: dateStr === todayStr,
    })
  }

  // 下月补位
  const remaining = 42 - days.length
  for (let d = 1; d <= remaining; d++) {
    const m = viewMonth === 12 ? 1 : viewMonth + 1
    const y = viewMonth === 12 ? viewYear + 1 : viewYear
    days.push({
      dayNum: d,
      date: `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`,
      inMonth: false,
      hasAnimals: false,
      allBreeds: [],
      isToday: false,
    })
  }

  return days
})

async function fetchCalendar() {
  loading.value = true
  try {
    const month = `${viewYear}-${String(viewMonth).padStart(2, '0')}`
    calendarData.value = await getCalendar(month)
  } catch (e) {
    console.error('获取日历数据失败', e)
  } finally {
    loading.value = false
  }
}

function prevMonth() {
  if (viewMonth === 1) { viewMonth = 12; viewYear-- } else { viewMonth-- }
  fetchCalendar()
}

function nextMonth() {
  if (viewMonth === 12) { viewMonth = 1; viewYear++ } else { viewMonth++ }
  fetchCalendar()
}

function goToday() {
  viewYear = new Date().getFullYear()
  viewMonth = new Date().getMonth() + 1
  fetchCalendar()
}

async function openDayDetail(day) {
  selectedDate.value = day.date
  showDetail.value = true
  detailLoading.value = true
  try {
    const res = await getPublicDetections(day.date)
    detailItems.value = res.items || []
  } catch (e) {
    console.error('获取日期详情失败', e)
    detailItems.value = []
  } finally {
    detailLoading.value = false
  }
}

onMounted(() => {
  fetchCalendar()
})
</script>

<style scoped>
.calendar-page { min-height: 100vh; background: #f5f7fa; }
.public-nav { background: rgba(255,255,255,0.9); backdrop-filter: blur(10px); position: sticky; top: 0; z-index: 100; }
.nav-content { max-width: 1200px; margin: 0 auto; display: flex; align-items: center; padding: 0 20px; height: 56px; }
.nav-brand { display: flex; align-items: center; gap: 8px; cursor: pointer; margin-right: 24px; }
.brand-icon { font-size: 24px; }
.brand-text { font-size: 18px; font-weight: 700; color: #7c5ce7; }
.admin-link { margin-left: auto; }
.cal-content { max-width: 1000px; margin: 0 auto; padding: 24px 20px; }
.month-header { display: flex; align-items: center; gap: 20px; margin-bottom: 24px; }
.month-title { margin: 0; font-size: 22px; }
.weekday-row { display: grid; grid-template-columns: repeat(7, 1fr); text-align: center; font-weight: 600; color: #909399; margin-bottom: 8px; }
.cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; }
.cal-cell { min-height: 80px; padding: 8px; background: #fff; border-radius: 8px; cursor: default; transition: all 0.2s; }
.cal-cell.has-animals { cursor: pointer; }
.cal-cell.has-animals:hover { background: #f0ebff; transform: scale(1.02); }
.cal-cell.is-today { border: 2px solid #7c5ce7; }
.cal-cell.is-other-month { opacity: 0.3; }
.day-num { font-weight: 600; font-size: 14px; margin-bottom: 4px; }
.day-breeds { display: flex; flex-wrap: wrap; gap: 2px; }
.breed-chip { font-size: 11px; background: #f0ebff; color: #7c5ce7; padding: 1px 4px; border-radius: 3px; }
.more-chip { font-size: 11px; color: #909399; }
.detail-list { max-height: 500px; overflow-y: auto; }
.detail-card { margin-bottom: 12px; }
.detail-info { display: flex; align-items: center; gap: 12px; margin-top: 8px; }
.detail-time { font-size: 13px; color: #909399; }
.detail-count { font-size: 13px; font-weight: 600; }
.detail-breeds { display: flex; gap: 4px; flex-wrap: wrap; margin-top: 6px; }
</style>
