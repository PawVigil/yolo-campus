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
  color: { type: String, default: '#7c5ce7' },
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
      ? { text: props.title, left: 'center', textStyle: { fontSize: 14, fontWeight: 500 } }
      : undefined,
    tooltip: { trigger: 'axis' },
    grid: { top: props.title ? 40 : 20, right: 20, bottom: 30, left: 50 },
    xAxis: {
      type: 'category',
      data: xData,
      axisLabel: { rotate: 30, fontSize: 11 },
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
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
            { offset: 0, color: props.color + '40' },
            { offset: 1, color: props.color + '05' },
          ]),
        },
        symbol: 'circle',
        symbolSize: 6,
      },
    ],
  })
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', () => chart?.resize())
})

onUnmounted(() => {
  window.removeEventListener('resize', () => chart?.resize())
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
