<template>
  <main class="library-page">
    <n-alert v-if="loadError" type="error" class="home-alert" :bordered="false">
      {{ loadError }}
    </n-alert>

    <section v-if="heroItems.length" class="showcase">
      <n-carousel autoplay draggable dot-type="line" class="hero-carousel">
        <article
          v-for="item in heroItems"
          :key="item.id"
          class="hero-slide"
          :style="{ backgroundImage: `url(${item.backdrop})` }"
        >
          <div class="hero-mask"></div>
          <div class="hero-copy">
            <h1>{{ item.title }}</h1>
            <div class="tag-row">
              <n-tag v-for="tag in item.tags" :key="tag" round class="soft-tag">{{ tag }}</n-tag>
            </div>
            <div class="hero-actions">
              <n-button type="primary" size="large" class="play-button" @click="playMovie(item.id)">
                <template #icon>
                  <n-icon><Play /></n-icon>
                </template>
                立即播放
              </n-button>
              <n-button secondary size="large" class="ghost-button" @click="goDetail(item.id)">
                <template #icon>
                  <n-icon><InformationCircleOutline /></n-icon>
                </template>
                查看详情
              </n-button>
            </div>
          </div>

        </article>
      </n-carousel>
    </section>
    <section v-else class="showcase empty-showcase">
      <n-spin v-if="loading" size="large" />
      <n-empty v-else description="暂无海报数据" />
    </section>

    <section class="stats-strip">
      <article v-for="item in libraryStats" :key="item.label" class="stat-card">
        <div class="stat-icon" :class="item.tone">
          <n-icon><component :is="item.icon" /></n-icon>
        </div>
        <div>
          <strong>{{ item.value }}</strong>
          <span>{{ item.label }}</span>
          <small>{{ item.help }}</small>
        </div>
      </article>
    </section>

    <section class="media-section">
      <header class="section-header">
        <div>
          <h2>{{ currentCategoryTitle }}</h2>
          <span>当前更多集中在 {{ currentCategoryLabel }}，共 {{ visibleCards.length }} 个条目。</span>
        </div>
        <n-button secondary round>查看全部</n-button>
      </header>

      <div class="media-rail">
        <article
          v-for="card in visibleCards"
          :key="card.id"
          class="media-card"
          :style="{ backgroundImage: `url(${card.cover})` }"
        >
          <div class="card-tags">
            <n-tag round size="small" class="card-type">{{ card.type }}</n-tag>
            <n-tag round size="small" class="year-tag">{{ card.year }}</n-tag>
          </div>
          <div class="card-footer">
            <strong>{{ card.title }}</strong>
            <div class="card-actions">
              <n-button size="small" class="source-pill">{{ card.source }}</n-button>
              <n-button size="small" type="primary" class="small-play" @click="playMovie(card.id)">播放</n-button>
              <n-button size="small" secondary class="small-save">收藏</n-button>
            </div>
          </div>
        </article>
      </div>
      <n-empty v-if="!loading && !visibleCards.length" description="暂无影视条目" class="media-empty" />
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  CloudOutline,
  FolderOpenOutline,
  InformationCircleOutline,
  Play,
  Star,
  VideocamOutline
} from '@vicons/ionicons5'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const loadError = ref('')
const homeData = ref({
  stats: {
    total: 0,
    remote: 0,
    local: 0,
    favorite: 0
  },
  hero: [],
  items: []
})

const categoryLabels = {
  all: '全部',
  movie: '电影',
  series: '剧集',
  anime: '动漫',
  variety: '综艺',
  music: '音乐',
  shorts: '短片',
  documentary: '纪录'
}

const sourceTypeLabels = {
  webdav: 'WebDAV',
  openlist: 'OpenList',
  local: '本地'
}

const currentCategory = computed(() => route.query.category || 'all')
const currentCategoryLabel = computed(() => categoryLabels[currentCategory.value] || '全部')
const currentCategoryTitle = computed(() => `${currentCategoryLabel.value}  ${visibleCards.value.length}`)
const heroItems = computed(() => homeData.value.hero.map(normalizeHeroItem).filter((item) => item.backdrop))
const visibleCards = computed(() => homeData.value.items.map(normalizeMovieCard).filter((item) => item.cover))
const libraryStats = computed(() => {
  const stats = homeData.value.stats || {}
  return [
    { label: '全部条目', value: stats.total || 0, help: '当前片库总量', icon: VideocamOutline, tone: 'violet' },
    { label: '远程条目', value: stats.remote || 0, help: '远程媒体源', icon: CloudOutline, tone: 'blue' },
    { label: '本地条目', value: stats.local || 0, help: '本地连接目录', icon: FolderOpenOutline, tone: 'orange' },
    { label: '收藏条目', value: stats.favorite || 0, help: '随时可重看', icon: Star, tone: 'indigo' }
  ]
})

onMounted(fetchHomeData)
watch(currentCategory, fetchHomeData)

function goDetail(id) {
  router.push({ name: 'MovieDetail', params: { id } })
}

async function fetchHomeData() {
  loading.value = true
  loadError.value = ''

  try {
    const params = new URLSearchParams({ limit: '12' })
    if (currentCategory.value !== 'all') {
      params.set('category', currentCategory.value)
    }

    const response = await fetch(`/api/movies/home?${params.toString()}`)
    if (!response.ok) {
      throw new Error(`接口请求失败：${response.status}`)
    }

    const result = await response.json()
    if (result.code !== 0) {
      throw new Error(result.message || '接口返回错误')
    }

    homeData.value = {
      stats: result.data?.stats || homeData.value.stats,
      hero: Array.isArray(result.data?.hero) ? result.data.hero : [],
      items: Array.isArray(result.data?.items) ? result.data.items : []
    }
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : '首页数据加载失败'
    homeData.value = {
      stats: {
        total: 0,
        remote: 0,
        local: 0,
        favorite: 0
      },
      hero: [],
      items: []
    }
  } finally {
    loading.value = false
  }
}

async function playMovie(id) {
  try {
    const response = await fetch(`/api/movies/${id}/play`)
    if (!response.ok) {
      throw new Error(`播放地址请求失败：${response.status}`)
    }

    const result = await response.json()
    if (result.code !== 0 || !result.data?.playUrl) {
      throw new Error(result.message || '暂无播放地址')
    }

    window.open(result.data.playUrl, '_blank')
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : '播放失败'
  }
}

function normalizeHeroItem(item) {
  const categoryLabel = categoryLabels[item.category] || item.category || '影视'
  const sourceName = item.sourceName || sourceTypeLabels[item.sourceType] || item.sourceType || '未知来源'
  return {
    id: item.id,
    title: item.title || '未命名影视',
    backdrop: item.backdropUrl,
    tags: Array.isArray(item.tags) && item.tags.length
      ? item.tags
      : [categoryLabel, item.year, sourceName, item.durationText].filter(Boolean)
  }
}

function normalizeMovieCard(item) {
  return {
    id: item.id,
    category: item.category,
    title: item.title || '未命名影视',
    type: categoryLabels[item.category] || item.category || '影视',
    year: item.year || '',
    source: item.sourceName || sourceTypeLabels[item.sourceType] || item.sourceType || '未知',
    cover: item.coverUrl
  }
}
</script>

<style>
.library-page {
  min-height: 100%;
  padding: 28px 38px 38px;
  box-sizing: border-box;
  color: #f6f8ff;
  background: #050b16;
}

.showcase {
  position: relative;
  min-height: 100vh;
  margin: -28px -38px 0;
  overflow: hidden;
}

.home-alert {
  position: fixed;
  z-index: 20;
  top: 18px;
  right: 18px;
  max-width: 420px;
}

.empty-showcase {
  display: grid;
  place-items: center;
  background:
    radial-gradient(circle at 50% 28%, rgba(50, 198, 255, 0.12), transparent 34%),
    #050b16;
}

.library-page .n-button {
  border-radius: 14px;
}

.library-page .n-button--round {
  border-radius: 999px;
}

.hero-carousel {
  display: block;
  height: 100vh !important;
  min-height: 720px;
}

.library-page .hero-carousel .n-carousel {
  height: 100%;
}

.library-page .hero-carousel .n-carousel__dots {
  left: 64px;
  right: auto;
  bottom: 228px;
  transform: none;
  z-index: 7;
}

.library-page .hero-carousel .n-carousel__dot {
  background-color: rgba(255, 255, 255, 0.38);
}

.library-page .hero-carousel .n-carousel__dot.n-carousel__dot--active {
  background-color: #ff8a2a;
}

.library-page .hero-carousel .n-carousel__arrow {
  background: rgba(255, 255, 255, 0.16);
  backdrop-filter: blur(12px);
}

.library-page .hero-carousel .n-carousel__slides,
.library-page .hero-carousel .n-carousel__slide {
  height: 100% !important;
}

.hero-slide {
  position: relative;
  display: block;
  height: 100%;
  min-height: 720px;
  overflow: hidden;
  background-position: center;
  background-size: cover;
}

.hero-mask {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(90deg, rgba(4, 9, 18, 0.96) 0%, rgba(4, 9, 18, 0.58) 40%, rgba(4, 9, 18, 0.18) 70%),
    linear-gradient(0deg, rgba(5, 11, 22, 1) 0%, rgba(5, 11, 22, 0.24) 44%, rgba(5, 11, 22, 0.36) 100%);
}

.hero-copy {
  position: absolute;
  z-index: 4;
  left: 64px !important;
  bottom: 282px !important;
  max-width: 560px;
}

.hero-copy h1 {
  margin: 0 0 14px;
  color: #fff;
  font-size: clamp(36px, 4.2vw, 62px);
  line-height: 1.08;
  letter-spacing: 0;
  text-shadow: 0 12px 36px rgba(0, 0, 0, 0.54);
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 9px;
  margin-bottom: 20px;
}

.soft-tag {
  color: #e8ecf6;
  background: rgba(8, 14, 26, 0.42);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.16);
}

.hero-actions {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
}

.play-button {
  min-width: 142px;
  border: 0;
  color: #06121a;
  background: linear-gradient(135deg, #69f0c6, #32c6ff);
  box-shadow: 0 16px 34px rgba(50, 198, 255, 0.24);
}

.ghost-button {
  min-width: 142px;
  color: #f7f9ff;
  background: rgba(7, 12, 22, 0.38);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.18);
}

.stats-strip {
  position: relative;
  z-index: 6;
  display: grid !important;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  width: min(1420px, calc(100% - 160px));
  margin: -158px auto 56px;
  padding: 18px 28px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 8px;
  background: rgba(18, 24, 39, 0.58);
  box-shadow: 0 22px 70px rgba(0, 0, 0, 0.36), inset 0 0 80px rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(18px);
}

.stat-card {
  display: flex;
  gap: 16px;
  align-items: center;
  min-width: 0;
  padding: 0 24px;
  border-right: 1px solid rgba(255, 255, 255, 0.18);
}

.stat-card:last-child {
  border-right: 0;
}

.stat-icon {
  display: grid;
  place-items: center;
  flex: 0 0 62px;
  height: 62px;
  border-radius: 8px;
  font-size: 28px;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.16);
}

.stat-icon.violet { color: #bd93ff; background: linear-gradient(135deg, rgba(128, 75, 255, 0.62), rgba(72, 42, 144, 0.54)); }
.stat-icon.blue { color: #b7ccff; background: linear-gradient(135deg, rgba(73, 103, 255, 0.58), rgba(30, 58, 138, 0.5)); }
.stat-icon.orange { color: #ffd09a; background: linear-gradient(135deg, rgba(255, 132, 46, 0.58), rgba(120, 65, 29, 0.5)); }
.stat-icon.indigo { color: #b9b8ff; background: linear-gradient(135deg, rgba(92, 96, 255, 0.58), rgba(39, 45, 119, 0.5)); }

.stat-card strong {
  display: block;
  color: #fff;
  font-size: 26px;
  line-height: 1;
}

.stat-card span {
  display: block;
  margin-top: 4px;
  color: #eef2ff;
  font-size: 15px;
}

.stat-card small {
  display: block;
  margin-top: 3px;
  color: #97a2b9;
  font-size: 12px;
}

.media-section {
  padding-top: 12px;
}

.section-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 14px;
}

.section-header h2 {
  margin: 0 0 5px;
  color: #fff;
  font-size: 20px;
  letter-spacing: 0;
}

.section-header span {
  color: #929cb0;
}

.media-rail {
  display: grid !important;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 18px;
}

.media-empty {
  padding: 56px 0;
}

.media-card {
  position: relative;
  display: block;
  min-height: 320px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 8px;
  background-position: center;
  background-size: cover;
  box-shadow: 0 18px 44px rgba(0, 0, 0, 0.3);
}

.media-card::after {
  position: absolute;
  inset: 0;
  content: "";
  background: linear-gradient(0deg, rgba(5, 9, 18, 0.92) 0%, rgba(5, 9, 18, 0.18) 58%);
}

.card-tags {
  position: absolute;
  z-index: 2;
  top: 14px;
  left: 14px;
  right: 14px;
  display: flex;
  justify-content: space-between;
}

.card-type {
  color: #e7f9ff;
  background: rgba(15, 31, 47, 0.72);
}

.year-tag {
  color: #fff;
  background: linear-gradient(135deg, #ff9a3d, #ff5f2d);
}

.card-footer {
  position: absolute;
  z-index: 2;
  left: 14px;
  right: 14px;
  bottom: 14px;
}

.card-footer strong {
  display: block;
  margin-bottom: 10px;
  color: #fff;
  font-size: 18px;
}

.card-actions {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
}

.source-pill,
.small-save {
  color: #f8fbff;
  background: rgba(9, 14, 24, 0.62);
}

.small-play {
  color: #06121a;
  background: linear-gradient(135deg, #69f0c6, #32c6ff);
}

@media (max-width: 1180px) {
  .stats-strip {
    width: calc(100% - 48px);
    grid-template-columns: repeat(2, 1fr);
  }

  .stat-card:nth-child(2) {
    border-right: 0;
  }
}

@media (max-width: 760px) {
  .library-page {
    padding: 18px;
  }

  .showcase {
    min-height: 100vh;
    margin: -18px -18px 0;
  }

  .hero-carousel {
    height: 100vh !important;
    min-height: 640px;
  }

  .hero-slide {
    min-height: 640px;
  }

  .hero-copy {
    left: 24px;
    right: 24px;
    bottom: 248px;
  }

  .library-page .hero-carousel .n-carousel__dots {
    left: 24px;
    bottom: 192px;
  }

  .stats-strip {
    grid-template-columns: 1fr;
    width: 100%;
    margin-top: -156px;
    padding: 16px;
  }

  .stat-card {
    padding: 14px 0;
    border-right: 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.12);
  }

  .stat-card:last-child {
    border-bottom: 0;
  }
}
</style>
