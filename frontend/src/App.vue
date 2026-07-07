<template>
  <n-config-provider :locale="zhCN" :date-locale="dateZhCN" :theme-overrides="themeOverrides">
    <n-message-provider>
      <router-view />
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import { zhCN, dateZhCN } from 'naive-ui'

const themeOverrides = {
  common: {
    primaryColor: '#7c5ce7',
    primaryColorHover: '#9b7ef0',
    primaryColorPressed: '#5e3fc7',
    primaryColorSuppl: '#7c5ce7',
    borderRadius: '8px',
  },
}
</script>

<style>
body {
  margin: 0;
  padding: 0;
  font-family: 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', sans-serif;
  background: #f5f7fa;
}

#app {
  min-height: 100vh;
}
</style>
