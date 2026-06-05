<template>
  <main class="server-page">
    <header class="server-header">
      <div>
        <h1>服务器</h1>
        <p>集中管理 WebDAV、OpenList 与本地媒体源，查看每个资源库的匹配情况。</p>
      </div>
      <n-button type="primary" size="large" class="add-button" @click="showAddModal = true">
        <template #icon>
          <n-icon><AddOutline /></n-icon>
        </template>
        添加数据源
      </n-button>
    </header>

    <section class="library-section">
      <h2>资源库</h2>

      <div class="source-grid">
        <article
          v-for="source in sources"
          :key="source.id"
          class="source-card"
          :class="{ active: source.active }"
          :style="{ '--card-tint': source.tint }"
        >
          <button class="card-menu-button" type="button" @click="toggleMenu(source.id)">
            <n-icon><OptionsOutline /></n-icon>
          </button>

          <div v-if="openedMenu === source.id" class="card-menu">
            <button type="button">
              <n-icon><CreateOutline /></n-icon>
              修改
            </button>
            <button type="button">
              <n-icon><RefreshOutline /></n-icon>
              重扫
            </button>
            <button type="button" class="danger">
              <n-icon><TrashOutline /></n-icon>
              删除
            </button>
          </div>

          <div class="source-main">
            <strong>{{ source.name }}</strong>
            <span>{{ source.type }}</span>
          </div>

          <div class="source-stats">
            <span><b>{{ source.files }}</b> 文件</span>
            <span><b>{{ source.movies }}</b> 电影</span>
            <span><b>{{ source.series }}</b> 剧集</span>
            <span><b>{{ source.anime }}</b> 动漫</span>
            <span><b>{{ source.music }}</b> 音乐</span>
          </div>

          <p class="unmatched">未匹配 {{ source.unmatched }}</p>

          <div class="poster-strip">
            <i v-for="index in 5" :key="index"></i>
          </div>

          <p class="source-path">{{ source.path }}</p>
        </article>
      </div>
    </section>

    <n-modal v-model:show="showAddModal" preset="card" class="source-modal" title="添加数据源">
      <n-form label-placement="top">
        <n-form-item label="数据源名称">
          <n-input v-model:value="sourceForm.name" placeholder="例如：阿里云盘" />
        </n-form-item>
        <n-form-item label="数据源类型">
          <n-select v-model:value="sourceForm.type" :options="sourceTypeOptions" />
        </n-form-item>
        <n-form-item label="资源路径">
          <n-input v-model:value="sourceForm.path" placeholder="WebDAV / OpenList 地址或本地目录" />
        </n-form-item>
        <n-form-item label="主题颜色">
          <div class="tint-options">
            <button
              v-for="tint in tintOptions"
              :key="tint.value"
              type="button"
              :class="{ selected: sourceForm.tint === tint.value }"
              :style="{ background: tint.value }"
              :aria-label="tint.label"
              @click="sourceForm.tint = tint.value"
            ></button>
          </div>
        </n-form-item>
      </n-form>
      <template #footer>
        <div class="modal-actions">
          <n-button secondary @click="showAddModal = false">取消</n-button>
          <n-button type="primary" class="add-button" :disabled="!canSubmitSource" @click="addSource">
            添加
          </n-button>
        </div>
      </template>
    </n-modal>
  </main>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import {
  AddOutline,
  CreateOutline,
  OptionsOutline,
  RefreshOutline,
  TrashOutline
} from '@vicons/ionicons5'

const openedMenu = ref('')
const showAddModal = ref(false)

const sources = ref([
  {
    id: 'webdav-kui',
    name: '夸克',
    type: 'WebDAV',
    files: 1497,
    movies: 0,
    series: 0,
    anime: 0,
    music: 0,
    unmatched: 0,
    path: 'http://118.89.62.59:5050/动漫 (+3)',
    tint: 'rgba(111, 110, 142, 0.62)'
  },
  {
    id: 'local-media',
    name: '本地媒体',
    type: '本地存储',
    files: 1497,
    movies: 0,
    series: 0,
    anime: 0,
    music: 0,
    unmatched: 168,
    path: 'D:/Media/Library',
    tint: 'rgba(95, 30, 30, 0.68)',
    active: true
  },
  {
    id: 'baidu-openlist',
    name: '百度',
    type: '内置openlist',
    files: 2345,
    movies: 0,
    series: 0,
    anime: 0,
    music: 0,
    unmatched: 245,
    path: 'OpenList / baidu',
    tint: 'rgba(45, 83, 102, 0.66)'
  },
  {
    id: '115-openlist',
    name: '115网盘',
    type: 'openlist',
    files: 3689,
    movies: 0,
    series: 0,
    anime: 0,
    music: 0,
    unmatched: 312,
    path: 'OpenList / 115',
    tint: 'rgba(91, 47, 116, 0.68)'
  }
])

const sourceForm = reactive({
  name: '',
  type: 'WebDAV',
  path: '',
  tint: 'rgba(111, 110, 142, 0.62)'
})

const sourceTypeOptions = [
  { label: 'WebDAV', value: 'WebDAV' },
  { label: 'OpenList', value: 'openlist' },
  { label: '本地存储', value: '本地存储' }
]

const tintOptions = [
  { label: '灰紫', value: 'rgba(111, 110, 142, 0.62)' },
  { label: '酒红', value: 'rgba(95, 30, 30, 0.68)' },
  { label: '海蓝', value: 'rgba(45, 83, 102, 0.66)' },
  { label: '紫色', value: 'rgba(91, 47, 116, 0.68)' }
]

const canSubmitSource = computed(() => sourceForm.name.trim() && sourceForm.path.trim())

function toggleMenu(id) {
  openedMenu.value = openedMenu.value === id ? '' : id
}

function addSource() {
  if (!canSubmitSource.value) return

  sources.value.unshift({
    id: `source-${Date.now()}`,
    name: sourceForm.name.trim(),
    type: sourceForm.type,
    files: 0,
    movies: 0,
    series: 0,
    anime: 0,
    music: 0,
    unmatched: 0,
    path: sourceForm.path.trim(),
    tint: sourceForm.tint,
    active: false
  })

  sourceForm.name = ''
  sourceForm.type = 'WebDAV'
  sourceForm.path = ''
  sourceForm.tint = tintOptions[0].value
  showAddModal.value = false
}
</script>

<style scoped>
.server-page {
  min-height: 100%;
  padding: 34px;
  box-sizing: border-box;
  color: #f7f9ff;
  background: #1b1b1c;
}

.server-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 30px;
}

.server-header h1 {
  margin: 0;
  color: #ffffff;
  font-size: 30px;
  line-height: 1.2;
}

.server-header p {
  margin: 8px 0 0;
  color: #8f96a4;
}

.add-button {
  min-width: 136px;
  background: #2f6df6;
}

:global(.source-modal) {
  width: min(420px, calc(100vw - 48px)) !important;
}

:global(.source-modal .n-card-header) {
  padding: 18px 20px 8px;
}

:global(.source-modal .n-card__content) {
  padding: 12px 20px 4px;
}

:global(.source-modal .n-card__footer) {
  padding: 12px 20px 18px;
}

.library-section h2 {
  margin: 0 0 18px;
  color: #ffffff;
  font-size: 26px;
}

.source-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  max-width: 1180px;
}

.source-card {
  position: relative;
  min-height: 194px;
  padding: 18px 16px;
  overflow: visible;
  border: 1px solid transparent;
  border-radius: 8px;
  background:
    linear-gradient(135deg, var(--card-tint), color-mix(in srgb, var(--card-tint) 52%, #171719));
  box-shadow: 0 18px 42px rgba(0, 0, 0, 0.2);
}

.source-card.active {
  border-color: #2f6df6;
  box-shadow: 0 0 0 1px rgba(47, 109, 246, 0.28), 0 18px 42px rgba(0, 0, 0, 0.26);
}

.card-menu-button {
  position: absolute;
  top: 16px;
  right: 16px;
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border: 0;
  border-radius: 6px;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.13);
  cursor: pointer;
}

.card-menu {
  position: absolute;
  z-index: 5;
  top: 44px;
  right: 12px;
  width: 152px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  background: #0f1017;
  box-shadow: 0 18px 44px rgba(0, 0, 0, 0.34);
}

.card-menu button {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  height: 38px;
  padding: 0 14px;
  border: 0;
  color: #f4f6fb;
  background: transparent;
  cursor: pointer;
}

.card-menu button:hover {
  background: rgba(255, 255, 255, 0.07);
}

.card-menu .danger {
  color: #ff5757;
}

.source-main {
  padding-right: 40px;
}

.source-main strong {
  display: block;
  color: #ffffff;
  font-size: 17px;
  line-height: 1.2;
}

.source-main span,
.source-path,
.unmatched {
  color: rgba(226, 231, 242, 0.62);
  font-size: 12px;
}

.source-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 14px 0 8px;
  color: #ffffff;
  font-size: 12px;
}

.source-stats b {
  margin-right: 3px;
  color: #ffffff;
}

.unmatched {
  margin: 0 0 16px;
}

.poster-strip {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
  margin-bottom: 16px;
}

.poster-strip i {
  display: block;
  height: 56px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.13);
}

.source-path {
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tint-options {
  display: flex;
  gap: 10px;
}

.tint-options button {
  width: 34px;
  height: 34px;
  border: 2px solid transparent;
  border-radius: 10px;
  cursor: pointer;
}

.tint-options button.selected {
  border-color: #69f0c6;
  box-shadow: 0 0 0 3px rgba(105, 240, 198, 0.14);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
