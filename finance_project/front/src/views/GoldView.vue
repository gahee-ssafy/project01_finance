<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'
import SpotLineChart from '@/components/SpotLineChart.vue'

const store = useAuthStore()

// 원본 데이터
const spotList = ref([])

// UI 상태
const asset = ref('Gold')         // 'Gold' | 'Silver'
const startDate = ref('')         // 'YYYY-MM-DD' or ''
const endDate = ref('')           // 'YYYY-MM-DD' or ''
const errorMsg = ref('')

// "조회" 버튼을 눌로만 필터 적용되게(원하면 즉시 필터로 바꿔도 됨)
const appliedStart = ref('')
const appliedEnd = ref('')

const loading = ref(true)

onMounted(async () => {
  loading.value = true
  try {
    const res = await axios({
      method: 'get',
      url: `${store.API_URL}/api/v1/products/spot/`,
    })
    spotList.value = res.data || []
  } catch (err) {
    console.log('데이터 로드 실패', err)
  } finally {
    loading.value = false
  }
})

function applyFilter() {
  errorMsg.value = ''

  // 입력 안 하면 전체 기간
  if (!startDate.value && !endDate.value) {
    appliedStart.value = ''
    appliedEnd.value = ''
    return
  }

  // 한쪽만 입력된 경우도 허용: start만 있으면 start~끝, end만 있으면 처음~end
  // 단, 둘 다 있을 때 start > end면 에러
  if (startDate.value && endDate.value) {
    if (startDate.value > endDate.value) {
      errorMsg.value = '잘못된 날짜 선택 시 적절한 문구 출력: 시작일이 종료일보다 늦습니다.'
      return
    }
  }

  appliedStart.value = startDate.value
  appliedEnd.value = endDate.value
}

function resetFilter() {
  startDate.value = ''
  endDate.value = ''
  appliedStart.value = ''
  appliedEnd.value = ''
  errorMsg.value = ''
}

const filtered = computed(() => {
  // 1) 자산 필터
  let arr = (spotList.value || []).filter((x) => x.item_name === asset.value)

  // 2) 날짜 오름차순 정렬 (문자열 YYYY-MM-DD라면 문자열 정렬도 OK)
  arr = arr.slice().sort((a, b) => (a.base_date > b.base_date ? 1 : -1))

  // 3) 기간 필터 (선택 안 하면 전체)
  const s = appliedStart.value
  const e = appliedEnd.value

  if (!s && !e) return arr

  return arr.filter((x) => {
    const d = x.base_date
    if (s && e) return s <= d && d <= e
    if (s && !e) return s <= d
    if (!s && e) return d <= e
    return true
  })
})

const chartLabels = computed(() => filtered.value.map((x) => x.base_date))
const chartValues = computed(() => filtered.value.map((x) => Number(x.price)))
const chartTitle = computed(() => (asset.value === 'Gold' ? '금(Gold) 가격' : '은(Silver) 가격'))
</script>

<template>
  <div class="container">
    <h1 class="title">📈 현물 시세 그래프</h1>

    <!-- 컨트롤 패널 -->
    <div class="controls">
      <div class="asset">
        <button :class="{ on: asset === 'Gold' }" @click="asset = 'Gold'">금 (Gold)</button>
        <button :class="{ on: asset === 'Silver' }" @click="asset = 'Silver'">은 (Silver)</button>
      </div>

      <div class="range">
        <div class="field">
          <label>시작일</label>
          <input type="date" v-model="startDate" />
        </div>
        <div class="field">
          <label>종료일</label>
          <input type="date" v-model="endDate" />
        </div>

        <div class="btns">
          <button class="primary" @click="applyFilter">조회</button>
          <button class="ghost" @click="resetFilter">전체보기</button>
        </div>
      </div>

      <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
      <p v-else class="hint">
        시작일/종료일을 선택하지 않으면 전체 기간 데이터를 보여줍니다.
      </p>
    </div>

    <!-- 그래프 -->
    <div v-if="loading" class="empty-box">불러오는 중...</div>

    <div v-else>
      <div v-if="chartLabels.length === 0" class="empty-box">
        해당 조건의 데이터가 없습니다.
      </div>

      <SpotLineChart
        v-else
        :labels="chartLabels"
        :values="chartValues"
        :title="chartTitle"
      />

      <!-- (선택) 아래 표도 같이 유지하고 싶으면 남겨둬도 됨 -->
      <div class="table-wrap" v-if="chartLabels.length > 0">
        <h2 class="subttl">데이터 목록</h2>
        <table class="gold-table">
          <thead>
            <tr>
              <th>품목</th>
              <th>기준일</th>
              <th>시세 ($)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filtered" :key="item.id">
              <td>
                <span v-if="item.item_name === 'Gold'">🟡 금 (Gold)</span>
                <span v-else>⚪ 은 (Silver)</span>
              </td>
              <td>{{ item.base_date }}</td>
              <td class="price">$ {{ Number(item.price).toLocaleString() }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container { max-width: 980px; margin: 0 auto; padding: 40px 20px; }
.title { text-align: center; margin-bottom: 18px; font-weight: 900; color: #333; }

.controls {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
}

.asset { display: flex; gap: 10px; margin-bottom: 14px; }
.asset button {
  border: 1px solid #ddd;
  background: #fff;
  padding: 10px 12px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 800;
}
.asset button.on { border-color: #999; }

.range { display: flex; gap: 12px; align-items: flex-end; flex-wrap: wrap; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 12px; color: #666; font-weight: 700; }
.field input { border: 1px solid #ddd; border-radius: 10px; padding: 8px 10px; }

.btns { display: flex; gap: 8px; }
.primary {
  border: 1px solid #ddd;
  background: #fff;
  padding: 10px 14px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 800;
}
.ghost {
  border: 1px solid #eee;
  background: #f8f9fa;
  padding: 10px 14px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 800;
}

.hint { margin-top: 10px; color: #666; font-size: 0.92rem; }
.error { margin-top: 10px; color: #c0392b; font-weight: 800; }

.empty-box { text-align: center; padding: 28px; background: #f1f1f1; border-radius: 12px; color: #666; margin-top: 14px; }

.table-wrap { margin-top: 18px; }
.subttl { margin: 14px 0 10px; font-weight: 900; }

.gold-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  border-radius: 8px;
  overflow: hidden;
}
.gold-table th { background: #f8f9fa; padding: 14px; text-align: left; font-weight: 900; border-bottom: 2px solid #eee; }
.gold-table td { padding: 14px; border-bottom: 1px solid #eee; }
.price { font-weight: 900; }
</style>
