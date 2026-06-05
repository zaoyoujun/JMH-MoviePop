<script setup>
import { darkTheme } from 'naive-ui'

const themeOverrides = {
  common: {
    borderRadius: '14px',
    borderRadiusSmall: '12px'
  },
  Button: {
    borderRadiusTiny: '10px',
    borderRadiusSmall: '12px',
    borderRadiusMedium: '14px',
    borderRadiusLarge: '16px'
  }
}
</script>

<template>
  <n-config-provider :theme="darkTheme" :theme-overrides="themeOverrides">
    <n-message-provider>
      <n-notification-provider>
        <router-view />
      </n-notification-provider>
    </n-message-provider>
  </n-config-provider>
</template>

