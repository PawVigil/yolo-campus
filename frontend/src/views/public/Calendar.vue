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

      <div class="river-wrap">
        <svg
          ref="svgRef"
          :viewBox="viewBoxStr"
          class="river-svg"
          preserveAspectRatio="xMidYMin meet"
        >
          <defs>
            <!-- 节点阴影 -->
            <filter id="nodeShadow" x="-30%" y="-30%" width="160%" height="160%">
              <feDropShadow dx="1" dy="2" stdDeviation="2" flood-color="rgba(26,51,0,0.12)"/>
            </filter>
          </defs>

          <!-- 透视蜿蜒墨线（粗细随远近渐变） -->
          <path :d="inkPath" fill="var(--color-forest-ink)" opacity="0.28" stroke="none" />
          <!-- 墨线中脊（虚线流动） -->
          <path :d="centerPath" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="1" stroke-dasharray="8 14" class="ink-flow" />

          <!-- 转折点标记 -->
          <g v-for="(k, i) in knotMarkers" :key="'k'+i">
            <circle :cx="k.x" :cy="k.y" r="18" fill="rgba(232,153,112,0.2)" stroke="#e89970" stroke-width="1.5" />
            <text :x="k.x" :y="k.y+1" text-anchor="middle" dominant-baseline="central"
                  font-size="13" font-weight="700" fill="#e89970" font-family="monospace">{{ i+1 }}</text>
            <line :x1="k.x" :y1="k.y" :x2="k.x" :y2="k.y + 26" stroke="#e89970" stroke-width="1" stroke-dasharray="3 3" />
            <text :x="k.x" :y="k.y + 32" text-anchor="middle" font-size="11" fill="#e89970" font-family="monospace">{{ k.label }}</text>
          </g>

          <!-- 日期节点 -->
          <g v-for="(pt, idx) in dayPoints" :key="idx">
            <!-- 节点光晕 -->
            <circle
              v-if="pt.day.hasAnimals && !pt.day.isFuture && pt.day.inMonth"
              :cx="pt.x" :cy="pt.y"
              :r="pt.r + 10"
              :fill="pt.day.isToday ? 'rgba(255,213,79,0.3)' : 'rgba(26,51,0,0.05)'"
            />
            <!-- 节点圆 -->
            <circle
              :cx="pt.x" :cy="pt.y" :r="pt.r"
              :fill="nodeFill(pt)"
              :stroke="nodeStroke(pt)"
              :stroke-width="pt.day.isToday ? 2.5 : 1.2"
              :opacity="pt.day.inMonth ? (0.5 + pt.depth * 0.5) : 0.12"
              :filter="pt.depth > 0.5 ? 'url(#nodeShadow)' : undefined"
              :class="{ 'node-today': pt.day.isToday }"
              :style="{ cursor: pt.day.hasAnimals && !pt.day.isFuture ? 'pointer' : 'default' }"
              @click="pt.day.hasAnimals && !pt.day.isFuture && openDetail(pt.day)"
              @mouseenter="hoveredIdx = idx"
              @mouseleave="hoveredIdx = -1"
            />
            <!-- 日期数字 -->
            <text
              :x="pt.x" :y="pt.y + 1"
              text-anchor="middle" dominant-baseline="central"
              :font-size="9 + pt.depth * 5"
              :font-weight="pt.day.isToday ? 800 : pt.day.inMonth ? 500 : 300"
              :fill="pt.day.isToday ? '#1a3300' : pt.day.inMonth ? '#1a3300' : '#b6b6b6'"
              font-family="'Roboto Mono', monospace"
              style="pointer-events: none;"
            >{{ pt.day.dayNum }}</text>
            <!-- 动物小点 -->
            <circle
              v-if="pt.day.hasCat && pt.day.inMonth && !pt.day.isFuture"
              :cx="pt.x - pt.r * 0.45" :cy="pt.y + pt.r + 6"
              :r="2.5 + pt.depth * 1.5" fill="#1a3300" :opacity="0.35 + pt.depth * 0.45"
            />
            <circle
              v-if="pt.day.hasDog && pt.day.inMonth && !pt.day.isFuture"
              :cx="pt.x + pt.r * 0.45" :cy="pt.y + pt.r + 6"
              :r="2.5 + pt.depth * 1.5" fill="#e89970" :opacity="0.35 + pt.depth * 0.45"
            />
          </g>
        </svg>

        <!-- Hover Tooltip -->
        <div
          v-if="hoveredIdx >= 0 && dayPoints[hoveredIdx]?.day.hasAnimals && dayPoints[hoveredIdx]?.day.inMonth"
          class="river-tooltip"
          :style="tooltipPos"
        >
          <div class="tt-date">{{ dayPoints[hoveredIdx].day.date }}</div>
          <div class="tt-info">
            <span v-if="dayPoints[hoveredIdx].day.hasCat">有猫</span>
            <span v-if="dayPoints[hoveredIdx].day.hasCat && dayPoints[hoveredIdx].day.hasDog"> · </span>
            <span v-if="dayPoints[hoveredIdx].day.hasDog">有狗</span>
          </div>
        </div>
      </div>

      <!-- 图例 -->
      <div class="river-legend">
        <span class="legend-item"><span class="legend-dot" style="background:#1a3300"></span>有猫</span>
        <span class="legend-item"><span class="legend-dot" style="background:#e89970"></span>有狗</span>
        <span class="legend-item"><span class="legend-dot legend-dot--today"></span>今天</span>
      </div>
    </n-layout-content>

    <!-- 详情弹窗 -->
    <n-modal v-model:show="showDetail" preset="card" :title="fmtDate(selectedDate)" style="max-width: 560px" :mask-closable="true">
      <n-spin :show="detailLoading">
        <n-empty v-if="!detailLoading && detailLocations.length === 0" description="这天还没有检测记录" :show-icon="false" />
        <div v-else class="detail-list">
          <PaperCard v-for="loc in detailLocations" :key="loc.name" stripe="ink" padding="sm" class="detail-card">
            <div class="detail-loc"><strong>{{ loc.name }}</strong></div>
            <div class="detail-breeds">
              <InkTag v-for="b in loc.breeds" :key="b" variant="mint">{{ b }}</InkTag>
            </div>
          </PaperCard>
        </div>
      </n-spin>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import PublicNav from '@/components/PublicNav.vue'
import PaperCard from '@/components/PaperCard.vue'
import InkTag from '@/components/InkTag.vue'
import { getCalendar, getPublicDetections } from '@/api/public.js'

const viewYear = ref(new Date().getFullYear())
const viewMonth = ref(new Date().getMonth() + 1)
const calendarData = ref({ days: [] })
const showDetail = ref(false)
const detailLoading = ref(false)
const detailLocations = ref([])
const selectedDate = ref('')
const hoveredIdx = ref(-1)
const svgRef = ref(null)

// ---- SVG 布局（透视引擎） ----
const svgW = 1200
const svgH = 960
const cx = svgW / 2
const vanishY = 30
const bottomY = 850
const rowCount = 6
const totalRange = bottomY - vanishY

function perspectiveDepth(t) {
  return Math.pow(t, 1.8)
}

// 用户给的横向偏移值（相对比例，自动映射到视口宽度的 88%）
const meanderKnots = [
  { t: 0.00, offset: 0 },
  { t: 0.20, offset: 150 },
  { t: 0.40, offset: -300 },
  { t: 0.60, offset: 470 },
  { t: 0.80, offset: -650 },
  { t: 1.00, offset: 900 },
]
const maxOffset = 900
const swingRatio = 0.74  // 最大偏移占视口宽度的比例（每侧）

function meanderX(t) {
  let idx = 0
  for (let j = 0; j < meanderKnots.length - 1; j++) {
    if (t >= meanderKnots[j].t && t <= meanderKnots[j+1].t) { idx = j; break }
  }
  const a = meanderKnots[idx]
  const b = meanderKnots[idx + 1]
  if (!b) return cx
  const seg = (t - a.t) / (b.t - a.t)
  const st = seg * seg * (3 - 2 * seg)
  const off = a.offset + (b.offset - a.offset) * st
  // 将用户偏移值按比例映射到视口宽度
  return cx + (off / maxOffset) * swingRatio * svgW
}

// ══ 墨线路径 ══
const inkSamples = 60

function curvePath(points, close) {
  if (points.length < 2) return ''
  let d = `M ${points[0].x} ${points[0].y}`
  for (let i = 1; i < points.length; i++) {
    const p = points[i - 1]
    const c = points[i]
    const cpY = p.y + (c.y - p.y) * 0.5
    d += ` C ${p.x} ${cpY} ${c.x} ${cpY} ${c.x} ${c.y}`
  }
  if (close) d += ' Z'
  return d
}

function bankPointsFrom(side, points, halfWidths) {
  const sign = side === 'left' ? -1 : 1
  return points.map((pt, i) => {
    const w = halfWidths[i] * sign
    const next = points[Math.min(i + 1, points.length - 1)]
    const dx = next.x - pt.x
    const dy = next.y - pt.y
    const len = Math.sqrt(dx * dx + dy * dy) || 1
    const nx = -dy / len
    const ny = dx / len
    return { x: pt.x + nx * w, y: pt.y + ny * w }
  })
}

function genInkPoints(count) {
  return Array.from({ length: count }, (_, i) => {
    const t = i / (count - 1)
    const depth = perspectiveDepth(t)
    const y = vanishY + depth * totalRange
    const scale = 0.06 + depth * 0.94
    const halfW = 1.5 + scale * 13
    return { x: meanderX(t), y, halfW, scale, t }
  })
}

const pointsCache = computed(() => genInkPoints(inkSamples))

const inkPath = computed(() => {
  const pts = pointsCache.value
  const halfWs = pts.map(p => p.halfW)
  const left = bankPointsFrom('left', pts, halfWs)
  const right = bankPointsFrom('right', pts, halfWs).reverse()
  const top = pts[0]
  const topY = top.y - 40
  return curvePath([
    { x: top.x - top.halfW * 2, y: topY },
    ...left,
    { x: top.x + top.halfW * 2, y: topY },
    ...right,
  ], false) + ' Z'
})

const centerPath = computed(() => curvePath(pointsCache.value, false))

// 视口：紧贴墨线实际范围，不裁剪
const viewBoxStr = computed(() => {
  const pts = pointsCache.value
  if (!pts.length) return `0 0 ${svgW} ${svgH}`
  const xs = pts.flatMap(p => [p.x - p.halfW, p.x + p.halfW])
  const ys = pts.map(p => p.y)
  const minX = Math.min(...xs)
  const maxX = Math.max(...xs)
  const minY = Math.min(...ys) - 60
  const maxY = Math.max(...ys) + 30
  return `${minX} ${minY} ${maxX - minX} ${maxY - minY}`
})

const rows = Array.from({ length: rowCount }, (_, i) => {
  const t = i / (rowCount - 1)
  const depth = perspectiveDepth(t)
  const y = vanishY + depth * totalRange
  const scale = 0.06 + depth * 0.94
  const halfW = 1.5 + scale * 13
  return { y, scale, halfW, t }
})

function centerYs() {
  return rows.map(r => ({ x: meanderX(r.t), y: r.y }))
}

// 转折点标记坐标
const knotMarkers = computed(() => {
  return meanderKnots.map(k => {
    const depth = perspectiveDepth(k.t)
    const y = vanishY + depth * totalRange
    const x = cx + (k.offset / maxOffset) * swingRatio * svgW
    const sign = k.offset >= 0 ? '+' : ''
    return { x, y, label: `${sign}${k.offset}` }
  })
})

// ---- 日期数据 ----
const calendarDays = computed(() => {
  const firstDay = new Date(viewYear.value, viewMonth.value - 1, 1)
  const lastDay = new Date(viewYear.value, viewMonth.value, 0)
  const daysInMonth = lastDay.getDate()
  const startWeekDay = firstDay.getDay()
  const today = new Date()
  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
  const days = []
  const prevLastDay = new Date(viewYear.value, viewMonth.value - 1, 0)
  for (let i = startWeekDay - 1; i >= 0; i--) {
    const d = prevLastDay.getDate() - i
    const m = viewMonth.value === 1 ? 12 : viewMonth.value - 1
    const y = viewMonth.value === 1 ? viewYear.value - 1 : viewYear.value
    days.push({ dayNum: d, date: `${y}-${String(m).padStart(2,'0')}-${String(d).padStart(2,'0')}`, inMonth: false, hasAnimals: false, hasCat: false, hasDog: false, isToday: false, isFuture: false })
  }
  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${viewYear.value}-${String(viewMonth.value).padStart(2,'0')}-${String(d).padStart(2,'0')}`
    const dayData = calendarData.value.days?.find(x => x.date === dateStr)
    const allBreeds = []
    if (dayData?.locations) dayData.locations.forEach(loc => loc.breeds?.forEach(b => allBreeds.push(b)))
    const uniq = [...new Set(allBreeds)]
    days.push({
      dayNum: d, date: dateStr, inMonth: true,
      hasAnimals: dayData?.has_animals || false,
      hasCat: uniq.some(b => b.includes('猫')),
      hasDog: uniq.some(b => !b.includes('猫')),
      isToday: dateStr === todayStr,
      isFuture: dateStr > todayStr,
    })
  }
  const remaining = 42 - days.length
  for (let d = 1; d <= remaining; d++) {
    const m = viewMonth.value === 12 ? 1 : viewMonth.value + 1
    const y = viewMonth.value === 12 ? viewYear.value + 1 : viewYear.value
    days.push({ dayNum: d, date: `${y}-${String(m).padStart(2,'0')}-${String(d).padStart(2,'0')}`, inMonth: false, hasAnimals: false, hasCat: false, hasDog: false, isToday: false, isFuture: true })
  }
  return days
})

// ---- 节点坐标（透视分布） ----
const dayPoints = computed(() => {
  const center = centerYs()
  const pts = []
  for (let i = 0; i < 42; i++) {
    const rowIdx = Math.floor(i / 7)
    const colIdx = i % 7
    const row = rows[rowIdx]
    const base = center[rowIdx]
    if (!row || !base) continue
    const spread = row.halfW * 0.65
    const x = base.x - spread + (colIdx / 6) * spread * 2
    const jitter = (colIdx % 2 === 0 ? -1 : 1) * (2 + row.scale * 5)
    pts.push({
      x,
      y: base.y + jitter,
      r: 10 + row.scale * 14,
      depth: row.scale,
      row: row,
      day: calendarDays.value[i],
    })
  }
  return pts
})

// ---- 节点样式 ----
function nodeFill(pt) {
  if (pt.day.isToday) return '#fff8e1'
  if (!pt.day.inMonth) return '#f0ede6'
  if (pt.day.hasAnimals && !pt.day.isFuture) return '#e8f5e9'
  return '#fdfcfa'
}
function nodeStroke(pt) {
  if (pt.day.isToday) return '#1a3300'
  if (pt.day.hasAnimals && !pt.day.isFuture) return 'rgba(26,51,0,0.35)'
  return 'rgba(26,51,0,0.12)'
}

// ---- Tooltip ----
const tooltipPos = computed(() => {
  if (hoveredIdx.value < 0 || !dayPoints.value[hoveredIdx.value]) return { display: 'none' }
  const pt = dayPoints.value[hoveredIdx.value]
  const el = svgRef.value
  if (!el) return { display: 'none' }
  const rect = el.getBoundingClientRect()
  const vb = viewBoxStr.value.split(' ').map(Number)
  const sx = rect.width / (vb[2] || svgW)
  const sy = rect.height / (vb[3] || svgH)
  return { left: `${rect.left + (pt.x - vb[0]) * sx}px`, top: `${rect.top + (pt.y - vb[1]) * sy - 52}px`, transform: 'translate(-50%, -100%)' }
})

// ---- 交互 ----
function fmtDate(d) { return d ? d.replace(/-/g, ' / ') : '' }

async function openDetail(day) {
  selectedDate.value = day.date
  showDetail.value = true
  detailLoading.value = true
  try {
    const res = await getPublicDetections(day.date)
    const locMap = {}
    ;(res.items || []).forEach(item => {
      if (!item.total_animals) return
      if (!locMap[item.location_name]) locMap[item.location_name] = { name: item.location_name, breeds: new Set() }
      ;(item.animals || []).forEach(a => locMap[item.location_name].breeds.add(a.breed_cn))
    })
    detailLocations.value = Object.values(locMap).map(l => ({ ...l, breeds: [...l.breeds] }))
  } catch (e) { console.error(e) }
  finally { detailLoading.value = false }
}

async function fetchCalendar() {
  try {
    calendarData.value = await getCalendar(`${viewYear.value}-${String(viewMonth.value).padStart(2,'0')}`)
  } catch (e) { console.error(e) }
}
function prevMonth() { viewMonth.value === 1 ? (viewMonth.value = 12, viewYear.value--) : viewMonth.value--; fetchCalendar() }
function nextMonth() { viewMonth.value === 12 ? (viewMonth.value = 1, viewYear.value++) : viewMonth.value++; fetchCalendar() }
function goToday() { viewYear.value = new Date().getFullYear(); viewMonth.value = new Date().getMonth() + 1; fetchCalendar() }

onMounted(() => fetchCalendar())
</script>

<style scoped>
.calendar-page { min-height: 100vh; background: var(--color-cream-paper); }
.cal-content { max-width: 1200px; margin: 0 auto; padding: 24px 20px 60px; }
.month-header { display: flex; align-items: center; gap: 20px; margin-bottom: 24px; }
.month-title { margin: 0; font-size: 22px; color: var(--color-forest-ink); }

.river-wrap { position: relative; width: 100%; }
.river-svg { width: 100%; height: auto; display: block; }

/* 中脊虚线流动 */
.ink-flow {
  stroke-dashoffset: 0;
  animation: flowDown 4s linear infinite;
}
@keyframes flowDown {
  from { stroke-dashoffset: 0; }
  to { stroke-dashoffset: -52; }
}

.node-today { animation: pulse 2s ease-in-out infinite; }
@keyframes pulse {
  0%, 100% { filter: drop-shadow(0 0 4px rgba(255,213,79,0.6)); }
  50% { filter: drop-shadow(0 0 14px rgba(255,213,79,0.95)); }
}

.river-tooltip {
  position: fixed; z-index: 100;
  background: var(--color-cream-paper);
  border: 1px solid var(--color-pencil-gray);
  border-radius: 8px; padding: 8px 14px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
  pointer-events: none; white-space: nowrap;
}
.tt-date { font-family: var(--font-mono); font-size: 13px; font-weight: var(--weight-semibold); color: var(--color-forest-ink); font-feature-settings: 'tnum'; }
.tt-info { font-size: 12px; color: var(--color-whisper-gray); margin-top: 2px; }

.river-legend { display: flex; gap: 20px; justify-content: center; margin-top: 20px; font-size: 13px; color: var(--color-whisper-gray); }
.legend-item { display: flex; align-items: center; gap: 6px; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; }
.legend-dot--today { background: #fff8e1; border: 2px solid #1a3300; }

.detail-list { display: flex; flex-direction: column; gap: 10px; }
.detail-card { margin-bottom: 2px; }
.detail-loc { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; color: var(--color-forest-ink); }
.detail-breeds { display: flex; gap: 4px; flex-wrap: wrap; }

@media (max-width: 768px) {
  .cal-content { padding: 16px 10px 40px; }
}
</style>
