<template>
  <n-layout has-sider style="height: 100vh;">
    <n-layout-sider
      collapse-mode="transform"
      :collapsed-width="64"
      :width="200"
      show-trigger="bar"
      bordered
      :native-scrollbar="false"
    >
      <div style="padding: 16px; text-align: center;">
        <n-h3 style="margin: 0;">MoviePop</n-h3>
      </div>
      <n-menu
        :collapsed-width="64"
        :collapsed-icon-size="22"
        :options="menuOptions"
        :value="activeKey"
        @update:value="handleMenuClick"
      />
    </n-layout-sider>
    <n-layout-content content-style="padding: 24px;" :native-scrollbar="false">
      <router-view />
    </n-layout-content>
  </n-layout>
</template>

<script setup>
import { computed, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NIcon } from 'naive-ui'
import { HomeOutline, HeartOutline, TimeOutline, BarChartOutline, SettingsOutline } from '@vicons/ionicons5'

const router = useRouter()
const route = useRoute()

const activeKey = computed(() => route.name)

function renderIcon(icon) {
  return function () {
    return h(NIcon, null, { default: function () { return h(icon) } })
  }
}

function handleMenuClick(key) {
  router.push({ name: key })
}

const menuOptions = [
  { label: '首页', key: 'Home', icon: renderIcon(HomeOutline) },
  { label: '收藏', key: 'Favorites', icon: renderIcon(HeartOutline) },
  { label: '历史记录', key: 'History', icon: renderIcon(TimeOutline) },
  { label: '观影统计', key: 'Stats', icon: renderIcon(BarChartOutline) },
  { label: '设置', key: 'Settings', icon: renderIcon(SettingsOutline) }
]
</script>
