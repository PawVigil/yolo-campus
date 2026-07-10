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
          <!-- 墨线中脊 -->
          <path :d="centerPath" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="1" stroke-dasharray="8 14" />

          <!-- 沿线爪印装饰 -->
          <g v-for="(d, di) in decorPoints" :key="'d'+di">
            <g :transform="`translate(${d.x}, ${d.y}) rotate(${d.rot}) scale(${d.scale})`"
               :opacity="d.opacity" fill="#1a3300" stroke="none">
              <ellipse cx="0" cy="-3" rx="3.5" ry="4.5" />
              <circle cx="-5.5" cy="-9" r="2.2" />
              <circle cx="-1.5" cy="-11.5" r="2.2" />
              <circle cx="2.5" cy="-11.5" r="2.2" />
              <circle cx="6" cy="-8.5" r="2.2" />
            </g>
          </g>

          <!-- 日期节点 -->
          <g v-for="(pt, idx) in dayPoints" :key="idx">
            <!-- 节点光晕 -->
            <circle
              :cx="pt.x" :cy="pt.y"
              :r="pt.r + 10"
              :fill="pt.day.isToday ? 'rgba(255,213,79,0.3)' : 'rgba(26,51,0,0.05)'"
            />
            <!-- 外环（虚线） -->
            <circle
              :cx="pt.x" :cy="pt.y" :r="pt.r + 5"
              fill="none"
              :stroke="pt.day.isToday ? '#1a3300' : 'rgba(26,51,0,0.25)'"
              :stroke-width="1"
              stroke-dasharray="3 3"
              :opacity="0.4 + pt.depth * 0.4"
              style="pointer-events: none"
            />
            <!-- 内环（实心） -->
            <circle
              :cx="pt.x" :cy="pt.y" :r="pt.r"
              :fill="pt.day.isToday ? '#fff8e1' : '#e8f5e9'"
              :stroke="pt.day.isToday ? '#1a3300' : 'rgba(26,51,0,0.4)'"
              :stroke-width="pt.day.isToday ? 2.5 : 1.5"
              :opacity="0.5 + pt.depth * 0.5"
              :filter="pt.depth > 0.5 ? 'url(#nodeShadow)' : undefined"
              :class="{ 'node-today': pt.day.isToday }"
              style="cursor: pointer"
              @click="openDetail(pt.day)"
              @mouseenter="hoveredIdx = idx"
              @mouseleave="hoveredIdx = -1"
            />
            <!-- 日期数字 -->
            <text
              :x="pt.x" :y="pt.y + 1"
              text-anchor="middle" dominant-baseline="central"
              :font-size="16 + pt.depth * 12"
              :font-weight="700"
              fill="#1a3300"
              font-family="'Roboto Mono', monospace"
              style="pointer-events: none;"
            >{{ pt.day.dayNum }}</text>
            <!-- 环上装饰点：猫 -->
            <circle
              v-if="pt.day.hasCat"
              :cx="pt.x - (pt.r + 5)" :cy="pt.y"
              :r="2.5 + pt.depth * 1.5" fill="#1a3300" :opacity="0.5 + pt.depth * 0.4"
            />
            <!-- 环上装饰点：狗 -->
            <circle
              v-if="pt.day.hasDog"
              :cx="pt.x + (pt.r + 5)" :cy="pt.y"
              :r="2.5 + pt.depth * 1.5" fill="#e89970" :opacity="0.5 + pt.depth * 0.4"
            />
          </g>
        </svg>

        <!-- Hover Tooltip -->
        <div
          v-if="hoveredIdx >= 0 && dayPoints[hoveredIdx]"
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
const inkSamples = 150

function curvePath(points, close) {
  if (points.length < 2) return ''
  let d = `M ${points[0].x} ${points[0].y}`
  for (let i = 1; i < points.length; i++) {
    d += ` L ${points[i].x} ${points[i].y}`
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
    const halfW = (1.5 + scale * 13) * 5
    return { x: meanderX(t), y, halfW, scale, t }
  })
}

const pointsCache = computed(() => genInkPoints(inkSamples))

// ══ 节点形状生成 ══
// 墨滴形
function blobPath(cx, cy, r, seed) {
  const n = 10
  const pts = []
  for (let i = 0; i < n; i++) {
    const angle = (i / n) * Math.PI * 2
    const jitter = 1 + 0.18 * Math.sin(seed * 137.5 + i * 2.3)
      + 0.10 * Math.cos(seed * 83.1 + i * 3.7)
      + 0.06 * Math.sin(seed * 211.3 + i * 5.1)
    const rr = r * jitter
    pts.push({ x: cx + Math.cos(angle) * rr, y: cy + Math.sin(angle) * rr })
  }
  let d = `M ${pts[0].x.toFixed(1)} ${pts[0].y.toFixed(1)}`
  for (let i = 0; i < n; i++) {
    const p0 = pts[(i - 1 + n) % n]
    const p1 = pts[i]
    const p2 = pts[(i + 1) % n]
    const p3 = pts[(i + 2) % n]
    const t = 0.35
    d += ` C ${(p1.x + (p2.x - p0.x) * t).toFixed(1)} ${(p1.y + (p2.y - p0.y) * t).toFixed(1)}, ${(p2.x - (p3.x - p1.x) * t).toFixed(1)} ${(p2.y - (p3.y - p1.y) * t).toFixed(1)}, ${p2.x.toFixed(1)} ${p2.y.toFixed(1)}`
  }
  return d + ' Z'
}
// 树叶形
function leafPath(cx, cy, r, seed) {
  const rot = (seed * 47) % 360
  const rad = rot * Math.PI / 180
  const w = r * 0.6
  const h = r * 1.15
  // 主轴方向
  const ux = Math.cos(rad), uy = Math.sin(rad)
  const nx = -uy, ny = ux
  const tip = { x: cx + ux * h, y: cy + uy * h }
  const base = { x: cx - ux * h, y: cy - uy * h }
  const l = { x: cx + nx * w, y: cy + ny * w }
  const r2 = { x: cx - nx * w, y: cy - ny * w }
  // 两片叶瓣用贝塞尔
  const d = `M ${tip.x.toFixed(1)} ${tip.y.toFixed(1)}`
    + ` C ${(cx + nx * w * 0.8 + ux * h * 0.2).toFixed(1)} ${(cy + ny * w * 0.8 + uy * h * 0.2).toFixed(1)},`
    + ` ${(cx + nx * w * 0.6 - ux * h * 0.3).toFixed(1)} ${(cy + ny * w * 0.6 - uy * h * 0.3).toFixed(1)},`
    + ` ${base.x.toFixed(1)} ${base.y.toFixed(1)}`
    + ` C ${(cx - nx * w * 0.6 - ux * h * 0.3).toFixed(1)} ${(cy - ny * w * 0.6 - uy * h * 0.3).toFixed(1)},`
    + ` ${(cx - nx * w * 0.8 + ux * h * 0.2).toFixed(1)} ${(cy - ny * w * 0.8 + uy * h * 0.2).toFixed(1)},`
    + ` ${tip.x.toFixed(1)} ${tip.y.toFixed(1)}`
  return { d, vein: { x1: tip.x, y1: tip.y, x2: base.x, y2: base.y } }
}

// ══ 沿线装饰（爪印）══
const decorSeed = [
  0.06, 0.10, 0.16, 0.20, 0.26, 0.30, 0.36, 0.40,
  0.46, 0.50, 0.56, 0.60, 0.66, 0.70, 0.76, 0.80,
  0.86, 0.90, 0.94,
]

const decorPoints = computed(() => {
  const pts = pointsCache.value
  if (pts.length < 10) return []
  return decorSeed.map((seed, i) => {
    const t = 0.04 + seed * 0.92
    const idx = Math.round(t * (pts.length - 1))
    const p = pts[Math.min(idx, pts.length - 1)]
    const next = pts[Math.min(idx + 1, pts.length - 1)]
    // 切线方向（路径走向）
    const dx = next.x - p.x
    const dy = next.y - p.y
    const angle = Math.atan2(dy, dx) * (180 / Math.PI)
    // 法线方向（侧向偏移）
    const len = Math.sqrt(dx * dx + dy * dy) || 1
    const nx = -dy / len
    const ny = dx / len
    const side = (i % 2 === 0) ? 1 : -1
    const offsetDist = p.halfW + 18 + seed * 12
    const x = p.x + nx * offsetDist * side
    const y = p.y + ny * offsetDist * side
    const depth = p.scale
    return {
      x, y,
      rot: angle + 90,
      scale: 0.8 + depth * 1.4,
      opacity: 0.12 + depth * 0.22,
    }
  })
})

// ══ 植物速写（背景装饰）══
// 蕨叶
function fernPath(x, y, size, rot) {
  const s = size
  const r = rot * Math.PI / 180
  const cos = Math.cos(r), sin = Math.sin(r)
  const tx = (dx, dy) => ({ x: x + dx * cos - dy * sin, y: y + dx * sin + dy * cos })
  const stem = `M ${tx(0,0).x} ${tx(0,0).y} L ${tx(0,-s).x} ${tx(0,-s).y}`
  const leaves = []
  for (let i = 1; i <= 5; i++) {
    const ty = -s * (i / 6)
    const leafLen = s * 0.35 * (1 - i / 7)
    const l = tx(-leafLen, ty + s * 0.03)
    const r2 = tx(leafLen, ty + s * 0.03)
    const tip = tx(0, ty)
    leaves.push(`M ${tip.x} ${tip.y} Q ${l.x} ${l.y} ${tx(-leafLen * 0.5, ty - s * 0.04).x} ${tx(-leafLen * 0.5, ty - s * 0.04).y}`)
    leaves.push(`M ${tip.x} ${tip.y} Q ${r2.x} ${r2.y} ${tx(leafLen * 0.5, ty - s * 0.04).x} ${tx(leafLen * 0.5, ty - s * 0.04).y}`)
  }
  return stem + ' ' + leaves.join(' ')
}
// 草丛
function grassPath(x, y, size, rot) {
  const s = size
  const r = rot * Math.PI / 180
  const cos = Math.cos(r), sin = Math.sin(r)
  const tx = (dx, dy) => ({ x: x + dx * cos - dy * sin, y: y + dx * sin + dy * cos })
  const blades = []
  for (let i = -2; i <= 2; i++) {
    const bx = i * s * 0.15
    const lean = i * s * 0.12
    const tip = tx(bx + lean, -s)
    const base = tx(bx, 0)
    const cp = tx(bx + lean * 0.5, -s * 0.6)
    blades.push(`M ${base.x} ${base.y} Q ${cp.x} ${cp.y} ${tip.x} ${tip.y}`)
  }
  return blades.join(' ')
}
// 蒲公英
function dandelionPath(x, y, size, rot) {
  const s = size
  const r = rot * Math.PI / 180
  const cos = Math.cos(r), sin = Math.sin(r)
  const tx = (dx, dy) => ({ x: x + dx * cos - dy * sin, y: y + dx * sin + dy * cos })
  const stem = `M ${tx(0,0).x} ${tx(0,0).y} L ${tx(0,-s*0.7).x} ${tx(0,-s*0.7).y}`
  const seeds = []
  for (let i = 0; i < 8; i++) {
    const a = (i / 8) * Math.PI * 2
    const len = s * 0.35
    const tip = tx(Math.cos(a) * len, -s * 0.7 + Math.sin(a) * len)
    const center = tx(0, -s * 0.7)
    seeds.push(`M ${center.x} ${center.y} L ${tip.x} ${tip.y}`)
  }
  return stem + ' ' + seeds.join(' ')
}

const plantDecorations = [
  { t: 0.06, side: -1, dist: 3.5, type: 'fern', size: 55, rot: -15 },
  { t: 0.18, side: 1, dist: 4.0, type: 'grass', size: 40, rot: 10 },
  { t: 0.30, side: -1, dist: 4.5, type: 'dandelion', size: 45, rot: -20 },
  { t: 0.40, side: 1, dist: 3.8, type: 'fern', size: 50, rot: 15 },
  { t: 0.52, side: -1, dist: 4.2, type: 'grass', size: 35, rot: -8 },
  { t: 0.65, side: 1, dist: 3.5, type: 'dandelion', size: 42, rot: 12 },
  { t: 0.72, side: -1, dist: 4.0, type: 'grass', size: 38, rot: -18 },
  { t: 0.88, side: 1, dist: 3.8, type: 'fern', size: 48, rot: 20 },
]

const plantPaths = computed(() => {
  const pts = pointsCache.value
  if (pts.length < 10) return []
  return plantDecorations.map(p => {
    const idx = Math.round(p.t * (pts.length - 1))
    const pt = pts[Math.min(idx, pts.length - 1)]
    const next = pts[Math.min(idx + 1, pts.length - 1)]
    const dx = next.x - pt.x
    const dy = next.y - pt.y
    const len = Math.sqrt(dx * dx + dy * dy) || 1
    const nx = -dy / len
    const ny = dx / len
    const x = pt.x + nx * pt.halfW * p.dist * p.side
    const y = pt.y + ny * pt.halfW * p.dist * p.side
    let d = ''
    if (p.type === 'fern') d = fernPath(x, y, p.size, p.rot)
    else if (p.type === 'grass') d = grassPath(x, y, p.size, p.rot)
    else d = dandelionPath(x, y, p.size, p.rot)
    return { d, opacity: 0.12 + pt.scale * 0.15 }
  })
})

// ══ 田野笔记统计 ══
const fieldStats = computed(() => {
  const days = calendarDays.value.filter(d => d.inMonth)
  const active = days.filter(d => d.hasAnimals && !d.isFuture)
  const catDays = active.filter(d => d.hasCat).length
  const dogDays = active.filter(d => d.hasDog).length
  const bothDays = active.filter(d => d.hasCat && d.hasDog).length
  let mostActiveDate = ''
  if (active.length) {
    // 取第一个有记录的日期作为示例
    mostActiveDate = active[0].date.slice(5) // MM-DD
  }
  return { activeDays: active.length, catDays, dogDays, bothDays, mostActiveDate }
})

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

// ---- 日期数据 ----
const calendarDays = computed(() => {
  const firstDay = new Date(viewYear.value, viewMonth.value - 1, 1)
  const lastDay = new Date(viewYear.value, viewMonth.value, 0)
  const daysInMonth = lastDay.getDate()
  const today = new Date()
  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
  const days = []
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
  return days
})

// ---- 节点坐标（沿墨线均匀分布） ----
const dayPoints = computed(() => {
  const eligible = calendarDays.value.filter(d => d.hasAnimals && !d.isFuture && d.inMonth)
  if (!eligible.length) return []
  return eligible.map((day, i) => {
    const t = 0.05 + (i / Math.max(eligible.length - 1, 1)) * 0.9
    const depth = perspectiveDepth(t)
    const y = vanishY + depth * totalRange
    const scale = 0.06 + depth * 0.94
    const x = meanderX(t)
    const r = 22 + scale * 24
    const leaf = leafPath(x, y, r, day.dayNum + i * 1.3)
    return { x, y, r, depth: scale, day, blob: leaf.d, vein: leaf.vein }
  })
})

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
.cal-content { max-width: 1200px; margin: 0 auto; padding: 24px 20px 60px; position: relative; z-index: 1; }
.month-header { display: flex; align-items: center; gap: 20px; margin-bottom: 24px; }
.month-title { margin: 0; font-size: 22px; color: var(--color-forest-ink); }

.calendar-main { display: flex; gap: 32px; align-items: flex-start; }
.river-wrap { position: relative; flex: 1; min-width: 0; }
.river-svg { width: 100%; height: auto; display: block; }

/* 田野笔记 */
.field-notes {
  width: 180px; flex-shrink: 0;
  background: rgba(26,51,0,0.02);
  border: 1px solid rgba(26,51,0,0.1);
  border-radius: 6px;
  padding: 20px 16px;
  font-family: 'ZCOOL XiaoWei', 'Noto Serif SC', serif;
  margin-top: 20px;
}
.fn-title {
  font-size: 15px; font-weight: 700; color: #1a3300;
  margin-bottom: 12px; letter-spacing: 2px;
  text-align: center;
}
.fn-line {
  height: 1px; background: rgba(26,51,0,0.08); margin: 10px 0;
}
.fn-row {
  display: flex; justify-content: space-between; align-items: baseline;
  padding: 2px 0;
}
.fn-label {
  font-size: 12px; color: rgba(26,51,0,0.5);
}
.fn-value {
  font-size: 18px; font-weight: 700; color: #1a3300;
  font-family: 'Roboto Mono', monospace;
}
.fn-value--sm { font-size: 13px; font-weight: 500; }
.fn-unit { font-size: 11px; font-weight: 400; color: rgba(26,51,0,0.4); margin-left: 2px; }
.fn-sketch { margin-top: 14px; text-align: center; }
.fn-sketch-svg { width: 80px; height: 60px; }

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
