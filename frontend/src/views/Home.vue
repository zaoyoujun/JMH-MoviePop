<template>
  <div>
    <n-h2>首页</n-h2>
    <n-card title="轮播推荐">
      <n-carousel autoplay>
        <img class="carousel-img" src="https://naive-ui.oss-cn-beijing.aliyuncs.com/carousel-img/carousel1.jpeg">
        <img class="carousel-img" src="https://naive-ui.oss-cn-beijing.aliyuncs.com/carousel-img/carousel2.jpeg">
        <img class="carousel-img" src="https://naive-ui.oss-cn-beijing.aliyuncs.com/carousel-img/carousel3.jpeg">
        <img class="carousel-img" src="https://naive-ui.oss-cn-beijing.aliyuncs.com/carousel-img/carousel4.jpeg">
      </n-carousel>
    </n-card>
    <n-card title="热门影视" style="margin-top: 16px;">
      <n-space>
        <n-tag v-for="i in 6" :key="i" type="info" size="large">影视 {{ i }}</n-tag>
      </n-space>
    </n-card>
  </div>
</template>

<style scoped>
.carousel-img {
  width: 100%;
  height: 240px;
  object-fit: cover;
}
</style>
