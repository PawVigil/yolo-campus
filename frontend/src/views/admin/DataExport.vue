<template>
  <div class="export-page">
    <h2 class="page-title">📥 数据导出</h2>

    <!-- 报告类型选择 -->
    <n-card :bordered="false" class="type-card">
      <n-radio-group v-model:value="reportType">
        <n-radio-button value="weekly">📊 周报</n-radio-button>
        <n-radio-button value="monthly">📅 月报</n-radio-button>
      </n-radio-group>

      <div class="date-selector">
        <!-- 周报：日期范围 -->
        <template v-if="reportType === 'weekly'">
          <n-form-item label="选择周范围">
            <n-date-picker v-model:value="weekRange" type="daterange" clearable placeholder="选择起止日期" />
          </n-form-item>
        </template>
        <!-- 月报：年月选择 -->
        <template v-else>
          <n-form-item label="选择月份">
            <n-date-picker v-model:value="monthDate" type="month" clearable placeholder="选择月份" />
          </n-form-item>
        </template>
      </div>

      <n-button type="primary" size="large" :loading="previewLoading" @click="doPreview">
        🔍 预览统计
      </n-button>
    </n-card>

    <!-- 预览结果 -->
    <n-card v-if="previewData" :bordered="false" title="📊 统计预览" class="preview-card">
      <n-table :single-line="false" :bordered="false">
        <thead>
          <tr>
            <th>指标</th>
            <th>数值</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in previewData.data" :key="item.metric">
            <td>{{ item.metric }}</td>
            <td class="value-cell">{{ item.value }}</td>
          </tr>
        </tbody>
      </n-table>

      <n-divider />

      <div class="export-actions">
        <n-button type="primary" @click="doExport('csv')">
          📄 导出 CSV
        </n-button>
        <n-button @click="doExport('json')">
          📋 导出 JSON
        </n-button>
      </div>
    </n-card>

    <!-- 导出完成提示 -->
    <n-card v-if="exportReady" :bordered="false" class="export-done">
      <n-result status="success" title="导出成功" :description="exportDesc">
        <template #footer>
          <n-button @click="downloadFile">📥 下载文件</n-button>
        </template>
      </n-result>
    </n-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useMessage } from 'naive-ui'
import { getWeeklyReport, getMonthlyReport } from '@/api/admin.js'

const message = useMessage()
const reportType = ref('weekly')
const weekRange = ref(null)
const monthDate = ref(null)
const previewLoading = ref(false)
const previewData = ref(null)
const exportReady = ref(false)
const exportDesc = ref('')
const exportBlob = ref(null)
const exportFileName = ref('')

function formatDate(d) {
  if (!d) return ''
  if (typeof d === 'number') {
    const dt = new Date(d)
    return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')}`
  }
  return d
}

async function doPreview() {
  previewLoading.value = true
  exportReady.value = false
  previewData.value = null

  try {
    if (reportType.value === 'weekly') {
      if (!weekRange.value || weekRange.value.length < 2) {
        message.warning('请选择起止日期')
        previewLoading.value = false
        return
      }
      const start = formatDate(weekRange.value[0])
      const end = formatDate(weekRange.value[1])
      previewData.value = await getWeeklyReport({ start, end, format: 'json' })
    } else {
      if (!monthDate.value) {
        message.warning('请选择月份')
        previewLoading.value = false
        return
      }
      const d = new Date(typeof monthDate.value === 'number' ? monthDate.value : monthDate.value)
      const year = d.getFullYear()
      const month = d.getMonth() + 1
      previewData.value = await getMonthlyReport({ year, month, format: 'json' })
    }
  } catch (e) {
    console.error('预览失败', e)
    message.error('获取统计数据失败')
  } finally {
    previewLoading.value = false
  }
}

async function doExport(format) {
  try {
    let data, fileName
    if (reportType.value === 'weekly') {
      const start = formatDate(weekRange.value[0])
      const end = formatDate(weekRange.value[1])
      data = await getWeeklyReport({ start, end, format })
      fileName = `周报_${start.replace(/-/g, '')}_${end.replace(/-/g, '')}.${format}`
    } else {
      const d = new Date(typeof monthDate.value === 'number' ? monthDate.value : monthDate.value)
      data = await getMonthlyReport({ year: d.getFullYear(), month: d.getMonth() + 1, format })
      fileName = `月报_${d.getFullYear()}年${d.getMonth() + 1}月.${format}`
    }

    const content = typeof data === 'string' ? data : JSON.stringify(data, null, 2)
    const mimeType = format === 'csv' ? 'text/csv;charset=utf-8' : 'application/json;charset=utf-8'
    exportBlob.value = new Blob(['﻿' + content], { type: mimeType })
    exportFileName.value = fileName
    exportReady.value = true
    exportDesc.value = `文件 ${fileName} 已就绪，点击下方按钮下载`
  } catch (e) {
    console.error('导出失败', e)
    message.error('导出数据失败')
  }
}

function downloadFile() {
  if (!exportBlob.value) return
  const url = URL.createObjectURL(exportBlob.value)
  const a = document.createElement('a')
  a.href = url
  a.download = exportFileName.value
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.export-page { max-width: 800px; }
.page-title { margin-bottom: 20px; font-size: 22px; }
.type-card { margin-bottom: 16px; }
.date-selector { margin: 16px 0; max-width: 400px; }
.preview-card { margin-bottom: 16px; }
.value-cell { font-weight: 700; font-size: 20px; color: #7c5ce7; }
.export-actions { display: flex; gap: 12px; }
.export-done { margin-top: 16px; }
</style>
