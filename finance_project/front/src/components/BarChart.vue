<template>
  <div>
    <canvas ref="canvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import Chart from 'chart.js/auto'

const props = defineProps({
  labels: { type: Array, default: () => [] },
  values: { type: Array, default: () => [] },
  title: { type: String, default: '금리 그래프' },
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
    type: 'bar',
    data: {
      labels: props.labels,
      datasets: [{ label: props.title, data: props.values }],
    },
    options: {
      responsive: true,
      scales: { y: { beginAtZero: true } },
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
