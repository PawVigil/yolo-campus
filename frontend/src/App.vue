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
    primaryColor: '#1a3300',
    primaryColorHover: '#2d4a0a',
    primaryColorPressed: '#0f1f00',
    primaryColorSuppl: '#1a3300',
    textColor1: '#1a3300',
    textColor2: '#1a3300',
    textColor3: '#b6b6b6',
    bodyColor: '#fcfaf5',
    cardColor: '#fcfaf5',
    modalColor: '#fcfaf5',
    popoverColor: '#fcfaf5',
    borderColor: '#b6b6b6',
    dividerColor: '#b6b6b6',
    borderRadius: '6px',
    inputColor: '#fcfaf5',
    successColor: '#1a3300',
    warningColor: '#e89970',
    errorColor: '#b33a3a',
    infoColor: '#a8e5e5',
    boxShadow1: 'rgba(0, 0, 0, 0.05) 0px 1px 2px 0px',
    boxShadow2: 'rgba(0, 0, 0, 0.08) 0px 1px 3px 0px',
    fontFamily: "'Inter', 'PingFang SC', 'Noto Sans SC', 'Microsoft YaHei', sans-serif",
    fontSize: '14px',
    fontSizeSmall: '12px',
    fontSizeMedium: '14px',
    fontSizeLarge: '16px',
    fontSizeHuge: '18px',
  },
  Button: {
    borderRadiusSmall: '6px',
    borderRadiusMedium: '6px',
    borderRadiusLarge: '6px',
  },
  Card: {
    borderRadius: '12px',
    paddingSmall: '16px',
    paddingMedium: '24px',
  },
  Tag: {
    borderRadius: '9999px',
  },
  Input: {
    borderRadius: '6px',
    borderFocus: '1.5px solid #1a3300',
    boxShadowFocus: 'none',
  },
  Menu: {
    itemTextColor: '#1a3300',
    itemTextColorHover: '#1a3300',
    itemTextColorActive: '#1a3300',
    itemColorActive: '#ffe95c',
    itemColorActiveHover: '#ffe95c',
  },
  Layout: {
    siderColor: '#fcfaf5',
    headerColor: '#fcfaf5',
    footerColor: '#fcfaf5',
  },
}
</script>

<style>
/* Global base styles are in src/styles/global.css — keep App.vue minimal */
</style>
