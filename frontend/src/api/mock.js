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

// ---- 品种列表（与 breed_info.json 一致的37种中文名）----
const CAT_NAMES = ['阿比西尼亚猫','孟加拉豹猫','伯曼猫','孟买猫','英国短毛猫','埃及猫','缅因猫','波斯猫','布偶猫','俄罗斯蓝猫','暹罗猫','斯芬克斯猫']
const DOG_NAMES = ['美国斗牛犬','美国比特犬','巴吉度猎犬','比格犬','拳师犬','吉娃娃','英国可卡犬','英国雪达犬','德国短毛指示犬','大白熊犬','哈瓦那犬','日本狆','荷兰毛狮犬','兰伯格犬','迷你品犬','纽芬兰犬','博美犬','巴哥犬','圣伯纳犬','萨摩耶','苏格兰梗','柴犬','斯塔福郡斗牛梗','软毛麦色梗','约克夏梗']
const ALL_BREED_CN = [...CAT_NAMES, ...DOG_NAMES]

// breed_en 反向映射（中文名→英文key，从 breed_info.json 推导）
const BREED_EN_MAP = {}
CAT_NAMES.forEach(n => { BREED_EN_MAP[n] = n === '阿比西尼亚猫' ? 'Abyssinian' : n === '孟加拉豹猫' ? 'Bengal' : n === '伯曼猫' ? 'Birman' : n === '孟买猫' ? 'Bombay' : n === '英国短毛猫' ? 'British_Shorthair' : n === '埃及猫' ? 'Egyptian_Mau' : n === '缅因猫' ? 'Maine_Coon' : n === '波斯猫' ? 'Persian' : n === '布偶猫' ? 'Ragdoll' : n === '俄罗斯蓝猫' ? 'Russian_Blue' : n === '暹罗猫' ? 'Siamese' : 'Sphynx' })
DOG_NAMES.forEach(n => { BREED_EN_MAP[n] = n === '美国斗牛犬' ? 'american_bulldog' : n === '美国比特犬' ? 'american_pit_bull_terrier' : n === '巴吉度猎犬' ? 'basset_hound' : n === '比格犬' ? 'beagle' : n === '拳师犬' ? 'boxer' : n === '吉娃娃' ? 'chihuahua' : n === '英国可卡犬' ? 'english_cocker_spaniel' : n === '英国雪达犬' ? 'english_setter' : n === '德国短毛指示犬' ? 'german_shorthaired' : n === '大白熊犬' ? 'great_pyrenees' : n === '哈瓦那犬' ? 'havanese' : n === '日本狆' ? 'japanese_chin' : n === '荷兰毛狮犬' ? 'keeshond' : n === '兰伯格犬' ? 'leonberger' : n === '迷你品犬' ? 'miniature_pinscher' : n === '纽芬兰犬' ? 'newfoundland' : n === '博美犬' ? 'pomeranian' : n === '巴哥犬' ? 'pug' : n === '圣伯纳犬' ? 'saint_bernard' : n === '萨摩耶' ? 'samoyed' : n === '苏格兰梗' ? 'scottish_terrier' : n === '柴犬' ? 'shiba_inu' : n === '斯塔福郡斗牛梗' ? 'staffordshire_bull_terrier' : n === '软毛麦色梗' ? 'wheaten_terrier' : 'yorkshire_terrier' })

function isCat(name) { return CAT_NAMES.includes(name) }
function isDog(name) { return DOG_NAMES.includes(name) }

// ---- 生成随机检测结果 ----
function makeAnimal(i) {
  const b = ALL_BREED_CN[i % ALL_BREED_CN.length]
  return {
    breed_cn: b,
    breed_en: BREED_EN_MAP[b] || 'Unknown',
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
  // ~25% 的记录拍不到动物
  const hasAnimals = Math.random() > 0.25
  const animalCount = hasAnimals ? Math.floor(Math.random() * 3) + 1 : 0
  const animals = hasAnimals ? Array.from({ length: animalCount }, (_, i) => makeAnimal(i + id)) : []
  // 近14天 (2026-06-25 ~ 2026-07-08)
  const d = new Date(2026, 6, 8 - Math.floor(Math.random() * 14))
  const dateStr = d.toISOString().slice(0, 10)
  const timeStr = `${String(Math.floor(Math.random() * 14) + 6).padStart(2, '0')}:${String(Math.floor(Math.random() * 60)).padStart(2, '0')}:00`
  return {
    id,
    location_name: loc?.name || '未知',
    location_id: locId,
    image_url: '/uploads/demo_orig.jpg',
    annotated_url: '/uploads/annotated/demo_annotated.jpg',
    detect_time: `${dateStr}T${timeStr}`,
    result_json: JSON.stringify(animals),
    total_animals: animalCount,
    animals,
    breed_summary: hasAnimals ? [...new Set(animals.map((a) => a.breed_cn))].join(', ') : '',
    created_at: `${dateStr}T${timeStr}`,
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
// ---- 社区分享 mock（多图+评论，使用真实动物占位照片）----
function catPhoto(id) { return `https://cataas.com/cat?width=400&height=300&random=${id}` }
function dogPhoto(id) { return `https://placedog.net/400/300?random=${id}` }

const communityItems = [
  { id: 1, images: [catPhoto(11), catPhoto(12)], location_name: '花园', description: '在花园发现一只超可爱的英国短毛猫！', nickname: '猫猫侠', breed: '英国短毛猫', created_at: '2026-07-08T07:30:00', comments: [{ id: 1, nickname: '路人甲', text: '好可爱！在哪看到的？', time: '2026-07-08T08:00:00' },{ id: 2, nickname: '猫猫侠', text: '花园长椅附近~', time: '2026-07-08T08:05:00' }] },
  { id: 2, images: [catPhoto(13), catPhoto(14)], location_name: '食堂', description: '食堂后面的孟买猫，每天都来', nickname: '干饭人', breed: '孟买猫', created_at: '2026-07-07T12:15:00', comments: [{ id: 3, nickname: '学霸猫', text: '我也经常看到它！', time: '2026-07-07T13:00:00' }] },
  { id: 3, images: [catPhoto(15), dogPhoto(11), catPhoto(16)], location_name: '图书馆', description: '图书馆旁边有一只布偶猫，超级亲人！还有一只柴犬', nickname: '学霸猫', breed: '布偶猫', created_at: '2026-07-08T08:45:00', comments: [{ id: 4, nickname: '干饭人', text: '布偶猫也太好看了吧！', time: '2026-07-08T09:00:00' }] },
  { id: 4, images: [dogPhoto(12), dogPhoto(13)], location_name: '操场', description: '操场上看到一只柴犬在跑步', nickname: '运动达人', breed: '柴犬', created_at: '2026-07-08T06:30:00', comments: [{ id: 5, nickname: '干饭人', text: '哈哈它每天都来跑步', time: '2026-07-08T07:00:00' }] },
  { id: 5, images: [catPhoto(17)], location_name: '宿舍', description: '宿舍楼下偶遇一只俄罗斯蓝猫', nickname: '猫奴', breed: '俄罗斯蓝猫', created_at: '2026-07-08T09:10:00', comments: [] },
  { id: 6, images: [dogPhoto(14), dogPhoto(15), dogPhoto(16)], location_name: '花园', description: '三只狗狗在花园草坪上玩耍', nickname: '汪星人', breed: '比格犬', created_at: '2026-07-08T09:20:00', comments: [{ id: 6, nickname: '猫猫侠', text: '太欢乐了！', time: '2026-07-08T09:35:00' }] },
]

// ---- 排行榜 mock ----
const rankingsData = {
  most_seen: { breed: '橘猫', count: 32, percentage: 0.35 },
  homebody: { breed: '三花', location: '食堂', percentage: 0.82 },
  rare: { breed: '萨摩耶', count: 1 },
  busiest_place: { name: '食堂', count: 23, percentage: 0.42 },
  best_time: { hour_range: '12:00 - 14:00', avg_count: 4.5 },
}

// 趋势数据见下方 makeTrend() —— 从实际detections聚合

// ---- 日历数据 ----
// 日历数据由 mockGetCalendar 从 detections 动态聚合

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
    get total_detections() { return detections.length },
    get with_animals() { return getLiveStats().withAnimals },
    get locations_covered() { return getLiveStats().locIds.size },
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
  get trend_14d() { return makeTrend() },
}

// ---- 近14天过滤（统一用字符串比较，避免时区问题）----
const DAYS = 14
const MOCK_END = '2026-07-08'
const MOCK_START = '2026-06-25' // 07-08 往前14天

function dayOf(detectTime) {
  return (detectTime || '').slice(0, 10)
}

function inRange(day) {
  return day >= MOCK_START && day <= MOCK_END
}

// 生成近14天日期列表
function last14Days() {
  const days = []
  const end = new Date(MOCK_END)
  for (let i = DAYS - 1; i >= 0; i--) {
    const d = new Date(end)
    d.setDate(d.getDate() - i)
    days.push(d.toISOString().slice(0, 10))
  }
  return days
}

// ---- 品种检测统计（近14天，每只动物计一次）----
function computeBreedStats() {
  const count = {}
  detections.forEach(d => {
    if (!d.animals) return
    if (!inRange(dayOf(d.detect_time))) return
    d.animals.forEach(a => {
      count[a.breed_cn] = (count[a.breed_cn] || 0) + 1
    })
  })
  return count
}

// ---- 趋势数据（近14天有动物记录，按天聚合）----
function makeTrend() {
  const dayMap = {}
  last14Days().forEach(day => { dayMap[day] = 0 })
  detections.forEach(d => {
    if (d.total_animals === 0) return
    const day = dayOf(d.detect_time)
    if (inRange(day)) dayMap[day] = (dayMap[day] || 0) + 1
  })
  return last14Days().map(day => ({ day, count: dayMap[day] || 0 }))
}

// 聚合统计
function getLiveStats() {
  const breedStats = computeBreedStats()
  const breedCount = Object.keys(breedStats).length
  const trend = makeTrend()
  // 有动物记录 = 趋势图每天之和
  const withAnimals = trend.reduce((sum, d) => sum + d.count, 0)
  const inRangeDetections = detections.filter(d => inRange(dayOf(d.detect_time)))
  const locIds = new Set(inRangeDetections.map(d => d.location_id))
  return { breedStats, breedCount, withAnimals, locIds, totalDetections: inRangeDetections.length }
}

const publicDashboardData = {
  stats: {
    get total_detections() { return detections.length },
    get with_animals() { return getLiveStats().withAnimals },
    get locations_covered() { return getLiveStats().locIds.size },
    get breed_count() { return getLiveStats().breedCount },
  },
  get location_status() {
    const emojis = { '食堂': '🍽️', '宿舍': '🏠', '图书馆': '📚', '操场': '🏟️', '花园': '🌳' }
    return locations.map(loc => {
      const locDetections = detections.filter(d => d.location_id === loc.id && inRange(dayOf(d.detect_time)))
      const latest = locDetections.sort((a, b) => (b.detect_time || '').localeCompare(a.detect_time || ''))[0]
      const lastTime = latest?.detect_time || null
      let status = 'no_record'
      if (lastTime) {
        const lastDay = dayOf(lastTime)
        // 同一天 = 0天前 → active; 1天前 → resting; 更早 → no_record
        const dayDiff = last14Days().indexOf(lastDay)
        const todayIdx = DAYS - 1
        if (dayDiff === todayIdx) status = 'active'
        else if (dayDiff >= todayIdx - 1) status = 'resting'
      }
      const recentBreeds = [...new Set(
        locDetections.filter(d => d.total_animals > 0).flatMap(d => (d.animals || []).map(a => a.breed_cn))
      )].slice(0, 3)
      return { id: loc.id, name: loc.name, emoji: emojis[loc.name] || '📍', status, recent_breeds: recentBreeds, last_detect_time: lastTime }
    })
  },
  get trend_14d() { return makeTrend() },
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
  if (params.breed) items = items.filter((d) => {
    const breeds = (d.animals || []).map(a => a.breed_cn)
    return breeds.some(b => b.includes(params.breed))
  })
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
  if (data.status) tip.status = data.status
  return tip
}

export async function mockDeleteSafetyTip(id) {
  await delay(200)
  const idx = safetyTips.findIndex(t => t.id === parseInt(id))
  if (idx < 0) throw { response: { status: 404 } }
  safetyTips.splice(idx, 1)
  return { ok: true }
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
      { location_id: 1, location_name: '食堂', count: 23, suggestion_text: '频繁出没，请注意避让', suggestion_content: '食堂区域近7天检测到23次动物出没，主要为橘猫和三花猫。建议提醒学生保持安全距离，不要随意投喂。', data_basis: '近7天检测23次' },
      { location_id: 2, location_name: '宿舍', count: 15, suggestion_text: '请留意周围', suggestion_content: '宿舍楼周边近7天检测到15次动物出没，奶牛猫和布偶猫较为活跃。建议晚间回宿舍时注意观察周围环境。', data_basis: '近7天检测15次' },
      { location_id: 4, location_name: '操场', count: 12, suggestion_text: '请留意周围', suggestion_content: '操场区域近7天检测到12次动物出没，黄狗和柴犬活跃。建议晨跑和晚间锻炼时注意安全，不要单独在操场逗留。', data_basis: '近7天检测12次' },
      { location_id: 3, location_name: '图书馆', count: 8, suggestion_text: '偶有出没，请保持关注', suggestion_content: '图书馆周边近7天检测到8次动物出没，布偶猫和暹罗猫偶有出现。保持关注即可，不需过度担心。', data_basis: '近7天检测8次' },
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

export async function mockGetBreedStats() {
  await delay(200)
  const stats = computeBreedStats()
  return { stats }
}

export async function mockGetCalendar(month) {
  await delay(400)
  // 从 detections 聚合：每天有哪些地点+品种
  const dayMap = {}
  detections.forEach(d => {
    if (d.total_animals === 0) return
    const day = dayOf(d.detect_time)
    if (!day.startsWith(month)) return
    if (!dayMap[day]) dayMap[day] = {}
    if (!dayMap[day][d.location_name]) dayMap[day][d.location_name] = new Set()
    ;(d.animals || []).forEach(a => dayMap[day][d.location_name].add(a.breed_cn))
  })
  const days = Object.entries(dayMap).map(([date, locs]) => ({
    date,
    has_animals: true,
    locations: Object.entries(locs).map(([name, breeds]) => ({ name, breeds: [...breeds] })),
  }))
  return { month, days }
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
  const breed = formData.get('auto_detect') === 'true' ? '布偶猫' : null
  const photos = formData.getAll('images')
  const images = [catPhoto(Math.floor(Math.random() * 30) + 20)]
  const now = new Date()
  const nowStr = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}T${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:00`
  const item = {
    id,
    images,
    location_name: formData.get('location_id') ? locations.find(l => l.id === parseInt(formData.get('location_id')))?.name || null : null,
    description: formData.get('description') || null,
    nickname: formData.get('nickname') || null,
    breed,
    created_at: nowStr,
    comments: [],
  }
  communityItems.unshift(item)
  return item
}

export async function mockGetCommunity(params = {}) {
  await delay(300)
  let items = [...communityItems]
  if (params.date) {
    items = items.filter(i => i.created_at.startsWith(params.date))
  }
  const page = params.page || 1
  const pageSize = params.page_size || 12
  const total = items.length
  const start = (page - 1) * pageSize
  items = items.slice(start, start + pageSize)
  return { items, total, page: page || 1, page_size: pageSize }
}

export async function mockAddComment(shareId, nickname, text) {
  await delay(200)
  const item = communityItems.find(i => i.id === shareId)
  if (!item) throw { response: { status: 404 } }
  const now = new Date()
  const time = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}T${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:00`
  const comment = { id: Date.now(), nickname: nickname || '匿名', text, time }
  item.comments.push(comment)
  return comment
}
