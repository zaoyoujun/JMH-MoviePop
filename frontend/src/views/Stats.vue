<template>
  <div>
    <n-h2>观影统计</n-h2>
    <n-grid :cols="3" :x-gap="16">
      <n-gi>
        <n-card title="总观影数">
          <n-statistic label="部" :value="42" />
        </n-card>
      </n-gi>
      <n-gi>
        <n-card title="总时长">
          <n-statistic label="小时" :value="128" />
        </n-card>
      </n-gi>
      <n-gi>
        <n-card title="本月观影">
          <n-statistic label="部" :value="7" />
        </n-card>
      </n-gi>
    </n-grid>
  </div>
</template>
