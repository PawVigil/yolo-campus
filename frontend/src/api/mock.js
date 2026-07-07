/**
 * 🧪 开发期 Mock 数据
 *
 * 按第6章接口契约编写，每个接口一个 mock 函数。
 * 联调时只需把 api/index.js 中 USE_MOCK 改为 false。
 */

// ---- 工具函数 ----
const delay = (ms = 200) => new Promise((r) => setTimeout(r, ms))

// ---- 地点数据 ----
const locations = [
  { id: 1, name: '食堂', description: '校园食堂及周边区域，中午人流量大', safety_tip: '近期猫咪出没频繁，请勿随意投喂', created_at: '2026-06-01T10:00:00' },
  { id: 2, name: '宿舍', description: '学生宿舍楼周边，傍晚较为安静', safety_tip: null, created_at: '2026-06-01T10:00:00' },
  { id: 3, name: '图书馆', description: '图书馆前后绿化带', safety_tip: null, created_at: '2026-06-01T10:00:00' },
  { id: 4, name: '操场', description: '田径场及周边健身区域', safety_tip: '请留意周围流浪狗', created_at: '2026-06-01T10:00:00' },
  { id: 5, name: '花园', description: '校园中心花园及小树林', safety_tip: null, created_at: '2026-06-02T08:00:00' },
]

// ---- 品种列表 ----
const breeds = ['橘猫', '三花', '黄狗', '奶牛猫', '布偶猫', '暹罗猫', '柴犬', '英国短毛猫', '孟加拉豹猫', '波斯猫', '萨摩耶', '比格犬']

// ---- 生成随机检测结果 ----
function makeAnimal(i) {
  const b = breeds[i % breeds.length]
  return {
    breed_cn: b,
    breed_en: b === '橘猫' ? 'Orange Tabby' : b === '三花' ? 'Calico' : b === '黄狗' ? 'Yellow Dog' : b === '奶牛猫' ? 'Cow Cat' : b === '布偶猫' ? 'Ragdoll' : b === '暹罗猫' ? 'Siamese' : b === '柴犬' ? 'Shiba Inu' : b === '英国短毛猫' ? 'British Shorthair' : b === '孟加拉豹猫' ? 'Bengal' : b === '波斯猫' ? 'Persian' : b === '萨摩耶' ? 'Samoyed' : b === '比格犬' ? 'Beagle' : 'Unknown',
    confidence: +(0.7 + Math.random() * 0.29).toFixed(4),
    box: {
      x1: +(Math.random() * 300).toFixed(1),
      y1: +(Math.random() * 200).toFixed(1),
      x2: +(300 + Math.random() * 300).toFixed(1),
      y2: +(200 + Math.random() * 200).toFixed(1),
    },
  }
}

function makeDetection(id, locId) {
  const loc = locations.find((l) => l.id === locId)
  const animalCount = Math.floor(Math.random() * 3) + 1
  const animals = Array.from({ length: animalCount }, (_, i) => makeAnimal(i + id))
  const detectTime = `2026-07-${String(Math.floor(Math.random() * 7) + 1).padStart(2, '0')}T${String(Math.floor(Math.random() * 14) + 6).padStart(2, '0')}:${String(Math.floor(Math.random() * 60)).padStart(2, '0')}:00`
  return {
    id,
    location_name: loc?.name || '未知',
    location_id: locId,
    image_url: '/uploads/demo_orig.jpg',
    annotated_url: '/uploads/annotated/demo_annotated.jpg',
    detect_time: detectTime,
    result_json: JSON.stringify(animals),
    total_animals: animalCount,
    animals,
    breed_summary: [...new Set(animals.map((a) => a.breed_cn))].join(', '),
    created_at: detectTime,
  }
}

const detections = Array.from({ length: 47 }, (_, i) => makeDetection(i + 1, (i % 5) + 1))

// ---- 安全提醒 mock ----
const safetyTips = [
  { id: 1, location_id: 1, location_name: '食堂', title: '食堂区域猫咪频繁出没', content: '近7天检测23次，主要为橘猫和三花猫。请同学们注意避让，不要随意投喂。', status: 'published', created_at: '2026-07-01T09:00:00', published_at: '2026-07-01T10:00:00' },
  { id: 2, location_id: 4, location_name: '操场', title: '操场周边流浪狗出没提醒', content: '近7天检测12次，主要为黄狗。建议晚间跑步的同学注意安全，不要单独逗留。', status: 'published', created_at: '2026-07-03T14:00:00', published_at: '2026-07-03T15:00:00' },
  { id: 3, location_id: 3, location_name: '图书馆', title: '图书馆绿化带猫咪增多', content: '近7天检测8次，偶有出没。猫咪在图书馆后门区域较多，请保持关注。', status: 'published', created_at: '2026-07-05T11:00:00', published_at: '2026-07-05T12:30:00' },
  { id: 4, location_id: 2, location_name: '宿舍', title: '宿舍区流浪猫投喂提示', content: '近7天检测15次，请留意周围流浪动物。建议由动保社团统一投喂。', status: 'draft', created_at: '2026-07-06T16:00:00', published_at: null },
  { id: 5, location_id: 5, location_name: '花园', title: '花园区域旧提醒（已下架）', content: '已过期', status: 'archived', created_at: '2026-06-20T08:00:00', published_at: '2026-06-20T09:00:00' },
]

// ---- 社区分享 mock ----
const communityItems = [
  { id: 1, image_url: '/uploads/community/demo1.jpg', location_name: '花园', description: '在花园发现一只超可爱的橘猫！', nickname: '猫猫侠', breed: '橘猫', created_at: '2026-07-06T15:30:00' },
  { id: 2, image_url: '/uploads/community/demo2.jpg', location_name: '食堂', description: '食堂后面的三花猫，每天都来', nickname: '干饭人', breed: '三花', created_at: '2026-07-06T12:00:00' },
  { id: 3, image_url: '/uploads/community/demo3.jpg', location_name: '图书馆', description: '图书馆旁边有一只布偶猫，超级亲人！', nickname: '学霸猫', breed: '布偶猫', created_at: '2026-07-05T18:00:00' },
  { id: 4, image_url: '/uploads/community/demo4.jpg', location_name: '操场', description: '操场上看到一只柴犬在跑步', nickname: '运动达人', breed: '柴犬', created_at: '2026-07-05T16:00:00' },
]

// ---- 排行榜 mock ----
const rankingsData = {
  most_seen: { breed: '橘猫', count: 32, percentage: 0.35 },
  homebody: { breed: '三花', location: '食堂', percentage: 0.82 },
  rare: { breed: '萨摩耶', count: 1 },
  busiest_place: { name: '食堂', count: 23, percentage: 0.42 },
  best_time: { hour_range: '12:00 - 14:00', avg_count: 4.5 },
}

// ---- 趋势数据 ----
function makeTrend(days) {
  const trend = []
  for (let i = days - 1; i >= 0; i--) {
    const d = new Date(2026, 6, 7 - i)
    trend.push({
      day: d.toISOString().slice(0, 10),
      count: Math.floor(Math.random() * 10) + 1,
    })
  }
  return trend
}

// ---- 日历数据 ----
function makeCalendarData(month) {
  const days = []
  const year = parseInt(month.split('-')[0])
  const mon = parseInt(month.split('-')[1])
  const daysInMonth = new Date(year, mon, 0).getDate()
  for (let d = 1; d <= daysInMonth; d++) {
    const hasAnimals = Math.random() > 0.5
    const date = `${month}-${String(d).padStart(2, '0')}`
    days.push({
      date,
      has_animals: hasAnimals,
      locations: hasAnimals
        ? [
            { name: '食堂', breeds: ['橘猫', '三花'].slice(0, Math.floor(Math.random() * 2) + 1) },
            { name: '宿舍', breeds: ['奶牛猫'].slice(0, Math.floor(Math.random() * 1) + 1) },
          ].filter((l) => l.breeds.length > 0)
        : [],
    })
  }
  return { month, days }
}

// ---- 指南数据 ----
function makeGuideData() {
  const guideLocations = [
    { name: '食堂', emoji: '🍽️', rating: 5, appearance_rate: 0.85, main_breeds: [{ breed_cn: '橘猫', count: 18 }, { breed_cn: '三花', count: 12 }], best_time: { start: '12:00', end: '13:00' }, pattern_desc: '几乎每天都会出现，午餐时间是它们最活跃的时段', tip: '带根火腿肠去食堂后门，橘猫大概率会在那里等你！中午12点左右是观测最佳时段。' },
    { name: '宿舍', emoji: '🏠', rating: 4, appearance_rate: 0.65, main_breeds: [{ breed_cn: '奶牛猫', count: 8 }, { breed_cn: '布偶猫', count: 5 }], best_time: { start: '17:00', end: '18:00' }, pattern_desc: '傍晚时分活跃，经常在宿舍楼周边出没', tip: '傍晚下课回宿舍的路上多留意绿化带，奶牛猫喜欢在草丛里打盹。' },
    { name: '图书馆', emoji: '📚', rating: 3, appearance_rate: 0.45, main_breeds: [{ breed_cn: '布偶猫', count: 6 }, { breed_cn: '暹罗猫', count: 4 }], best_time: { start: '15:00', end: '16:00' }, pattern_desc: '下午偶尔出现，喜欢在图书馆后门的台阶上晒太阳', tip: '下午去图书馆自习时，从后门进去可能会遇到晒太阳的布偶猫，它很亲人但别打扰它午睡。' },
    { name: '操场', emoji: '🏟️', rating: 2, appearance_rate: 0.30, main_breeds: [{ breed_cn: '黄狗', count: 6 }, { breed_cn: '柴犬', count: 3 }], best_time: { start: '06:00', end: '07:00' }, pattern_desc: '早晨偶尔出现，多为流浪狗在操场边缘活动', tip: '晨跑时可能会在操场东北角看到黄狗，建议保持距离观察。' },
    { name: '花园', emoji: '🌳', rating: 1, appearance_rate: 0.15, main_breeds: [{ breed_cn: '波斯猫', count: 2 }], best_time: { start: '10:00', end: '11:00' }, pattern_desc: '不常出现，偶尔有小猫在花丛中穿梭', tip: '上午阳光好的时候在花园长椅附近可能会遇到小猫，但概率不高，不要抱太大期望。' },
  ]
  return { locations: guideLocations }
}

// ---- Dashboard 数据 ----
const adminDashboardData = {
  stats: {
    total_detections: 156,
    with_animals: 89,
    locations_covered: 5,
    published_tips: 3,
  },
  location_ranking: [
    { name: '食堂', count: 47 },
    { name: '宿舍', count: 28 },
    { name: '图书馆', count: 15 },
    { name: '操场', count: 10 },
    { name: '花园', count: 4 },
  ],
  breed_top5: [
    { breed: '橘猫', count: 32 },
    { breed: '三花', count: 22 },
    { breed: '黄狗', count: 12 },
    { breed: '奶牛猫', count: 8 },
    { breed: '布偶猫', count: 5 },
  ],
  trend_14d: makeTrend(14),
}

const publicDashboardData = {
  stats: {
    total_detections: 156,
    with_animals: 89,
    locations_covered: 5,
    breed_count: 37,
  },
  location_status: [
    { id: 1, name: '食堂', emoji: '🍽️', status: 'active', recent_breeds: ['橘猫', '三花'], last_detect_time: '2026-07-07T13:30:00' },
    { id: 2, name: '宿舍', emoji: '🏠', status: 'resting', recent_breeds: ['奶牛猫'], last_detect_time: '2026-07-07T08:00:00' },
    { id: 3, name: '图书馆', emoji: '📚', status: 'active', recent_breeds: ['布偶猫', '暹罗猫'], last_detect_time: '2026-07-07T14:00:00' },
    { id: 4, name: '操场', emoji: '🏟️', status: 'resting', recent_breeds: ['黄狗'], last_detect_time: '2026-07-07T05:30:00' },
    { id: 5, name: '花园', emoji: '🌳', status: 'no_record', recent_breeds: [], last_detect_time: null },
  ],
  trend_14d: makeTrend(14),
  safety_tips: [
    { location_name: '食堂', content: '近期猫咪出没频繁，请勿随意投喂' },
    { location_name: '操场', content: '请留意周围流浪狗' },
  ],
}

// ============================================================
// Mock API 函数（每个对应一个真实接口）
// ============================================================

// ---- 鉴权 ----
export async function mockLogin(username, password) {
  await delay()
  if (username === 'admin' && password === 'admin123') {
    return { token: 'mock-jwt-token-abc123', username: 'admin', role: 'admin' }
  }
  throw { response: { status: 401, data: { detail: '用户名或密码错误' } } }
}

// ---- 管理端 ----
export async function mockUpload(file, locationId) {
  await delay(800)
  const animals = [makeAnimal(0), makeAnimal(1)]
  return {
    image_url: '/uploads/demo_orig.jpg',
    annotated_url: '/uploads/annotated/demo_annotated.jpg',
    animals,
    total: animals.length,
  }
}

export async function mockSaveDetection(data) {
  await delay(300)
  const id = Math.floor(Math.random() * 1000) + 200
  return { id, created_at: new Date().toISOString() }
}

export async function mockGetDetections(params = {}) {
  await delay(400)
  const page = params.page || 1
  const pageSize = params.page_size || 15
  let items = [...detections]
  if (params.location_id) items = items.filter((d) => d.location_id === parseInt(params.location_id))
  if (params.date_from) items = items.filter((d) => d.detect_time >= params.date_from)
  if (params.date_to) items = items.filter((d) => d.detect_time <= params.date_to + 'T23:59:59')
  const total = items.length
  const start = (page - 1) * pageSize
  items = items.slice(start, start + pageSize)
  return { items, total, page, page_size: pageSize }
}

export async function mockGetDetectionById(id) {
  await delay(300)
  const d = detections.find((d) => d.id === parseInt(id))
  if (!d) throw { response: { status: 404, data: { detail: '检测记录不存在' } } }
  return d
}

export async function mockDeleteDetection(id) {
  await delay(300)
  return { ok: true }
}

export async function mockGetLocations() {
  await delay(200)
  return { items: locations }
}

export async function mockCreateLocation(data) {
  await delay(300)
  const id = locations.length + 1
  const loc = { id, name: data.name, description: data.description || null, safety_tip: null, created_at: new Date().toISOString() }
  locations.push(loc)
  return loc
}

export async function mockUpdateLocation(id, data) {
  await delay(300)
  const loc = locations.find((l) => l.id === parseInt(id))
  if (!loc) throw { response: { status: 404, data: { detail: '地点不存在' } } }
  if (data.name) loc.name = data.name
  if (data.description !== undefined) loc.description = data.description
  return loc
}

export async function mockDeleteLocation(id) {
  await delay(300)
  return { ok: true }
}

export async function mockGetSafetyTips() {
  await delay(300)
  return { items: safetyTips }
}

export async function mockCreateSafetyTip(data) {
  await delay(300)
  const id = safetyTips.length + 1
  const tip = {
    id,
    location_id: data.location_id,
    location_name: locations.find((l) => l.id === data.location_id)?.name || '',
    title: data.title,
    content: data.content,
    status: data.status || 'draft',
    created_at: new Date().toISOString(),
    published_at: null,
  }
  safetyTips.push(tip)
  return tip
}

export async function mockUpdateSafetyTip(id, data) {
  await delay(300)
  const tip = safetyTips.find((t) => t.id === parseInt(id))
  if (!tip) throw { response: { status: 404, data: { detail: '提醒不存在' } } }
  if (data.title) tip.title = data.title
  if (data.content) tip.content = data.content
  return tip
}

export async function mockUpdateSafetyTipStatus(id, status) {
  await delay(300)
  const tip = safetyTips.find((t) => t.id === parseInt(id))
  if (!tip) throw { response: { status: 404, data: { detail: '提醒不存在' } } }
  tip.status = status
  if (status === 'published') tip.published_at = new Date().toISOString()
  return { id: tip.id, status: tip.status, published_at: tip.published_at }
}

export async function mockGetSuggestions() {
  await delay(500)
  return {
    suggestions: [
      { location_id: 1, location_name: '食堂', count: 23, suggestion_text: '频繁出没，请注意避让', data_basis: '近7天检测23次' },
      { location_id: 2, location_name: '宿舍', count: 15, suggestion_text: '请留意周围', data_basis: '近7天检测15次' },
      { location_id: 4, location_name: '操场', count: 12, suggestion_text: '请留意周围', data_basis: '近7天检测12次' },
      { location_id: 3, location_name: '图书馆', count: 8, suggestion_text: '偶有出没，请保持关注', data_basis: '近7天检测8次' },
    ],
  }
}

export async function mockGetAdminDashboard() {
  await delay(400)
  return adminDashboardData
}

export async function mockGetWeeklyReport(params) {
  await delay(600)
  if (params.format === 'csv') return '指标,数值\n总检测数,47\n有动物记录数,32\n覆盖地点数,5\n最常见品种,橘猫(18次)\n最活跃地点,食堂(23次)'
  return {
    type: 'weekly',
    period: { start: params.start, end: params.end },
    data: [
      { metric: '总检测数', value: 47 },
      { metric: '有动物记录数', value: 32 },
      { metric: '覆盖地点数', value: 5 },
      { metric: '最常见品种', value: '橘猫(18次)' },
      { metric: '最活跃地点', value: '食堂(23次)' },
    ],
  }
}

export async function mockGetMonthlyReport(params) {
  await delay(600)
  if (params.format === 'csv') return '指标,数值\n总检测数,156\n有动物记录数,89\n覆盖地点数,5\n最常见品种,橘猫(32次)\n最活跃地点,食堂(47次)'
  return {
    type: 'monthly',
    period: { year: params.year, month: params.month },
    data: [
      { metric: '总检测数', value: 156 },
      { metric: '有动物记录数', value: 89 },
      { metric: '覆盖地点数', value: 5 },
      { metric: '最常见品种', value: '橘猫(32次)' },
      { metric: '最活跃地点', value: '食堂(47次)' },
    ],
  }
}

// ---- 公共端 ----
export async function mockGetPublicDashboard() {
  await delay(400)
  return publicDashboardData
}

export async function mockGetCalendar(month) {
  await delay(400)
  return makeCalendarData(month || '2026-07')
}

export async function mockGetPublicDetections(date) {
  await delay(300)
  const items = detections.filter((d) => d.detect_time.startsWith(date)).slice(0, 10)
  return { items }
}

export async function mockGetRankings() {
  await delay(400)
  return rankingsData
}

export async function mockGetGuide() {
  await delay(400)
  return makeGuideData()
}

export async function mockGetPublicSafetyTips() {
  await delay(200)
  return { items: safetyTips.filter((t) => t.status === 'published') }
}

export async function mockGetShareCard(detectionId) {
  await delay(300)
  return { html: `<html><body><div style="text-align:center;padding:40px"><h1>🐾 分享卡片 #${detectionId}</h1><p>此卡片将在后端渲染为完整HTML</p></div></body></html>` }
}

export async function mockUploadCommunity(formData) {
  await delay(800)
  const id = communityItems.length + 1
  const breed = formData.get('auto_detect') === 'true' ? '橘猫' : null
  const item = {
    id,
    image_url: '/uploads/community/new_demo.jpg',
    location_name: null,
    description: formData.get('description') || null,
    nickname: formData.get('nickname') || null,
    breed,
    breed_card: breed
      ? {
          name_cn: '橘猫',
          emoji: '🐱',
          size: '中型',
          temperament: '活泼亲人，喜欢吃，容易发胖',
          fun_fact: '橘猫的毛色由基因决定，80%的橘猫是公猫！而且橘猫通常比其他花色的猫体型更大。',
        }
      : null,
    created_at: new Date().toISOString(),
  }
  communityItems.unshift(item)
  return item
}

export async function mockGetCommunity(params = {}) {
  await delay(300)
  const page = params.page || 1
  const pageSize = params.page_size || 12
  const total = communityItems.length
  const start = (page - 1) * pageSize
  const items = communityItems.slice(start, start + pageSize)
  return { items, total, page, page_size: pageSize }
}
