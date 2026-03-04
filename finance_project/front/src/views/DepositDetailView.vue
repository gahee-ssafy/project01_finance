<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const store = useAuthStore()

const fin_prdt_cd = route.params.fin_prdt_cd

const loading = ref(true)
const product = ref(null)

const savedCodes = computed(() => {
  if (Array.isArray(store.user?.joined_products)) {
    return new Set(store.user.joined_products.map(p => p.fin_prdt_cd).filter(Boolean))
  }
  const raw = store.user?.financial_products || ''
  return new Set(raw.split(',').map(s => s.trim()).filter(Boolean))
})

const isSaved = computed(() => {
  if (!product.value?.fin_prdt_cd) return false
  return savedCodes.value.has(product.value.fin_prdt_cd)
})

const fetchDetail = async () => {
  loading.value = true
  try {
    const res = await axios.get(`${store.API_URL}/api/v1/products/deposit/${fin_prdt_cd}/`)
    product.value = res.data
  } catch (err) {
    console.log('상세 조회 실패:', err?.response?.status, err?.response?.data)
    window.alert('상품 상세를 불러오지 못했습니다.')
    router.push({ name: 'DepositView' })
  } finally {
    loading.value = false
  }
}

const toggleSave = async () => {
  if (!store.isLogin) {
    window.alert('로그인이 필요합니다.')
    router.push({ name: 'LogInView' })
    return
  }

  try {
    await axios({
      method: isSaved.value ? 'delete' : 'post',
      url: `${store.API_URL}/api/v1/products/deposit/${fin_prdt_cd}/join/`,
      headers: store.authHeader,
    })
    await store.fetchMe?.()
  } catch (err) {
    console.log('저장 토글 실패:', err?.response?.status, err?.response?.data)
    window.alert('저장 처리에 실패했습니다.')
  }
}

onMounted(fetchDetail)
</script>

<template>
  <div class="container">
    <button class="back" @click="$router.back()">← 뒤로</button>

    <div v-if="loading" class="loading">불러오는 중...</div>

    <div v-else-if="product" class="card">
      <div class="head">
        <div>
          <div class="bank">{{ product.kor_co_nm }}</div>
          <h1 class="name">{{ product.fin_prdt_nm }}</h1>
        </div>

        <button class="save-btn" :class="{ saved: isSaved }" @click="toggleSave">
          {{ isSaved ? '저장됨' : '저장' }}
        </button>
      </div>

      <div class="meta">
        <div><b>상품코드</b> {{ product.fin_prdt_cd }}</div>
        <div v-if="product.join_deny"><b>가입제한</b> {{ product.join_deny }}</div>
        <div v-if="product.join_way"><b>가입방법</b> {{ product.join_way }}</div>
      </div>

      <h2 class="subttl">기간별 금리</h2>
      <table class="tbl" v-if="product.options && product.options.length">
        <thead>
          <tr>
            <th>기간</th>
            <th>금리유형</th>
            <th>기본금리</th>
            <th>최고금리</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="opt in product.options" :key="opt.id">
            <td>{{ opt.save_trm }}개월</td>
            <td>{{ opt.intr_rate_type_nm }}</td>
            <td>{{ opt.intr_rate }}%</td>
            <td class="hi">{{ opt.intr_rate2 }}%</td>
          </tr>
        </tbody>
      </table>

      <div v-else class="empty">옵션 데이터가 없습니다.</div>
    </div>
  </div>
</template>

<style scoped>
.container { max-width: 980px; margin: 0 auto; padding: 30px 18px; }
.back { border: 1px solid #eee; background: #fff; padding: 8px 12px; border-radius: 10px; cursor: pointer; font-weight: 800; }
.loading { margin-top: 20px; text-align: center; color: #777; }

.card { margin-top: 14px; border: 1px solid #eee; background: #fff; border-radius: 14px; padding: 18px; }
.head { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.bank { color: #666; font-weight: 800; }
.name { margin: 4px 0 0; font-weight: 1000; }

.save-btn { border: 1px solid #ddd; background: #fff; border-radius: 10px; padding: 10px 14px; font-weight: 900; cursor: pointer; }
.save-btn.saved { border-color: #42b983; color: #42b983; }

.meta { margin-top: 12px; display: grid; gap: 6px; color: #333; }
.subttl { margin: 18px 0 10px; font-weight: 1000; }

.tbl { width: 100%; border-collapse: collapse; }
.tbl th, .tbl td { padding: 10px; border-bottom: 1px solid #eee; text-align: left; }
.tbl th { background: #f8f9fa; font-weight: 900; }
.hi { font-weight: 1000; color: #d63031; }

.empty { padding: 14px; background: #f6f6f6; border-radius: 10px; color: #666; }
</style>
