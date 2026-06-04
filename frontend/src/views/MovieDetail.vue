<template>
  <div>
    <n-page-header title="返回" @back="$router.back()">
      <template #extra>
        <n-space>
          <n-button type="primary">收藏</n-button>
          <n-button>分享</n-button>
        </n-space>
      </template>
    </n-page-header>
    <n-card :title="`影视详情 #${$route.params.id}`">
      <n-descriptions bordered :column="2">
        <n-descriptions-item label="类型">电影</n-descriptions-item>
        <n-descriptions-item label="年份">2026</n-descriptions-item>
        <n-descriptions-item label="导演">导演名称</n-descriptions-item>
        <n-descriptions-item label="评分">8.5</n-descriptions-item>
        <n-descriptions-item label="简介" :span="2">
          这是一部精彩的电影，剧情跌宕起伏，值得一看。
        </n-descriptions-item>
      </n-descriptions>
    </n-card>
  </div>
</template>
