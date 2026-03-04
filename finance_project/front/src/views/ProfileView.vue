<template>
  <div class="page">
    <h2>마이페이지</h2>

    <div class="tabs">
      <button :class="{ on: tab === 'edit' }" @click="tab = 'edit'">프로필 편집</button>
      <button :class="{ on: tab === 'products' }" @click="tab = 'products'">찜한 상품</button>
    </div>

    <!-- 공통 메시지 -->
    <p v-if="msg" class="msg">{{ msg }}</p>

    <!-- 프로필 편집 -->
    <section v-if="tab === 'edit'" class="card">
      <h3>회원 정보</h3>

      <div v-if="loading">불러오는 중...</div>

      <div v-else class="form">
        <div class="row">
          <label>아이디</label>
          <div>{{ profile.username }}</div>
        </div>

        <div class="row">
          <label>이메일</label>
          <div>{{ profile.email }}</div>
        </div>

        <div class="row">
          <label>이름</label>
          <div class="inline">
            <input v-model="form.first_name" placeholder="first name" />
            <input v-model="form.last_name" placeholder="last name" />
          </div>
        </div>

        <div class="row">
          <label>닉네임</label>
          <input v-model="form.nickname" />
        </div>

        <div class="row">
          <label>나이</label>
          <input v-model.number="form.age" type="number" min="0" />
        </div>

        <div class="row">
          <label>자산</label>
          <input v-model.number="form.money" type="number" min="0" />
        </div>

        <div class="row">
          <label>연봉</label>
          <input v-model.number="form.salary" type="number" min="0" />
        </div>

        <button class="primary" @click="save" :disabled="saving">
          {{ saving ? '저장 중...' : '저장' }}
        </button>
      </div>
    </section>

    <!-- 가입상품 확인 -->
    <section v-else class="card">
      <h3>찜한 상품</h3>

      <div v-if="loading">불러오는 중...</div>

      <div v-else>
        <div v-if="!profile.joined_products || profile.joined_products.length === 0">
          아직 찜한 상품이 없습니다.
        </div>

        <div v-else>
          <ul class="list">
            <li v-for="p in profile.joined_products" :key="p.fin_prdt_cd" class="item">
              <div class="title">{{ p.fin_prdt_nm }}</div>
              <div class="sub">{{ p.kor_co_nm }}</div>
              <div class="rate">최고 우대금리: {{ p.max_intr_rate2 }}%</div>
            </li>
          </ul>

          <div class="chart">
            <BarChart
              v-if="profile.chart"
              :labels="profile.chart.labels"
              :values="profile.chart.values"
              title="가입상품 최고 우대금리(%)"
            />
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import BarChart from '@/components/BarChart.vue'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

const tab = ref('edit')
const loading = ref(true)
const saving = ref(false)
const msg = ref('')

const profile = reactive({})

const form = reactive({
  first_name: '',
  last_name: '',
  nickname: '',
  age: 0,
  money: 0,
  salary: 0,
})

function guardLogin() {
  if (!auth.isLogin) {
    msg.value = '로그인이 필요합니다.'
    router.push({ name: 'LogInView' }).catch(() => router.push('/'))
    return false
  }
  return true
}

async function fetchProfile() {
  if (!guardLogin()) return

  loading.value = true
  msg.value = ''
  try {
    const res = await axios({
      method: 'get',
      url: `${auth.API_URL}/accounts/me/`,
      headers: auth.authHeader,
    })

    Object.assign(profile, res.data)

    // 폼 채우기
    form.first_name = profile.first_name || ''
    form.last_name = profile.last_name || ''
    form.nickname = profile.nickname || ''
    form.age = profile.age ?? 0
    form.money = profile.money ?? 0
    form.salary = profile.salary ?? 0
  } catch (err) {
    console.log(err?.response?.status, err?.response?.data)
    msg.value = '프로필을 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

async function save() {
  if (!guardLogin()) return

  saving.value = true
  msg.value = ''
  try {
    const res = await axios({
      method: 'patch',
      url: `${auth.API_URL}/accounts/me/`,
      data: form,
      headers: auth.authHeader,
    })

    Object.assign(profile, res.data)

    // auth store의 user도 최신화(원하면)
    auth.user = res.data

    msg.value = '저장 완료!'
  } catch (err) {
    console.log(err?.response?.status, err?.response?.data)
    msg.value = '저장에 실패했습니다. 입력값을 확인하세요.'
  } finally {
    saving.value = false
  }
}

onMounted(fetchProfile)
</script>

<style scoped>
.page { max-width: 960px; margin: 0 auto; padding: 16px; }
.tabs { display: flex; gap: 8px; margin: 12px 0; }
.tabs button { padding: 8px 12px; border-radius: 10px; border: 1px solid #ddd; background: white; cursor: pointer; }
.tabs button.on { font-weight: 800; }
.card { border: 1px solid #eee; border-radius: 14px; padding: 16px; }
.form { display: grid; gap: 10px; }
.row { display: grid; grid-template-columns: 120px 1fr; gap: 10px; align-items: center; }
.inline { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
input { padding: 8px 10px; border: 1px solid #ddd; border-radius: 10px; }
.primary { margin-top: 10px; padding: 10px 14px; border: 1px solid #ddd; border-radius: 12px; background: #fff; cursor: pointer; }
.msg { margin: 8px 0 0; color: #444; }
.list { list-style: none; padding: 0; margin: 0; display: grid; gap: 10px; }
.item { border: 1px solid #eee; border-radius: 12px; padding: 12px; }
.title { font-weight: 800; }
.sub { color: #666; font-size: 0.9rem; margin-top: 2px; }
.rate { margin-top: 6px; }
.chart { margin-top: 16px; }
</style>
