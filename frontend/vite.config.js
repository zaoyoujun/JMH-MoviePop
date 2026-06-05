import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// 自动导入插件
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { NaiveUiResolver } from 'unplugin-vue-components/resolvers'

// https://vite.dev/config/
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: process.env.VITE_API_TARGET || 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  plugins: [
    vue(),
    vueDevTools(),

    // 👇 新增：自动导入 Vue API + Naive UI 组件
    AutoImport({
      imports: ['vue', 'vue-router'], // 自动导入 vue / vue-router
      dts: true, // 生成类型声明文件（TS 友好）
    }),
    Components({
      resolvers: [NaiveUiResolver()], // 自动识别 naive-ui 组件
      dts: true,
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})
