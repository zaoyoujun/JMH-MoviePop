<template>
  <n-layout has-sider class="movie-shell">
    <n-layout-sider
      bordered
      collapse-mode="width"
      :collapsed="collapsed"
      :collapsed-width="76"
      :width="232"
      :native-scrollbar="false"
      class="movie-sider"
    >
      <div class="sider-frame">
        <div class="brand-bar">
          <div class="brand-mark">M</div>
          <div v-if="!collapsed" class="brand-copy">
            <strong>MoviePop</strong>
            <span>私人片库</span>
          </div>
          <n-button quaternary circle size="small" class="collapse-btn" @click="collapsed = !collapsed">
            <template #icon>
              <n-icon>
                <ChevronBackOutline v-if="!collapsed" />
                <ChevronForwardOutline v-else />
              </n-icon>
            </template>
          </n-button>
        </div>

        <n-menu
          :collapsed="collapsed"
          :collapsed-width="76"
          :collapsed-icon-size="22"
          :options="primaryMenuOptions"
          :value="activeKey"
          item-height="46px"
          @update:value="handleMenuClick"
        />

        <div class="category-block">
          <div v-if="!collapsed" class="section-title">影视分类</div>
          <div class="category-scroll">
            <n-menu
              :collapsed="collapsed"
              :collapsed-width="76"
              :collapsed-icon-size="20"
              :options="categoryMenuOptions"
              :value="categoryKey"
              item-height="46px"
              @update:value="handleCategoryClick"
            />
          </div>
        </div>

        <div class="sider-bottom">
          <n-menu
            :collapsed="collapsed"
            :collapsed-width="76"
            :collapsed-icon-size="22"
            :options="bottomMenuOptions"
            :value="activeKey"
            item-height="46px"
            @update:value="handleMenuClick"
          />
        </div>
      </div>
    </n-layout-sider>

    <n-layout class="content-layout">
      <n-layout-content :native-scrollbar="false" content-style="height: 100%;">
        <router-view />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<script setup>
import { computed, h, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NIcon } from 'naive-ui'
import {
  AlbumsOutline,
  BarChartOutline,
  ChevronBackOutline,
  ChevronForwardOutline,
  FilmOutline,
  GridOutline,
  HeartOutline,
  HomeOutline,
  MusicalNotesOutline,
  PlayCircleOutline,
  SettingsOutline,
  SparklesOutline,
  TimeOutline,
  TvOutline,
  VideocamOutline
} from '@vicons/ionicons5'

const router = useRouter()
const route = useRoute()
const collapsed = ref(false)

const activeKey = computed(() => route.name)
const categoryKey = computed(() => route.name === 'Home' ? route.query.category || 'all' : null)

function renderIcon(icon) {
  return () => h(NIcon, null, { default: () => h(icon) })
}

function handleMenuClick(key) {
  router.push({ name: key })
}

function handleCategoryClick(key) {
  router.push({ name: 'Home', query: key === 'all' ? {} : { category: key } })
}

const primaryMenuOptions = [
  { label: '首页', key: 'Home', icon: renderIcon(HomeOutline) },
  { label: '收藏', key: 'Favorites', icon: renderIcon(HeartOutline) },
  { label: '历史记录', key: 'History', icon: renderIcon(TimeOutline) },
  { label: '观影统计', key: 'Stats', icon: renderIcon(BarChartOutline) }
]

const movieCategories = [
  { label: '全部', key: 'all', icon: GridOutline },
  { label: '电影', key: 'movie', icon: FilmOutline },
  { label: '剧集', key: 'series', icon: TvOutline },
  { label: '动漫', key: 'anime', icon: SparklesOutline },
  { label: '综艺', key: 'variety', icon: VideocamOutline },
  { label: '音乐', key: 'music', icon: MusicalNotesOutline },
  { label: '短片', key: 'shorts', icon: PlayCircleOutline },
  { label: '纪录', key: 'documentary', icon: AlbumsOutline }
]

const categoryMenuOptions = movieCategories.map((item) => ({
  label: item.label,
  key: item.key,
  icon: renderIcon(item.icon)
}))

const bottomMenuOptions = [
  { label: '设置', key: 'Settings', icon: renderIcon(SettingsOutline) }
]
</script>

<style scoped>
.movie-shell {
  height: 100vh;
  color: #eef3ff;
  background: #080b10;
}

.movie-sider {
  background: linear-gradient(180deg, #111722 0%, #0c1018 54%, #090b10 100%);
}

.movie-sider :deep(.n-layout-sider-scroll-container) {
  height: 100%;
  overflow: hidden !important;
}

.sider-frame {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: 100vh;
  min-height: 0;
  padding: 14px 10px;
  box-sizing: border-box;
  overflow: hidden;
}

.brand-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 46px;
  margin-bottom: 10px;
  padding: 0 6px;
}

.brand-mark {
  display: grid;
  place-items: center;
  flex: 0 0 34px;
  width: 34px;
  height: 34px;
  border-radius: 8px;
  color: #071016;
  font-weight: 900;
  background: linear-gradient(135deg, #6ee7b7, #60a5fa);
}

.brand-copy {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-width: 0;
  line-height: 1.15;
}

.brand-copy strong {
  overflow: hidden;
  font-size: 15px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.brand-copy span {
  margin-top: 3px;
  color: #8793a8;
  font-size: 12px;
}

.collapse-btn {
  flex: 0 0 auto;
  color: #9aa7bd;
}

.category-block {
  display: flex;
  flex: 1 1 auto;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.07);
}

.category-scroll {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 2px;
}

.category-scroll::-webkit-scrollbar {
  width: 4px;
}

.category-scroll::-webkit-scrollbar-thumb {
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.32);
}

.category-scroll::-webkit-scrollbar-track {
  background: transparent;
}

.section-title {
  margin: 0 12px 8px;
  color: #6f7b91;
  font-size: 12px;
  letter-spacing: 0;
}

.sider-bottom {
  flex: 0 0 auto;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.content-layout {
  height: 100%;
  background:
    radial-gradient(circle at 18% 4%, rgba(63, 185, 170, 0.16), transparent 30%),
    radial-gradient(circle at 84% 0%, rgba(96, 165, 250, 0.14), transparent 28%),
    #080b10;
}

.movie-shell :deep(.n-layout-scroll-container) {
  height: 100%;
}

.movie-shell :deep(.n-menu) {
  background: transparent;
}

.movie-shell :deep(.n-menu-item) {
  height: 46px;
  margin: 0 0 8px;
}

.movie-shell :deep(.n-menu-item-content) {
  box-sizing: border-box;
  width: 100%;
  height: 46px;
  margin: 0;
  padding-right: 16px;
  border-radius: 8px;
  color: #a7b0c0;
  background: transparent;
}

.movie-shell :deep(.n-menu-item-content:hover) {
  color: #eef3ff;
  background-color: rgba(255, 255, 255, 0.06);
}

.movie-shell :deep(.n-menu-item-content--selected) {
  color: #66f0ce;
  background: rgba(32, 92, 86, 0.82);
}

.movie-shell :deep(.n-menu-item-content--selected::before) {
  display: none;
}

.movie-shell :deep(.n-menu-item-content__icon) {
  color: currentColor;
}

.movie-shell :deep(.n-layout-sider--collapsed .n-menu-item-content) {
  position: relative;
  display: flex;
  justify-content: center;
  width: 46px;
  margin: 0 auto;
  padding: 0 !important;
}

.movie-shell :deep(.n-layout-sider--collapsed .n-menu-item-content-header) {
  display: none;
}

.movie-shell :deep(.n-layout-sider--collapsed .n-menu-item-content__icon) {
  position: absolute;
  top: 50%;
  left: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  margin: 0 !important;
  transform: translate(-50%, -50%);
}

.movie-shell :deep(.n-layout-sider--collapsed .n-menu-item-content__icon .n-icon) {
  display: flex;
  margin: 0;
}
</style>
