<template>
  <div class="breeds-page">
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

    <n-layout-content class="breeds-content">
      <n-spin :show="loading">
        <template v-if="!loading">
          <!-- Hero -->
          <div class="hero">
            <h1>🐾 校园动物品种百科</h1>
            <p>YOLOv8 可识别 <strong>37</strong> 种猫狗 · {{ cats.length }} 猫 + {{ dogs.length }} 狗</p>
          </div>

          <!-- Tabs -->
          <div class="tabs">
            <div class="tab" :class="{ active: activeTab === 'all' }" @click="activeTab = 'all'">📋 全部（{{ cats.length + dogs.length }}）</div>
            <div class="tab" :class="{ active: activeTab === 'cat' }" @click="activeTab = 'cat'">🐱 猫咪（{{ cats.length }}）</div>
            <div class="tab" :class="{ active: activeTab === 'dog' }" @click="activeTab = 'dog'">🐕 狗狗（{{ dogs.length }}）</div>
          </div>

          <!-- Breed grid -->
          <h2 class="sec-title" v-if="activeTab === 'all'">全部品种</h2>
          <h2 class="sec-title" v-else-if="activeTab === 'cat'">🐱 猫咪品种</h2>
          <h2 class="sec-title" v-else>🐕 狗狗品种</h2>

          <div class="grid">
            <n-card v-for="b in filteredBreeds" :key="b.key" :bordered="false" class="card" :class="b.type">
              <div class="card-emoji">{{ b.emoji }}</div>
              <h3>{{ b.name_cn }}</h3>
              <p class="en-name">{{ b.en_display }}</p>
              <n-divider />
              <div class="attr"><span class="lbl">体型</span><n-tag size="small" round>{{ b.size }}</n-tag></div>
              <div class="attr"><span class="lbl">性格</span>{{ b.temperament }}</div>
              <div class="fact">💡 {{ b.fun_fact }}</div>
            </n-card>
          </div>
        </template>
      </n-spin>
    </n-layout-content>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const activeMenu = ref('breeds')
const activeTab = ref('all')
const loading = ref(true)
const breedData = ref({})

const menuOptions = [
  { label: '🏠 实时大屏', key: 'live' },
  { label: '📅 出没日历', key: 'calendar' },
  { label: '🏆 排行榜', key: 'rankings' },
  { label: '🐱 撸猫指南', key: 'guide' },
  { label: '⚠️ 安全提醒', key: 'safety' },
  { label: '📸 社区分享', key: 'community' },
]

function onMenuChange(key) {
  const map = { live: '/', calendar: '/calendar', rankings: '/rankings', guide: '/guide', safety: '/safety', community: '/community' }
  router.push(map[key])
}

const catKeys = ['Abyssinian','Bengal','Birman','Bombay','British_Shorthair','Egyptian_Mau','Maine_Coon','Persian','Ragdoll','Russian_Blue','Siamese','Sphynx']
const dogKeys = ['american_bulldog','american_pit_bull_terrier','basset_hound','beagle','boxer','chihuahua','english_cocker_spaniel','english_setter','german_shorthaired','great_pyrenees','havanese','japanese_chin','keeshond','leonberger','miniature_pinscher','newfoundland','pomeranian','pug','saint_bernard','samoyed','scottish_terrier','shiba_inu','staffordshire_bull_terrier','wheaten_terrier','yorkshire_terrier']

function makeBreed(key, type) {
  return { key, type, en_display: key.replace(/_/g, ' '), ...breedData.value[key] }
}

const cats = computed(() => catKeys.filter(k => breedData.value[k]).map(k => makeBreed(k, 'cat')))
const dogs = computed(() => dogKeys.filter(k => breedData.value[k]).map(k => makeBreed(k, 'dog')))

const filteredBreeds = computed(() => {
  if (activeTab.value === 'cat') return cats.value
  if (activeTab.value === 'dog') return dogs.value
  return [...cats.value, ...dogs.value]
})

onMounted(async () => {
  try {
    const res = await fetch('/breed_info.json')
    breedData.value = await res.json()
  } catch (e) {
    console.error('加载品种数据失败', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.breeds-page { min-height: 100vh; background: #f5f7fa; }
.public-nav { background: rgba(255,255,255,0.9); backdrop-filter: blur(10px); position: sticky; top: 0; z-index: 100; }
.nav-content { max-width: 1300px; margin: 0 auto; display: flex; align-items: center; padding: 0 20px; height: 56px; }
.nav-brand { display: flex; align-items: center; gap: 8px; cursor: pointer; margin-right: 24px; }
.brand-icon { font-size: 24px; }
.brand-text { font-size: 18px; font-weight: 700; color: #7c5ce7; }
.admin-link { margin-left: auto; }
.breeds-content { max-width: 1300px; margin: 0 auto; padding: 24px 20px 60px; }
.hero { text-align: center; padding: 40px 20px; background: linear-gradient(135deg, #667eea18, #764ba218); border-radius: 16px; margin-bottom: 24px; }
.hero h1 { font-size: 32px; color: #7c5ce7; margin: 0 0 8px; }
.hero p { color: #909399; margin: 0; }

/* Tabs */
.tabs { display: flex; justify-content: center; gap: 12px; margin-bottom: 28px; }
.tab { padding: 8px 24px; border-radius: 999px; cursor: pointer; font-size: 14px; font-weight: 600; color: #909399; background: #fff; border: 1px solid #e8e8e8; transition: all 0.2s; }
.tab:hover { color: #7c5ce7; border-color: #d4c4f0; }
.tab.active { background: #7c5ce7; color: #fff; border-color: #7c5ce7; }

.sec-title { font-size: 22px; margin: 0 0 16px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 16px; }
.card { border-radius: 12px; transition: all 0.3s; }
.card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.08); }
.card.cat { border-top: 3px solid #18a058; }
.card.dog { border-top: 3px solid #f0a020; }
.card-emoji { font-size: 48px; text-align: center; }
.card h3 { text-align: center; font-size: 18px; margin: 4px 0 2px; }
.en-name { text-align: center; font-size: 12px; color: #aaa; margin: 0 0 8px; }
.attr { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; font-size: 14px; color: #555; }
.lbl { color: #999; font-size: 13px; min-width: 32px; }
.fact { background: #fef9f0; border-radius: 8px; padding: 10px 12px; margin-top: 8px; font-size: 13px; color: #5d4037; line-height: 1.5; }
</style>
