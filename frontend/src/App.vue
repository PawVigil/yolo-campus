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
    primaryColor: '#2F4B26',
    primaryColorHover: '#3D5A45',
    primaryColorPressed: '#1E3318',
    primaryColorSuppl: '#2F4B26',
    textColor1: '#2F4B26',
    textColor2: '#4A4238',
    textColor3: '#8A7F6F',
    bodyColor: '#FCF8F1',
    cardColor: '#FCF7ED',
    modalColor: '#FCF7ED',
    popoverColor: '#FCF7ED',
    borderColor: '#E6DED0',
    dividerColor: '#E6DED0',
    borderRadius: '6px',
    inputColor: '#FCF7ED',
    successColor: '#3D5A45',
    warningColor: '#D69146',
    errorColor: '#A03D2B',
    infoColor: '#a8e5e5',
    boxShadow1: 'rgba(90, 70, 45, 0.10) 0px 1px 2px 0px',
    boxShadow2: 'rgba(90, 70, 45, 0.14) 0px 1px 3px 0px',
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
