<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const store = useAuthStore()

const products = ref([])
const loading = ref(false)

// 필터/정렬/검색
const bank = ref('')
const term = ref('')
const sort = ref('')
const q = ref('')
const bankOptions = ref([])

const savedCodes = computed(() => {
  if (Array.isArray(store.user?.joined_products)) {
    return new Set(store.user.joined_products.map(p => p.fin_prdt_cd).filter(Boolean))
  }
  const raw = store.user?.financial_products || ''
  return new Set(raw.split(',').map(s => s.trim()).filter(Boolean))
})

const fetchProducts = async () => {
  loading.value = true
  try {
    const res = await axios.get(`${store.API_URL}/api/v1/products/deposit/`, {
      params: {
        bank: bank.value || undefined,
        term: term.value || undefined,
        sort: sort.value || undefined,
        q: q.value || undefined,
      },
    })
    products.value = res.data || []

    const set = new Set(products.value.map(p => p.kor_co_nm).filter(Boolean))
    bankOptions.value = Array.from(set).sort()
  } catch (err) {
    console.log('예적금 목록 로드 실패:', err)
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  bank.value = ''
  term.value = ''
  sort.value = ''
  q.value = ''
  fetchProducts()
}

const goDetail = (product) => {
  router.push({ name: 'DepositDetailView', params: { fin_prdt_cd: product.fin_prdt_cd } })
}

const toggleSave = async (product) => {
  if (!store.isLogin) {
    window.alert('로그인이 필요합니다.')
    router.push({ name: 'LogInView' })
    return
  }

  const code = product.fin_prdt_cd
  if (!code) return

  const isSaved = savedCodes.value.has(code)

  try {
    await axios({
      method: isSaved ? 'delete' : 'post',
      url: `${store.API_URL}/api/v1/products/deposit/${code}/join/`,
      headers: store.authHeader,
    })
    await store.fetchMe?.()
  } catch (err) {
    console.log('저장 토글 실패:', err?.response?.status, err?.response?.data)
    window.alert('저장 처리에 실패했습니다.')
  }
}

onMounted(fetchProducts)
</script>

<template>
  <div class="container">
    <h1 class="page-title">💰 예금 상품 조회</h1>

    <!-- 필터/정렬/검색 -->
    <div class="panel">
      <div class="row">
        <div class="field">
          <label>은행</label>
          <select v-model="bank">
            <option value="">전체</option>
            <option v-for="b in bankOptions" :key="b" :value="b">{{ b }}</option>
          </select>
        </div>

        <div class="field">
          <label>기간(개월)</label>
          <select v-model="term">
            <option value="">전체</option>
            <option value="6">6</option>
            <option value="12">12</option>
            <option value="24">24</option>
            <option value="36">36</option>
          </select>
        </div>

        <div class="field">
          <label>정렬</label>
          <select v-model="sort">
            <option value="">기본</option>
            <option value="intr_rate2_desc">최고금리 높은순</option>
            <option value="intr_rate_desc">기본금리 높은순</option>
            <option value="bank_asc">은행명 오름차순</option>
            <option value="name_asc">상품명 오름차순</option>
          </select>
        </div>

        <div class="field search">
          <label>검색</label>
          <input v-model="q" placeholder="은행명/상품명 검색" @keyup.enter="fetchProducts" />
        </div>

        <div class="btns">
          <button class="primary" @click="fetchProducts">적용</button>
          <button class="ghost" @click="resetFilter">초기화</button>
        </div>
      </div>
      <p class="hint">필터/정렬 변경 후 “적용”을 누르거나 검색창에서 Enter를 누르세요.</p>
    </div>

    <div v-if="loading" class="loading">상품을 불러오는 중...</div>

    <div v-else-if="products.length > 0" class="product-list">
      <div v-for="product in products" :key="product.id" class="product-card">

        <div class="card-header">
          <div class="title-area">
            <span class="bank-name">{{ product.kor_co_nm }}</span>
            <h3 class="product-name">{{ product.fin_prdt_nm }}</h3>
          </div>

          <!-- ✅ 카드 상단 오른쪽에 저장 상태 배지 느낌 -->
          <span class="badge" :class="{ on: savedCodes.has(product.fin_prdt_cd) }">
            {{ savedCodes.has(product.fin_prdt_cd) ? '저장됨' : '미저장' }}
          </span>
        </div>

        <hr class="divider" />

        <div class="options-container">
          <p class="option-title">기간별 금리 (최고 우대)</p>

          <table class="option-table">
            <thead>
              <tr>
                <th>기간</th>
                <th>금리 유형</th>
                <th>기본 금리</th>
                <th>최고 금리</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="opt in product.options" :key="opt.id">
                <td>{{ opt.save_trm }}개월</td>
                <td>{{ opt.intr_rate_type_nm }}</td>
                <td>{{ opt.intr_rate }}%</td>
                <td class="highlight">{{ opt.intr_rate2 }}%</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- ✅ 버튼을 카드 하단에 정렬 -->
        <div class="actions">
          <button class="ghost" @click="goDetail(product)">상세보기</button>
          <button
            class="primary"
            :class="{ saved: savedCodes.has(product.fin_prdt_cd) }"
            @click="toggleSave(product)"
          >
            {{ savedCodes.has(product.fin_prdt_cd) ? '저장 해제' : '저장' }}
          </button>
        </div>
      </div>
    </div>

    <div v-else class="loading">조건에 맞는 상품이 없습니다.</div>
  </div>
</template>

<style scoped>
.container { max-width: 1100px; margin: 0 auto; padding: 40px 20px; }
.page-title { text-align: center; font-size: 2rem; font-weight: 900; margin-bottom: 20px; color: #333; }

.panel {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 18px;
}
.row { display: flex; gap: 12px; align-items: flex-end; flex-wrap: wrap; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 12px; color: #666; font-weight: 800; }
.field select, .field input {
  border: 1px solid #ddd;
  border-radius: 10px;
  padding: 8px 10px;
  min-width: 160px;
}
.field.search input { min-width: 220px; }
.btns { display: flex; gap: 8px; }
.primary, .ghost {
  border: 1px solid #ddd;
  border-radius: 10px;
  padding: 10px 14px;
  font-weight: 900;
  cursor: pointer;
  background: #fff;
}
.ghost { background: #f8f9fa; border-color: #eee; }
.hint { margin-top: 10px; color: #777; font-size: 0.92rem; }

.product-list { display: flex; flex-direction: column; gap: 30px; }
.product-card {
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  background: white;
  transition: transform 0.2s;
}
.product-card:hover { transform: translateY(-3px); border-color: #42b983; }

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}
.title-area { display: flex; flex-direction: column; gap: 4px; }
.bank-name { font-size: 0.9rem; color: #666; font-weight: 800; }
.product-name { font-size: 1.4rem; font-weight: 1000; color: #2c3e50; margin: 0; }

.badge {
  border: 1px solid #ddd;
  border-radius: 999px;
  padding: 6px 10px;
  font-weight: 1000;
  font-size: 0.85rem;
  color: #777;
  background: #fff;
}
.badge.on {
  border-color: #42b983;
  color: #42b983;
}

.divider { border: 0; height: 1px; background: #eee; margin: 20px 0; }

.options-container { background-color: #f8f9fa; padding: 16px; border-radius: 8px; }
.option-title { font-size: 0.95rem; font-weight: 1000; margin-bottom: 10px; color: #555; }

.option-table { width: 100%; text-align: left; border-collapse: collapse; font-size: 0.9rem; }
.option-table th { color: #888; font-weight: 900; padding: 8px; border-bottom: 1px solid #ddd; }
.option-table td { padding: 8px; border-bottom: 1px solid #eee; color: #333; }
.option-table tr:last-child td { border-bottom: none; }
.highlight { color: #d63031; font-weight: 1000; }

.actions {
  margin-top: 16px;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  align-items: center;
}
.primary.saved {
  border-color: #42b983;
  color: #42b983;
}
.loading { text-align: center; margin-top: 50px; color: #888; }
</style>
