<template>
  <main class="history-page">
    <section class="history-header">
      <div>
        <span class="page-kicker">WATCH HISTORY</span>
        <h1>历史记录</h1>
        <p>记录最近观看的内容和进度，随时回到刚才暂停的位置。</p>
      </div>
      <n-button secondary round class="clear-button">
        <template #icon>
          <n-icon><TrashOutline /></n-icon>
        </template>
        清除记录
      </n-button>
    </section>

    <section class="continue-panel">
      <div class="continue-cover" :style="{ backgroundImage: `url(${continueMovie.cover})` }"></div>
      <div class="continue-copy">
        <n-tag round :bordered="false" class="continue-tag">继续观看</n-tag>
        <h2>{{ continueMovie.title }}</h2>
        <p>{{ continueMovie.meta }}</p>
        <div class="progress-track">
          <span :style="{ width: `${continueMovie.progress}%` }"></span>
        </div>
        <div class="continue-footer">
          <span>已观看 {{ continueMovie.progress }}%</span>
          <n-button type="primary" class="play-button">
            <template #icon>
              <n-icon><Play /></n-icon>
            </template>
            继续播放
          </n-button>
        </div>
      </div>
    </section>

    <section v-for="group in historyGroups" :key="group.title" class="history-group">
      <header>
        <h2>{{ group.title }}</h2>
        <span>{{ group.items.length }} 条记录</span>
      </header>

      <article v-for="item in group.items" :key="item.id" class="history-item">
        <div class="item-cover" :style="{ backgroundImage: `url(${item.cover})` }"></div>
        <div class="item-main">
          <div class="item-title-row">
            <div>
              <strong>{{ item.title }}</strong>
              <span>{{ item.episode }} / {{ item.source }}</span>
            </div>
            <time>{{ item.time }}</time>
          </div>
          <div class="progress-track compact">
            <span :style="{ width: `${item.progress}%` }"></span>
          </div>
          <div class="item-footer">
            <span>看到 {{ item.progress }}%</span>
            <div>
              <n-button size="small" type="primary" class="small-play">继续</n-button>
              <n-button size="small" secondary class="small-remove">移除</n-button>
            </div>
          </div>
        </div>
      </article>
    </section>
  </main>
</template>

<script setup>
import { Play, TrashOutline } from '@vicons/ionicons5'

const continueMovie = {
  title: '夜航信号',
  meta: '电影 / OpenList / 128 分钟',
  progress: 68,
  cover: 'https://images.unsplash.com/photo-1519608487953-e999c86e7455?auto=format&fit=crop&w=900&q=85'
}

const historyGroups = [
  {
    title: '今天',
    items: [
      {
        id: 'h1',
        title: '夜航信号',
        episode: '01:24:18',
        source: 'OpenList',
        time: '21:40',
        progress: 68,
        cover: 'https://images.unsplash.com/photo-1519608487953-e999c86e7455?auto=format&fit=crop&w=480&q=85'
      },
      {
        id: 'h2',
        title: '雪境来信',
        episode: '第 4 集',
        source: 'WebDAV',
        time: '18:12',
        progress: 42,
        cover: 'https://images.unsplash.com/photo-1541961017774-22349e4a1262?auto=format&fit=crop&w=480&q=85'
      }
    ]
  },
  {
    title: '本周',
    items: [
      {
        id: 'h3',
        title: '城市回声',
        episode: '第 8 集',
        source: '本地',
        time: '周三 22:08',
        progress: 91,
        cover: 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?auto=format&fit=crop&w=480&q=85'
      },
      {
        id: 'h4',
        title: '旅途的终点',
        episode: '第 2 集',
        source: 'WebDAV',
        time: '周一 20:31',
        progress: 23,
        cover: 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=480&q=85'
      }
    ]
  }
]
</script>

<style scoped>
.history-page {
  min-height: 100%;
  padding: 32px;
  box-sizing: border-box;
  color: #f6f8ff;
  background:
    radial-gradient(circle at 80% 0%, rgba(105, 240, 198, 0.1), transparent 34%),
    #050b16;
}

.history-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 24px;
}

.page-kicker {
  color: #69f0c6;
  font-size: 12px;
  font-weight: 800;
}

.history-header h1 {
  margin: 8px 0 10px;
  font-size: 42px;
  line-height: 1.1;
}

.history-header p {
  margin: 0;
  color: #98a4b8;
}

.clear-button,
.small-remove {
  color: #f7f9ff;
  background: rgba(9, 14, 24, 0.62);
}

.continue-panel {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 28px;
  margin-bottom: 30px;
  padding: 18px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(17, 25, 42, 0.82), rgba(7, 12, 22, 0.78));
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.34);
}

.continue-cover {
  min-height: 220px;
  border-radius: 12px;
  background-position: center;
  background-size: cover;
}

.continue-copy {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.continue-tag {
  width: fit-content;
  color: #06121a;
  background: linear-gradient(135deg, #69f0c6, #32c6ff);
}

.continue-copy h2 {
  margin: 14px 0 8px;
  font-size: 34px;
}

.continue-copy p {
  margin: 0 0 24px;
  color: #a8b2c3;
}

.progress-track {
  width: 100%;
  height: 8px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.1);
}

.progress-track span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #69f0c6, #32c6ff);
}

.continue-footer,
.item-footer {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  margin-top: 16px;
  color: #9ca8ba;
}

.play-button,
.small-play {
  color: #06121a;
  background: linear-gradient(135deg, #69f0c6, #32c6ff);
}

.history-group {
  margin-top: 26px;
}

.history-group header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.history-group h2 {
  margin: 0;
  font-size: 22px;
}

.history-group header span {
  color: #8793a8;
}

.history-item {
  display: grid;
  grid-template-columns: 132px 1fr;
  gap: 18px;
  padding: 14px;
  margin-bottom: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.045);
}

.item-cover {
  min-height: 92px;
  border-radius: 10px;
  background-position: center;
  background-size: cover;
}

.item-main {
  min-width: 0;
}

.item-title-row {
  display: flex;
  justify-content: space-between;
  gap: 18px;
}

.item-title-row strong {
  display: block;
  color: #fff;
  font-size: 18px;
}

.item-title-row span,
.item-title-row time {
  color: #98a4b8;
}

.compact {
  height: 6px;
  margin-top: 14px;
}

.item-footer div {
  display: flex;
  gap: 8px;
}
</style>
