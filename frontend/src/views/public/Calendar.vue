<template>
  <div class="calendar-page">
    <PublicNav menu-key="calendar" />

    <n-layout-content class="cal-content">
      <div class="month-header">
        <n-button-group>
          <n-button @click="prevMonth">◀ 上月</n-button>
          <n-button @click="goToday">本月</n-button>
          <n-button @click="nextMonth">下月 ▶</n-button>
        </n-button-group>
        <h2 class="month-title">{{ viewYear }}年{{ viewMonth }}月</h2>
      </div>

      <div class="notebook-card">
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
              'is-future': day.isFuture,
              'is-dimmed': !day.inMonth,
            }"
            @click="day.hasAnimals && !day.isFuture && openDetail(day)"
          >
            <div class="day-num">{{ day.dayNum }}</div>
            <div v-if="day.hasAnimals && !day.isFuture" class="day-stamps">
              <span v-if="day.hasCat" class="stamp stamp-cat" title="有猫">●</span>
              <span v-if="day.hasDog" class="stamp stamp-dog" title="有狗">●</span>
            </div>
          </div>
        </div>
      </div>
    </n-layout-content>

    <!-- 日详情弹窗 -->
    <n-modal v-model:show="showDetail" preset="card" :title="selectedDate" style="max-width: 560px" :mask-closable="true">
      <n-spin :show="detailLoading">
        <n-empty v-if="!detailLoading && detailLocations.length === 0" description="这天还没有检测记录 — 不妨去食堂或花园附近看看" :show-icon="false" />
        <div v-else class="detail-list">
          <PaperCard v-for="loc in detailLocations" :key="loc.name" stripe="ink" padding="sm" class="detail-card">
            <div class="detail-loc">
              <span class="loc-emoji">{{ loc.emoji }}</span>
              <strong>{{ loc.name }}</strong>
            </div>
            <div class="detail-breeds">
              <n-tag v-for="b in loc.breeds" :key="b" size="small" round>{{ b }}</n-tag>
            </div>
          </PaperCard>
        </div>
      </n-spin>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PublicNav from '@/components/PublicNav.vue'
import PaperCard from '@/components/PaperCard.vue'
import { getCalendar, getPublicDetections } from '@/api/public.js'

const router = useRouter()
const weekDays = ['日', '一', '二', '三', '四', '五', '六']

const now = new Date()
const viewYear = ref(now.getFullYear())
const viewMonth = ref(now.getMonth() + 1)
const calendarData = ref({ days: [] })
const showDetail = ref(false)
const detailLoading = ref(false)
const detailLocations = ref([])
const selectedDate = ref('')


const locEmojis = { '食堂': '🍽️', '宿舍': '🏠', '图书馆': '📚', '操场': '🏟️', '花园': '🌳' }

const calendarDays = computed(() => {
  const firstDay = new Date(viewYear.value, viewMonth.value - 1, 1)
  const lastDay = new Date(viewYear.value, viewMonth.value, 0)
  const daysInMonth = lastDay.getDate()
  const startWeekDay = firstDay.getDay()
  const today = new Date()
  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`

  const days = []
  // 上月补位
  const prevLastDay = new Date(viewYear.value, viewMonth.value - 1, 0)
  for (let i = startWeekDay - 1; i >= 0; i--) {
    const d = prevLastDay.getDate() - i
    const m = viewMonth.value === 1 ? 12 : viewMonth.value - 1
    const y = viewMonth.value === 1 ? viewYear.value - 1 : viewYear.value
    days.push({ dayNum: d, date: `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`, inMonth: false, hasAnimals: false, hasCat: false, hasDog: false, isToday: false, isFuture: false })
  }
  // 当月
  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${viewYear.value}-${String(viewMonth.value).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    const dayData = calendarData.value.days?.find(x => x.date === dateStr)
    const allBreeds = []
    if (dayData?.locations) dayData.locations.forEach(loc => loc.breeds?.forEach(b => allBreeds.push(b)))
    const uniqueBreeds = [...new Set(allBreeds)]
    const hasCat = uniqueBreeds.some(b => b.includes('猫'))
    const hasDog = uniqueBreeds.some(b => !b.includes('猫')) // 非猫即狗
    days.push({
      dayNum: d, date: dateStr, inMonth: true,
      hasAnimals: dayData?.has_animals || false,
      hasCat, hasDog,
      isToday: dateStr === todayStr,
      isFuture: dateStr > todayStr,
    })
  }
  // 下月补位
  const remaining = 42 - days.length
  for (let d = 1; d <= remaining; d++) {
    const m = viewMonth.value === 12 ? 1 : viewMonth.value + 1
    const y = viewMonth.value === 12 ? viewYear.value + 1 : viewYear.value
    const dateStr = `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    days.push({ dayNum: d, date: dateStr, inMonth: false, hasAnimals: false, hasCat: false, hasDog: false, isToday: false, isFuture: true })
  }
  return days
})

async function fetchCalendar() {
  try {
    const m = `${viewYear.value}-${String(viewMonth.value).padStart(2, '0')}`
    calendarData.value = await getCalendar(m)
  } catch (e) {
    console.error('获取日历失败', e)
  }
}

function prevMonth() {
  if (viewMonth.value === 1) { viewMonth.value = 12; viewYear.value-- }
  else { viewMonth.value-- }
  fetchCalendar()
}
function nextMonth() {
  if (viewMonth.value === 12) { viewMonth.value = 1; viewYear.value++ }
  else { viewMonth.value++ }
  fetchCalendar()
}
function goToday() {
  viewYear.value = new Date().getFullYear()
  viewMonth.value = new Date().getMonth() + 1
  fetchCalendar()
}

async function openDetail(day) {
  selectedDate.value = day.date
  showDetail.value = true
  detailLoading.value = true
  try {
    const res = await getPublicDetections(day.date)
    // 按地点聚合，只保留有动物的
    const locMap = {}
    ;(res.items || []).forEach(item => {
      if (!item.total_animals || item.total_animals === 0) return
      if (!locMap[item.location_name]) locMap[item.location_name] = { name: item.location_name, emoji: locEmojis[item.location_name] || '📍', breeds: new Set() }
      ;(item.animals || []).forEach(a => locMap[item.location_name].breeds.add(a.breed_cn))
    })
    detailLocations.value = Object.values(locMap).map(l => ({ ...l, breeds: [...l.breeds] }))
  } catch (e) {
    console.error('获取详情失败', e)
  } finally {
    detailLoading.value = false
  }
}

onMounted(() => fetchCalendar())
</script>

<style scoped>
.calendar-page { min-height: 100vh; background: var(--color-cream-paper); }
.cal-content { max-width: 1000px; margin: 0 auto; padding: 24px 20px 60px; }
.month-header { display: flex; align-items: center; gap: 20px; margin-bottom: 24px; }
.month-title { margin: 0; font-size: 22px; color: var(--color-forest-ink); }

/* ================================
   Notebook Card — field journal
   ================================ */
.notebook-card {
  background-color: #fdfcfa;
  background-image:
    /* horizontal ruled lines */
    repeating-linear-gradient(
      0deg,
      transparent,
      transparent 39px,
      rgba(182, 182, 182, 0.18) 39px,
      rgba(182, 182, 182, 0.18) 40px
    ),
    /* left margin line (red, faint) */
    linear-gradient(90deg, rgba(200, 80, 60, 0.12) 0px, rgba(200, 80, 60, 0.12) 1px, transparent 1px);
  border: 1px solid var(--color-pencil-gray);
  border-radius: 2px;
  padding: 28px 28px 28px 36px;
  box-shadow:
    2px 2px 0 rgba(0,0,0,0.04),
    0 1px 4px rgba(0,0,0,0.06);
}

.weekday-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  font-weight: var(--weight-semibold);
  font-size: 13px;
  color: var(--color-whisper-gray);
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.cal-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
}

.cal-cell {
  min-height: 78px;
  padding: 6px 6px 8px;
  cursor: default;
  transition: all var(--transition-fast);
  position: relative;
  border-radius: 2px;
}

.cal-cell.has-animals { cursor: pointer; }
.cal-cell.has-animals:hover { background: rgba(26, 51, 0, 0.04); }

.cal-cell.is-dimmed .day-num { color: var(--color-whisper-gray); }

/* Today — highlighter yellow swipe */
.cal-cell.is-today {
  background: var(--color-highlighter-yellow);
  box-shadow: inset 0 0 0 1px rgba(26,51,0,0.1);
}
.cal-cell.is-today .day-num {
  font-weight: var(--weight-extrabold);
  font-size: 16px;
}

.cal-cell.is-future { opacity: 0.35; pointer-events: none; }

.day-num {
  font-family: var(--font-mono);
  font-weight: var(--weight-medium);
  font-size: 13px;
  color: var(--color-forest-ink);
  margin-bottom: 2px;
  font-feature-settings: 'tnum';
}

/* Ink stamps — circular, slightly irregular */
.day-stamps {
  display: flex;
  justify-content: center;
  gap: 5px;
  margin-top: 4px;
}
.stamp {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  font-size: 10px;
  line-height: 1;
  opacity: 0.82;
  transform: rotate(-5deg);
  box-shadow: inset 0 0 2px rgba(0,0,0,0.15);
}
.stamp-cat {
  background: rgba(26, 51, 0, 0.12);
  color: var(--color-forest-ink);
}
.stamp-dog {
  background: rgba(232, 153, 112, 0.2);
  color: var(--color-terracotta);
}
.cal-cell:nth-child(7n+2) .stamp { transform: rotate(3deg); }
.cal-cell:nth-child(7n+5) .stamp { transform: rotate(-7deg); }
.cal-cell:nth-child(3n+1) .stamp { transform: rotate(6deg); }

/* Detail modal */
.detail-list { max-height: 400px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
.detail-card { margin-bottom: 2px; }
.detail-loc { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.loc-emoji { font-size: 20px; }
.detail-breeds { display: flex; gap: 4px; flex-wrap: wrap; }
</style>
