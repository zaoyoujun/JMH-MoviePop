<template>
  <main class="favorites-page">
    <section class="favorites-hero">
      <div>
        <span class="page-kicker">FAVORITES</span>
        <h1>收藏片库</h1>
        <p>把想反复看的电影、剧集和动漫收进这里，下一次打开就能直接续上。</p>
      </div>
      <div class="favorite-summary">
        <article v-for="item in summary" :key="item.label">
          <strong>{{ item.value }}</strong>
          <span>{{ item.label }}</span>
        </article>
      </div>
    </section>

    <section class="filter-row">
      <n-button v-for="filter in filters" :key="filter" secondary round>{{ filter }}</n-button>
    </section>

    <section class="favorite-grid">
      <article
        v-for="movie in favoriteMovies"
        :key="movie.id"
        class="media-card"
        :style="{ backgroundImage: `url(${movie.cover})` }"
      >
        <div class="card-tags">
          <n-tag round size="small" class="card-type">{{ movie.type }}</n-tag>
          <n-tag round size="small" class="year-tag">{{ movie.year }}</n-tag>
        </div>
        <div class="card-footer">
          <strong>{{ movie.title }}</strong>
          <div class="card-actions">
            <n-button size="small" class="source-pill">{{ movie.source }}</n-button>
            <n-button size="small" type="primary" class="small-play">
              <template #icon>
                <n-icon><Play /></n-icon>
              </template>
              播放
            </n-button>
            <n-button size="small" secondary class="small-save">
              <template #icon>
                <n-icon><Heart /></n-icon>
              </template>
              已收藏
            </n-button>
          </div>
        </div>
      </article>
    </section>
  </main>
</template>

<script setup>
import { InformationCircleOutline, Play, Heart } from '@vicons/ionicons5'

const summary = [
  { label: '全部收藏', value: 18 },
  { label: '本周新增', value: 5 },
  { label: '待继续', value: 7 }
]

const filters = ['全部', '电影', '剧集', '动漫', 'WebDAV', 'OpenList', '本地']

const favoriteMovies = [
  {
    id: 'snow-letter',
    title: '雪境来信',
    type: '动漫',
    year: 2024,
    source: 'WebDAV',
    savedAt: '06-05',
    cover: 'https://images.unsplash.com/photo-1541961017774-22349e4a1262?auto=format&fit=crop&w=700&q=85'
  },
  {
    id: 'blue-border',
    title: '蓝色边界',
    type: '电影',
    year: 2022,
    source: 'OpenList',
    savedAt: '06-04',
    cover: 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=700&q=85'
  },
  {
    id: 'city-echo',
    title: '城市回声',
    type: '剧集',
    year: 2009,
    source: '本地',
    savedAt: '06-03',
    cover: 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?auto=format&fit=crop&w=700&q=85'
  },
  {
    id: 'summer-club',
    title: '午后的社团',
    type: '动漫',
    year: 2008,
    source: 'WebDAV',
    savedAt: '06-01',
    cover: 'https://images.unsplash.com/photo-1529156069898-49953e39b3ac?auto=format&fit=crop&w=700&q=85'
  },
  {
    id: 'night-signal',
    title: '夜航信号',
    type: '电影',
    year: 2026,
    source: 'OpenList',
    savedAt: '05-30',
    cover: 'https://images.unsplash.com/photo-1519608487953-e999c86e7455?auto=format&fit=crop&w=700&q=85'
  },
  {
    id: 'green-journey',
    title: '旅途的终点',
    type: '动漫',
    year: 2023,
    source: 'WebDAV',
    savedAt: '05-28',
    cover: 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=700&q=85'
  }
]
</script>

<style scoped>
.favorites-page {
  min-height: 100%;
  padding: 32px;
  box-sizing: border-box;
  color: #f6f8ff;
  background:
    radial-gradient(circle at 18% 0%, rgba(50, 198, 255, 0.12), transparent 34%),
    #050b16;
}

.favorites-hero {
  display: flex;
  justify-content: space-between;
  gap: 28px;
  align-items: flex-end;
  padding: 34px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(17, 25, 42, 0.82), rgba(7, 12, 22, 0.78));
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.34);
}

.page-kicker {
  color: #69f0c6;
  font-size: 12px;
  font-weight: 800;
}

.favorites-hero h1 {
  margin: 8px 0 10px;
  font-size: 42px;
  line-height: 1.1;
}

.favorites-hero p {
  max-width: 620px;
  margin: 0;
  color: #98a4b8;
  font-size: 15px;
}

.favorite-summary {
  display: grid;
  grid-template-columns: repeat(3, 120px);
  gap: 12px;
}

.favorite-summary article {
  padding: 16px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.06);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.1);
}

.favorite-summary strong {
  display: block;
  font-size: 28px;
}

.favorite-summary span {
  color: #9ca8ba;
  font-size: 12px;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin: 24px 0;
}

.favorite-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 18px;
}
</style>
