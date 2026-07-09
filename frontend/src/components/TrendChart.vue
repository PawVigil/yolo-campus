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
let observer = null
let animated = false

function initChart() {
  if (!chartRef.value) return
  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting) {
        observer.disconnect()
        observer = null
        chart = echarts.init(chartRef.value)
        updateChart()
        animated = true
      }
    },
    { threshold: 0.6 }
  )
  observer.observe(chartRef.value)
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
    animationDuration: animated ? 400 : 3000,
    animationEasing: 'cubicOut',
    series: [
      // 面积填充层
      {
        type: 'line',
        data: yData,
        smooth: true,
        lineStyle: { width: 0 },
        itemStyle: { color: 'transparent' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(26, 51, 0, 0.25)' },
            { offset: 1, color: 'rgba(26, 51, 0, 0.02)' },
          ]),
        },
        symbol: 'none',
        silent: true,
        animationDuration: animated ? 400 : 2000,
        animationEasing: 'cubicOut',
        z: 0,
      },
      // 线条 + 数据点（逐点绘制）
      {
        type: 'line',
        data: yData,
        smooth: true,
        lineStyle: { color: props.color, width: 2 },
        itemStyle: { color: props.color },
        symbol: 'circle',
        symbolSize: 6,
        animationDuration: animated ? 400 : 3000,
        animationEasing: 'cubicOut',
        animationDelay: animated ? 0 : function (idx) {
          // 前几个点慢，后面匀速
          var total = 14
          var slowPart = Math.min(idx, 4) * 280   // 前4个点，每个280ms
          var fastPart = Math.max(0, idx - 4) * 100  // 后面匀速100ms
          return slowPart + fastPart
        },
        markPoint: {
          data: [
            { type: 'max', name: '最高', symbol: 'pin', symbolSize: 1, itemStyle: { color: 'transparent' }, label: { show: true, fontSize: 13, fontWeight: 'bold', color: '#1a3300', formatter: '{c}', offset: [0, -14] } },
          ],
          animationDuration: animated ? 400 : 800,
          animationDelay: animated ? 0 : 3000,
        },
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
  observer?.disconnect()
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
