<template>
  <div class="breeds-page">
    <PublicNav menu-key="breeds" />

    <n-layout-content class="breeds-content">
      <n-spin :show="loading">
        <n-empty v-if="!loading && error" description="数据加载失败，请稍后重试" class="error-state" />
        <template v-else-if="!loading">
          <div class="hero">
            <h1>🐾 校园动物品种百科</h1>
            <p>
              YOLOv8 可识别 <strong>37</strong> 种 · {{ cats.length }} 猫 + {{ dogs.length }} 狗
              &nbsp;|&nbsp; 已监测 <strong class="green">{{ detectedCats + detectedDogs }}</strong> 种
            </p>
          </div>

          <div class="tabs">
            <div class="tab" :class="{ active: activeTab === 'cat' }" @click="activeTab = 'cat'">🐱 猫咪（{{ cats.length }}）</div>
            <div class="tab" :class="{ active: activeTab === 'dog' }" @click="activeTab = 'dog'">🐕 狗狗（{{ dogs.length }}）</div>
          </div>

          <h2 class="sec-title" v-if="activeTab === 'cat'">🐱 猫咪品种</h2>
          <h2 class="sec-title" v-else>🐕 狗狗品种</h2>

          <div class="grid">
            <n-card v-for="b in filteredBreeds" :key="b.key" :bordered="false" class="card" :class="[b.type, { undetected: b.detectCount === 0 }]">
              <div class="card-emoji">{{ b.emoji }}</div>
              <h3>{{ b.name_cn }}</h3>
              <p class="en-name">{{ b.en_display }}</p>
              <div class="badge-row">
                <n-tag v-if="b.detectCount > 0" type="success" size="small" round>📸 监测 {{ b.detectCount }} 次</n-tag>
                <n-tag v-else type="default" size="small" round>🔍 暂未监测到</n-tag>
              </div>
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
import PublicNav from '@/components/PublicNav.vue'
import { getBreedStats } from '@/api/public.js'

const router = useRouter()
const activeTab = ref('cat')
const loading = ref(true)
const breedData = ref({})
const breedStats = ref({})
const error = ref(false)


const catKeys = ['Abyssinian','Bengal','Birman','Bombay','British_Shorthair','Egyptian_Mau','Maine_Coon','Persian','Ragdoll','Russian_Blue','Siamese','Sphynx']
const dogKeys = ['american_bulldog','american_pit_bull_terrier','basset_hound','beagle','boxer','chihuahua','english_cocker_spaniel','english_setter','german_shorthaired','great_pyrenees','havanese','japanese_chin','keeshond','leonberger','miniature_pinscher','newfoundland','pomeranian','pug','saint_bernard','samoyed','scottish_terrier','shiba_inu','staffordshire_bull_terrier','wheaten_terrier','yorkshire_terrier']

function makeBreed(key, type) {
  const info = breedData.value[key] || { name_cn: key, emoji: '🐾', size: '未知', temperament: '', fun_fact: '' }
  const name = info.name_cn
  return { key, type, en_display: key.replace(/_/g, ' '), detectCount: breedStats.value[name] || 0, ...info }
}

function sortBreeds(list) {
  return [...list].sort((a, b) => {
    if (a.detectCount > 0 && b.detectCount === 0) return -1
    if (a.detectCount === 0 && b.detectCount > 0) return 1
    if (a.detectCount > 0) return b.detectCount - a.detectCount
    return a.name_cn.localeCompare(b.name_cn, 'zh')
  })
}

const cats = computed(() => sortBreeds(catKeys.filter(k => breedData.value[k]).map(k => makeBreed(k, 'cat'))))
const dogs = computed(() => sortBreeds(dogKeys.filter(k => breedData.value[k]).map(k => makeBreed(k, 'dog'))))
const filteredBreeds = computed(() => activeTab.value === 'cat' ? cats.value : activeTab.value === 'dog' ? dogs.value : [...cats.value, ...dogs.value])
const detectedCats = computed(() => cats.value.filter(b => b.detectCount > 0).length)
const detectedDogs = computed(() => dogs.value.filter(b => b.detectCount > 0).length)

onMounted(async () => {
  error.value = false
  try {
    const [info, stats] = await Promise.all([
      fetch('/breed_info.json').then(r => r.json()),
      getBreedStats(),
    ])
    breedData.value = info
    breedStats.value = stats.stats || {}
  } catch (e) {
    console.error('加载失败', e)
    error.value = true
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
.green { color: #18a058; }
.tabs { display: flex; justify-content: center; gap: 12px; margin-bottom: 28px; }
.tab { padding: 8px 24px; border-radius: 999px; cursor: pointer; font-size: 14px; font-weight: 600; color: #909399; background: #fff; border: 1px solid #e8e8e8; transition: all 0.2s; }
.tab:hover { color: #7c5ce7; border-color: #d4c4f0; }
.tab.active { background: #7c5ce7; color: #fff; border-color: #7c5ce7; }
.sec-title { font-size: 20px; margin: 0 0 16px; color: #555; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 16px; }
.card { border-radius: 12px; transition: all 0.3s; }
.card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.08); }
.card.cat { border-top: 3px solid #18a058; }
.card.dog { border-top: 3px solid #f0a020; }
.card.undetected { opacity: 0.55; }
.card.undetected:hover { opacity: 0.85; }
.card-emoji { font-size: 48px; text-align: center; }
.card h3 { text-align: center; font-size: 18px; margin: 4px 0 2px; }
.en-name { text-align: center; font-size: 12px; color: #aaa; margin: 0; }
.badge-row { text-align: center; margin: 6px 0; }
.attr { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; font-size: 14px; color: #555; }
.lbl { color: #999; font-size: 13px; min-width: 32px; }
.fact { background: #fef9f0; border-radius: 8px; padding: 10px 12px; margin-top: 8px; font-size: 13px; color: #5d4037; line-height: 1.5; }
</style>
