<template>
  <div ref="chartRef" class="trend-chart"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: { type: Array, required: true },        // [{day, count}, ...]
  title: { type: String, default: '' },
  height: { type: String, default: '300px' },
  xField: { type: String, default: 'day' },
  yField: { type: String, default: 'count' },
  color: { type: String, default: '#1a3300' },
})

const chartRef = ref(null)
let chart = null

function initChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value)
  updateChart()
}

function updateChart() {
  if (!chart) return
  const xData = props.data.map((d) => d[props.xField])
  const yData = props.data.map((d) => d[props.yField])

  chart.setOption({
    title: props.title
      ? { text: props.title, left: 'center', textStyle: { fontSize: 14, fontWeight: 500, color: '#1a3300' } }
      : undefined,
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#fcfaf5',
      borderColor: '#b6b6b6',
      textStyle: { color: '#1a3300', fontSize: 12 },
    },
    grid: { top: props.title ? 40 : 20, right: 20, bottom: 30, left: 50 },
    xAxis: {
      type: 'category',
      data: xData.map(d => d.slice(5)),
      axisLabel: { rotate: 45, fontSize: 11, color: '#b6b6b6' },
      axisLine: { lineStyle: { color: '#b6b6b6' } },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      splitLine: { lineStyle: { color: '#e8e0d5', type: 'dashed' } },
      axisLabel: { fontSize: 11, color: '#b6b6b6' },
    },
    series: [
      {
        type: 'line',
        data: yData,
        smooth: true,
        lineStyle: { color: props.color, width: 2 },
        itemStyle: { color: props.color },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(26, 51, 0, 0.25)' },
            { offset: 1, color: 'rgba(26, 51, 0, 0.02)' },
          ]),
        },
        symbol: 'circle',
        symbolSize: 6,
      },
    ],
  })
}

const onResize = () => chart?.resize()

onMounted(() => {
  initChart()
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  chart?.dispose()
})

watch(() => props.data, updateChart, { deep: true })
</script>

<style scoped>
.trend-chart {
  width: 100%;
  height: v-bind(height);
}
</style>
