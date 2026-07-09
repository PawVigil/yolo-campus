<template>
  <div class="breeds-page">
    <PublicNav menu-key="breeds" />

    <n-layout-content class="breeds-content">
      <n-spin :show="loading">
        <n-empty v-if="!loading && error" description="数据加载失败 — 请检查网络连接后刷新页面" class="error-state" :show-icon="false" />
        <template v-else-if="!loading">
          <div class="hero">
            <h1>校园动物品种百科</h1>
            <p>
              YOLOv8 可识别 <strong>37</strong> 种 · {{ cats.length }} 猫 + {{ dogs.length }} 狗
              &nbsp;|&nbsp; 已监测 <strong class="green">{{ detectedCats + detectedDogs }}</strong> 种
            </p>
          </div>

          <div class="tabs">
            <div class="tab" :class="{ active: activeTab === 'cat' }" @click="activeTab = 'cat'">猫咪（{{ cats.length }}）</div>
            <div class="tab" :class="{ active: activeTab === 'dog' }" @click="activeTab = 'dog'">狗狗（{{ dogs.length }}）</div>
          </div>

          <h2 class="sec-title" v-if="activeTab === 'cat'">猫咪品种</h2>
          <h2 class="sec-title" v-else>狗狗品种</h2>

          <div class="grid">
            <PaperCard
              v-for="b in filteredBreeds"
              :key="b.key"
              :stripe="b.detectCount > 0 ? (b.type === 'cat' ? 'mint' : 'sand') : 'none'"
              :class="['breed-card', b.type, { undetected: b.detectCount === 0 }]"
            >
              <div class="card-emoji">{{ b.emoji }}</div>
              <h3>{{ b.name_cn }}</h3>
              <p class="en-name">{{ b.en_display }}</p>
              <div class="badge-row">
                <InkTag v-if="b.detectCount > 0" variant="ink">监测 {{ b.detectCount }} 次</InkTag>
                <InkTag v-else variant="ghost">暂未监测到</InkTag>
              </div>
              <div class="card-divider"></div>
              <div class="attr"><span class="lbl">体型</span><InkTag variant="mint">{{ b.size }}</InkTag></div>
              <div class="attr"><span class="lbl">性格</span><span class="attr-val">{{ b.temperament }}</span></div>
              <div class="fact">{{ b.fun_fact }}</div>
            </PaperCard>
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
import PaperCard from '@/components/PaperCard.vue'
import InkTag from '@/components/InkTag.vue'
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
.breeds-page { min-height: 100vh; background: var(--color-cream-paper); }
.breeds-content { max-width: 1300px; margin: 0 auto; padding: 24px 20px 60px; }
.hero { text-align: left; padding: 40px 20px; background: var(--color-cream-paper); border-radius: var(--radius-card); margin-bottom: 24px; border: 1px solid var(--color-pencil-gray); }
.hero h1 { font-size: 32px; color: var(--color-forest-ink); margin: 0 0 8px; }
.hero p { color: var(--color-whisper-gray); margin: 0; }
.green { color: var(--color-forest-ink); font-weight: var(--weight-bold); font-family: var(--font-mono); font-feature-settings: 'tnum'; }
.tabs { display: flex; justify-content: flex-start; gap: 12px; margin-bottom: 28px; }
.tab { padding: 8px 24px; border-radius: var(--radius-full); cursor: pointer; font-size: 14px; font-weight: var(--weight-semibold); color: var(--color-forest-ink); background: var(--color-cream-paper); border: 1px solid var(--color-pencil-gray); transition: all var(--transition-fast); }
.tab:hover { border-color: var(--color-forest-ink); }
.tab.active { background: var(--surface-highlighter); color: var(--color-forest-ink); border-color: var(--surface-highlighter); }
.sec-title { font-size: 20px; margin: 0 0 16px; color: var(--color-forest-ink); }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 16px; }

/* 品种卡片 — PaperCard 基础上微调 */
.breed-card {
  transition: transform var(--transition-fast);
}
.breed-card:hover {
  transform: translateY(-2px);
}

/* 未检测到的品种 — 虚线褪色 */
.breed-card.undetected {
  background: transparent !important;
  border: 1.5px dashed var(--color-pencil-gray) !important;
  border-radius: 4px 12px 12px 4px !important;
  box-shadow: none !important;
}
.breed-card.undetected::before { display: none; }
.breed-card.undetected:hover {
  border-color: var(--color-forest-ink) !important;
  background: rgba(26, 51, 0, 0.02) !important;
}
.breed-card.undetected .card-emoji { opacity: 0.35; filter: grayscale(1); }
.breed-card.undetected h3 { color: var(--color-pencil-gray); }
.breed-card.undetected .en-name { color: var(--color-whisper-gray); }
.breed-card.undetected .badge-row,
.breed-card.undetected .attr,
.breed-card.undetected .fact { display: none; }

/* 卡片内容 */
.card-emoji { font-size: 48px; text-align: center; }
.breed-card h3 { text-align: center; font-size: 18px; margin: 6px 0 2px; color: var(--color-forest-ink); }
.en-name { text-align: center; font-size: 12px; color: var(--color-pencil-gray); margin: 0 0 4px; }
.badge-row { text-align: center; margin: 8px 0; }

/* 自定义分割线 */
.card-divider {
  height: 1px;
  background: var(--color-whisper-gray);
  margin: 10px 0;
}

.attr { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; font-size: 14px; color: var(--color-forest-ink); }
.lbl { color: var(--color-whisper-gray); font-size: 13px; min-width: 36px; }
.attr-val { font-size: 14px; color: var(--color-forest-ink); }
.fact { background: rgba(26, 51, 0, 0.03); border-radius: 6px; padding: 10px 12px; margin-top: 10px; font-size: 13px; color: var(--color-forest-ink); line-height: 1.5; }
</style>
