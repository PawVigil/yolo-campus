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
              @click="openBreedDetail(b)"
              style="cursor:pointer"
            >
              <div class="card-emoji">{{ b.emoji }}</div>
              <h3>{{ b.name_cn }}</h3>
              <p class="en-name">{{ b.en_display }}</p>
              <div class="badge-row">
                <span v-if="b.detectCount > 0" class="badge-detected">监测 {{ b.detectCount }} 次</span>
                <span v-else class="badge-none">监测 0 次</span>
              </div>
              <div class="card-divider"></div>
              <div class="attr"><span class="lbl">体型</span><InkTag variant="mint">{{ b.size }}</InkTag></div>
              <div class="attr"><span class="lbl">性格</span><span class="attr-val">{{ b.temperament }}</span></div>
              <div class="fact">{{ b.fun_fact }}</div>
            </PaperCard>
          </div>
        </template>
      </n-spin>

      <!-- 品种详情弹窗 -->
      <n-modal v-model:show="showDetail" preset="card" :title="detailBreed?.name_cn || '品种详情'" style="max-width: 600px" :mask-closable="true">
        <template v-if="detailBreed">
          <div class="detail-hero">
            <img v-if="detailBreed.image_url" :src="detailBreed.image_url" class="detail-photo" alt="" />
            <div v-else class="detail-photo-placeholder">{{ detailBreed.emoji }}</div>
            <div class="detail-hero-info">
              <div class="detail-emoji">{{ detailBreed.emoji }}</div>
              <h3 class="detail-name">{{ detailBreed.name_cn }}</h3>
              <p class="detail-en">{{ detailBreed.en_display }}</p>
              <span v-if="detailBreed.detectCount > 0" class="badge-detected">监测 {{ detailBreed.detectCount }} 次</span>
              <span v-else class="badge-none">监测 0 次</span>
            </div>
          </div>
          <div class="detail-section" v-if="detailBreed.desc">
            <h4>📖 品种介绍</h4>
            <p>{{ detailBreed.desc }}</p>
          </div>
          <div class="detail-section">
            <h4>📋 基本信息</h4>
            <div class="detail-attrs">
              <div class="detail-attr"><span class="da-lbl">体型</span><span>{{ detailBreed.size }}</span></div>
              <div class="detail-attr"><span class="da-lbl">性格</span><span>{{ detailBreed.temperament }}</span></div>
            </div>
          </div>
          <div class="detail-fact">💡 {{ detailBreed.fun_fact }}</div>
        </template>
      </n-modal>
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

// 品种详情弹窗
const showDetail = ref(false)
const detailBreed = ref(null)

function openBreedDetail(breed) {
  detailBreed.value = breed
  showDetail.value = true
}

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
  contain: layout style;
  content-visibility: auto;
  contain-intrinsic-size: 280px;
}
.breed-card:hover {
  transform: translateY(-2px);
}

/* 未检测到的品种 — 略淡但不灰 */
.breed-card.undetected {
  opacity: 0.65;
  transition: opacity var(--transition-fast), transform var(--transition-fast);
}
.breed-card.undetected:hover {
  opacity: 0.85;
  transform: translateY(-2px);
}

/* 卡片内容 */
.card-emoji { font-size: 48px; text-align: center; }
.breed-card h3 { text-align: center; font-size: 18px; margin: 6px 0 2px; color: var(--color-forest-ink); }
.en-name { text-align: center; font-size: 12px; color: var(--color-pencil-gray); margin: 0 0 4px; }
.badge-row { text-align: center; margin: 8px 0; }
.badge-detected { font-size: 12px; font-weight: 600; color: var(--color-forest-ink); background: var(--surface-highlighter); padding: 3px 12px; border-radius: var(--radius-full); }
.badge-none { font-size: 12px; font-weight: 500; color: #888; background: rgba(0,0,0,0.03); padding: 3px 12px; border-radius: var(--radius-full); }

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

/* 品种详情弹窗 */
.detail-hero { display: flex; gap: 16px; margin-bottom: 16px; align-items: flex-start; }
.detail-photo { width: 200px; height: 160px; object-fit: cover; border-radius: 10px; flex-shrink: 0; }
.detail-photo-placeholder { width: 200px; height: 160px; border-radius: 10px; background: var(--surface-cream); display: flex; align-items: center; justify-content: center; font-size: 64px; flex-shrink: 0; }
.detail-hero-info { flex: 1; }
.detail-emoji { font-size: 36px; }
.detail-name { font-size: 22px; font-weight: 800; color: var(--color-forest-ink); margin: 4px 0; }
.detail-en { font-size: 13px; color: #888; margin: 0 0 8px; }
.detail-section { margin-top: 14px; }
.detail-section h4 { font-size: 14px; font-weight: 700; color: var(--color-forest-ink); margin: 0 0 8px; }
.detail-section p { font-size: 14px; color: #555; line-height: 1.7; margin: 0; max-height: 200px; overflow-y: auto; }
.detail-attrs { display: flex; flex-direction: column; gap: 6px; }
.detail-attr { display: flex; gap: 12px; font-size: 14px; color: var(--color-forest-ink); }
.da-lbl { color: #888; min-width: 36px; }
.detail-fact { background: #FFFBEB; border-radius: 8px; padding: 12px 14px; margin-top: 14px; font-size: 14px; color: #92400E; line-height: 1.6; }
</style>
