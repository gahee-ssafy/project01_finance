<template>
  <div class="chart-wrap">
    <canvas ref="canvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import Chart from 'chart.js/auto'

const props = defineProps({
  labels: { type: Array, default: () => [] }, // 날짜 문자열 배열
  values: { type: Array, default: () => [] }, // 가격 배열
  title: { type: String, default: '가격 변동' },
})

const canvas = ref(null)
let chart = null

function render() {
  if (!canvas.value) return

  if (chart) {
    chart.destroy()
    chart = null
  }

  chart = new Chart(canvas.value, {
    type: 'line',
    data: {
      labels: props.labels,
      datasets: [
        {
          label: props.title,
          data: props.values,
          tension: 0.25,
          pointRadius: 2,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: true },
      },
      scales: {
        y: { beginAtZero: false },
      },
    },
  })
}

onMounted(render)

watch(
  () => [props.labels, props.values],
  () => render(),
  { deep: true }
)

onBeforeUnmount(() => {
  if (chart) chart.destroy()
})
</script>

<style scoped>
.chart-wrap {
  width: 100%;
  background: #fff;
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 14px;
}
</style>
