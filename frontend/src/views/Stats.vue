<template>
  <main class="stats-page">
    <section class="stats-header">
      <div>
        <span class="page-kicker">VIEWING STATS</span>
        <h1>观影统计</h1>
        <p>用静态仪表盘整理片库消费情况，后续接入真实 API 时可以直接替换数据源。</p>
      </div>
      <n-tag round :bordered="false" class="range-tag">最近 30 天</n-tag>
    </section>

    <section class="metric-grid">
      <article v-for="metric in metrics" :key="metric.label" class="metric-card">
        <div class="metric-icon" :class="metric.tone">
          <n-icon><component :is="metric.icon" /></n-icon>
        </div>
        <div>
          <strong>{{ metric.value }}</strong>
          <span>{{ metric.label }}</span>
          <small>{{ metric.tip }}</small>
        </div>
      </article>
    </section>

    <section class="dashboard-grid">
      <article class="chart-panel">
        <header>
          <h2>分类分布</h2>
          <span>按条目数量</span>
        </header>
        <div class="distribution-list">
          <div v-for="item in categoryDistribution" :key="item.label" class="distribution-row">
            <div class="row-head">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </div>
            <div class="bar-track">
              <span :style="{ width: `${item.percent}%`, background: item.color }"></span>
            </div>
          </div>
        </div>
      </article>

      <article class="chart-panel">
        <header>
          <h2>来源分布</h2>
          <span>远程与本地</span>
        </header>
        <div class="source-stack">
          <div v-for="item in sourceDistribution" :key="item.label" :style="{ flex: item.value, background: item.color }">
            <span>{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
        <div class="source-legend">
          <span v-for="item in sourceDistribution" :key="item.label">
            <i :style="{ background: item.color }"></i>{{ item.label }}
          </span>
        </div>
      </article>
    </section>

    <section class="trend-panel">
      <header>
        <div>
          <h2>最近 7 天观影趋势</h2>
          <span>单位：分钟</span>
        </div>
        <strong>本周 615 分钟</strong>
      </header>
      <div class="trend-chart">
        <div v-for="item in weeklyTrend" :key="item.day" class="trend-column">
          <div class="trend-bar" :style="{ height: `${item.percent}%` }">
            <span>{{ item.minutes }}</span>
          </div>
          <small>{{ item.day }}</small>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import {
  BarChartOutline,
  FilmOutline,
  HeartOutline,
  TimeOutline
} from '@vicons/ionicons5'

const metrics = [
  { label: '总观影数', value: 128, tip: '累计完成条目', icon: FilmOutline, tone: 'cyan' },
  { label: '总时长', value: '312h', tip: '折合 13 天', icon: TimeOutline, tone: 'violet' },
  { label: '本月观影', value: 17, tip: '较上月 +24%', icon: BarChartOutline, tone: 'blue' },
  { label: '收藏数', value: 18, tip: '反复观看清单', icon: HeartOutline, tone: 'rose' }
]

const categoryDistribution = [
  { label: '电影', value: 42, percent: 88, color: 'linear-gradient(90deg, #69f0c6, #32c6ff)' },
  { label: '剧集', value: 36, percent: 76, color: 'linear-gradient(90deg, #8b7dff, #32c6ff)' },
  { label: '动漫', value: 31, percent: 66, color: 'linear-gradient(90deg, #ffb86b, #ff6a9a)' },
  { label: '纪录', value: 12, percent: 28, color: 'linear-gradient(90deg, #b7ccff, #7c5cff)' },
  { label: '综艺', value: 7, percent: 18, color: 'linear-gradient(90deg, #72e4a0, #d6f779)' }
]

const sourceDistribution = [
  { label: 'WebDAV', value: 62, color: 'linear-gradient(180deg, #69f0c6, #24a7ff)' },
  { label: 'OpenList', value: 44, color: 'linear-gradient(180deg, #8b7dff, #5a4ad8)' },
  { label: '本地', value: 22, color: 'linear-gradient(180deg, #ffb86b, #ff7a22)' }
]

const weeklyTrend = [
  { day: '周一', minutes: 45, percent: 30 },
  { day: '周二', minutes: 90, percent: 60 },
  { day: '周三', minutes: 120, percent: 80 },
  { day: '周四', minutes: 75, percent: 50 },
  { day: '周五', minutes: 160, percent: 100 },
  { day: '周六', minutes: 85, percent: 56 },
  { day: '周日', minutes: 40, percent: 26 }
]
</script>

<style scoped>
.stats-page {
  min-height: 100%;
  padding: 32px;
  box-sizing: border-box;
  color: #f6f8ff;
  background:
    radial-gradient(circle at 12% 0%, rgba(139, 125, 255, 0.13), transparent 34%),
    #050b16;
}

.stats-header {
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

.stats-header h1 {
  margin: 8px 0 10px;
  font-size: 42px;
  line-height: 1.1;
}

.stats-header p {
  margin: 0;
  color: #98a4b8;
}

.range-tag {
  color: #06121a;
  background: linear-gradient(135deg, #69f0c6, #32c6ff);
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 18px;
}

.metric-card,
.chart-panel,
.trend-panel {
  border: 1px solid rgba(255, 255, 255, 0.11);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.045);
  box-shadow: 0 22px 58px rgba(0, 0, 0, 0.28), inset 0 0 80px rgba(255, 255, 255, 0.03);
}

.metric-card {
  display: flex;
  gap: 16px;
  align-items: center;
  padding: 20px;
}

.metric-icon {
  display: grid;
  place-items: center;
  flex: 0 0 58px;
  height: 58px;
  border-radius: 14px;
  font-size: 28px;
}

.metric-icon.cyan { color: #06121a; background: linear-gradient(135deg, #69f0c6, #32c6ff); }
.metric-icon.violet { color: #ded8ff; background: linear-gradient(135deg, #7c5cff, #3e2e91); }
.metric-icon.blue { color: #d8e6ff; background: linear-gradient(135deg, #32c6ff, #2458d8); }
.metric-icon.rose { color: #ffe3ef; background: linear-gradient(135deg, #ff6a9a, #7c5cff); }

.metric-card strong {
  display: block;
  font-size: 28px;
  line-height: 1;
}

.metric-card span {
  display: block;
  margin-top: 5px;
  color: #eef2ff;
}

.metric-card small {
  display: block;
  margin-top: 4px;
  color: #8d98aa;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 18px;
}

.chart-panel,
.trend-panel {
  padding: 22px;
}

.chart-panel header,
.trend-panel header {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-start;
  margin-bottom: 22px;
}

.chart-panel h2,
.trend-panel h2 {
  margin: 0 0 5px;
  font-size: 22px;
}

.chart-panel header span,
.trend-panel header span {
  color: #8d98aa;
}

.distribution-list {
  display: grid;
  gap: 18px;
}

.row-head {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.bar-track {
  height: 10px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
}

.bar-track span {
  display: block;
  height: 100%;
  border-radius: inherit;
}

.source-stack {
  display: flex;
  height: 220px;
  overflow: hidden;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.08);
}

.source-stack div {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  min-width: 0;
  padding: 16px 12px;
  box-sizing: border-box;
}

.source-stack span,
.source-stack strong {
  color: #fff;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.36);
}

.source-legend {
  display: flex;
  gap: 16px;
  margin-top: 16px;
  color: #a8b2c3;
}

.source-legend i {
  display: inline-block;
  width: 10px;
  height: 10px;
  margin-right: 6px;
  border-radius: 50%;
}

.trend-panel {
  margin-top: 18px;
}

.trend-panel header strong {
  color: #69f0c6;
}

.trend-chart {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 14px;
  height: 260px;
  align-items: end;
}

.trend-column {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  gap: 10px;
}

.trend-bar {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  width: 100%;
  min-height: 30px;
  border-radius: 14px 14px 8px 8px;
  background: linear-gradient(180deg, #69f0c6, #32c6ff);
  box-shadow: 0 16px 34px rgba(50, 198, 255, 0.18);
}

.trend-bar span {
  margin-top: 8px;
  color: #06121a;
  font-weight: 800;
}

.trend-column small {
  color: #9ca8ba;
}
</style>
