<template>
  <div>
    <n-h2>设置</n-h2>
    <n-form label-placement="left" label-width="120">
      <n-form-item label="主题">
        <n-switch v-model:value="darkMode" />
        <span style="margin-left: 8px;">暗色模式</span>
      </n-form-item>
      <n-form-item label="通知">
        <n-switch v-model:value="notification" />
        <span style="margin-left: 8px;">开启通知</span>
      </n-form-item>
      <n-form-item label="语言">
        <n-select v-model:value="language" :options="langOptions" style="width: 200px;" />
      </n-form-item>
    </n-form>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const darkMode = ref(true)
const notification = ref(false)
const language = ref('zh-CN')
const langOptions = [
  { label: '简体中文', value: 'zh-CN' },
  { label: 'English', value: 'en-US' }
]
</script>
