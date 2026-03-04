<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const router = useRouter()
const store = useAuthStore()

/* ---------------------------
   ✅ 오늘의 팁(페이드 등장)
--------------------------- */
const tips = [
  '💰 첫 월급의 50%는 무조건 저축하는 습관을 들여보세요!',
  '📌 소비 전 “필요 vs 욕구”를 10초만 구분해보면 지출이 줄어요.',
  '🧾 고정지출(통신/구독)을 먼저 줄이면 절약이 쉬워요.',
  '🏦 우대금리 조건(급여이체/자동이체)을 체크하면 체감수익이 커져요.',
  '📈 적금은 “목표 금액/기간”부터 정하면 선택이 쉬워요.',
]
const todayTip = ref('')
const showTip = ref(false)

/* ---------------------------
   ✅ 예적금 / 커뮤니티 / 시세 데이터
--------------------------- */
const loading = ref(false)
const items = ref([])

const loadingPosts = ref(false)
const posts = ref([])

const loadingSpot = ref(false)
const spotList = ref([])

const topDeposits = computed(() => (Array.isArray(items.value) ? items.value.slice(0, 3) : []))
const latestPosts = computed(() => (Array.isArray(posts.value) ? posts.value.slice(0, 3) : []))

const formatDate = (iso) => (iso ? String(iso).slice(0, 10) : '')

const pickRate = (p) => {
  const candidates = [p?.intr_rate2, p?.max_intr_rate, p?.intr_rate, p?.highest_rate, p?.best_rate]
  const n = candidates.find((v) => typeof v === 'number')
  return typeof n === 'number' ? n : null
}

const goDepositDetail = (p) => {
  if (p?.fin_prdt_cd) {
    router.push({ name: 'DepositDetailView', params: { fin_prdt_cd: p.fin_prdt_cd } })
  } else {
    router.push({ name: 'DepositView' })
  }
}

const fetchDeposits = async () => {
  loading.value = true
  try {
    const res = await axios.get(`${store.API_URL}/api/v1/products/deposit/`)
    items.value = Array.isArray(res.data) ? res.data.slice(0, 6) : []
  } catch (err) {
    console.log('예적금 미리보기 로드 실패', err)
    items.value = []
  } finally {
    loading.value = false
  }
}

const fetchCommunity = async () => {
  loadingPosts.value = true
  try {
    const res = await axios.get(`${store.API_URL}/api/v1/community/posts/`)
    posts.value = Array.isArray(res.data) ? res.data : []
  } catch (err) {
    console.log('커뮤니티 최신글 로드 실패', err)
    posts.value = []
  } finally {
    loadingPosts.value = false
  }
}

const fetchSpot = async () => {
  loadingSpot.value = true
  try {
    const res = await axios.get(`${store.API_URL}/api/v1/products/spot/`)
    spotList.value = Array.isArray(res.data) ? res.data : []
  } catch (err) {
    console.log('금/은 시세 로드 실패', err)
    spotList.value = []
  } finally {
    loadingSpot.value = false
  }
}

const latestSpotOf = (name) => {
  const arr = (spotList.value || []).filter((x) => x.item_name === name)
  if (arr.length === 0) return null
  return arr.reduce((a, b) => (a.base_date > b.base_date ? a : b))
}

const goldSpot = computed(() => latestSpotOf('Gold'))
const silverSpot = computed(() => latestSpotOf('Silver'))

const spotBaseDate = computed(() => {
  const g = goldSpot.value?.base_date
  const s = silverSpot.value?.base_date
  if (!g && !s) return ''
  if (g && !s) return g
  if (!g && s) return s
  return g > s ? g : s
})

/* ---------------------------
   ✅ 목표 달성 계산기 로직(그대로 유지)
--------------------------- */
const calcAmount = ref(500000) // 매월 저축액
const calcMonths = ref(12) // 저축 기간
const calcRate = ref(4.0) // 이자율

const expectedResult = computed(() => {
  const p = calcAmount.value
  const n = calcMonths.value
  const r = calcRate.value / 100 / 12 // 월 이자율

  // 적금 미래가치 공식 (단리 기준 간단 계산)
  const principal = p * n
  const interest = p * (n * (n + 1) / 2) * r
  const total = Math.floor(principal + interest)

  return total.toLocaleString()
})

/* ---------------------------
   ✅ onMounted: 팁 선택 + 페이드 등장 + 기존 데이터 로드
--------------------------- */
onMounted(async () => {
  // 1) 랜덤 팁 선택
  todayTip.value = tips[Math.floor(Math.random() * tips.length)]

  // 2) ✅ 팁을 약간 늦게 페이드로 등장
  setTimeout(() => {
    showTip.value = true
  }, 350)

  // 3) 기존 로그인 유저 정보 확인 로직
  if (store.isLogin && !store.user?.nickname && typeof store.fetchMe === 'function') {
    await store.fetchMe()
  }

  // 4) 기존 데이터들(예적금, 커뮤니티, 시세) 한꺼번에 가져오기
  await Promise.all([fetchDeposits(), fetchCommunity(), fetchSpot()])
})
</script>


<template>
  <main class="home">
    <section class="hero">
      <p v-if="store.isLogin && store.user?.nickname" class="welcome">
        안녕하세요, <b>{{ store.user.nickname }}</b>님!
      </p>

      <h1 class="title">
        <span class="title-weak">사회초년생의</span>
        <span class="title-strong">첫 적금 메이트</span>
      </h1>

      <p class="subtitle">금융 상품 비교부터 <b>금/은 시세</b>까지 한눈에!</p>

      <transition name="fade-up">
        <div class="tip-bar" v-if="showTip && todayTip">
          <div class="tip-content">
            <span class="tip-badge">💡 오늘의 팁</span>
            <p class="tip-text">{{ todayTip }}</p>
          </div>
        </div>
      </transition>
    </section>

    <!-- ✅ 6개 바로가기 배너 (첫 화면 하단) -->
<section class="banner-grid">
  <RouterLink class="banner b-orange" :to="{ name: 'DepositView' }">
    <div class="icon-box">🏦</div>
    <div class="banner-text">
      <div class="banner-title">예적금 조회</div>
      <div class="banner-desc">예금·적금 상품 한눈에</div>
    </div>
  </RouterLink>

  <RouterLink class="banner b-yellow" :to="{ name: 'GoldView' }">
    <div class="icon-box">🥇</div>
    <div class="banner-text">
      <div class="banner-title">금/은 시세</div>
      <div class="banner-desc">실시간 현물 시세 확인</div>
    </div>
  </RouterLink>

  <RouterLink class="banner b-blue" :to="{ name: 'MapView' }">
    <div class="icon-box">🗺️</div>
    <div class="banner-text">
      <div class="banner-title">지도 조회</div>
      <div class="banner-desc">내 근처 은행 찾기</div>
    </div>
  </RouterLink>

  <RouterLink class="banner b-peach" :to="{ name: 'YoutubeSearchView' }">
    <div class="icon-box">📺</div>
    <div class="banner-text">
      <div class="banner-title">유튜브</div>
      <div class="banner-desc">관심 종목 영상 보기</div>
    </div>
  </RouterLink>

  <RouterLink class="banner b-sky" :to="{ name: 'CommunityListView' }">
    <div class="icon-box">💬</div>
    <div class="banner-text">
      <div class="banner-title">커뮤니티</div>
      <div class="banner-desc">정보 공유 · 후기 · 질문</div>
    </div>
  </RouterLink>

  <RouterLink class="banner b-purple" :to="{ name: 'AIRecommendView' }">
    <div class="icon-box">🤖</div>
    <div class="banner-text">
      <div class="banner-title">AI</div>
      <div class="banner-desc">사회초년생 맞춤 AI 추천</div>
    </div>
  </RouterLink>
</section>


    <section class="bottom">
      <div class="summary-grid">
        <!-- 1) 오늘의 예적금 미리보기 -->
        <div class="summary-card">
          <div class="summary-head">
            <div class="summary-title">오늘의 예적금 미리보기</div>
            <RouterLink class="summary-link" :to="{ name: 'DepositView' }">전체 보기 →</RouterLink>
          </div>

          <div v-if="loading" class="mini-loading">불러오는 중...</div>
          <div v-else-if="topDeposits.length === 0" class="mini-empty">
            아직 불러올 상품이 없어요. <span class="mini-hint">예적금 페이지에서 확인해 주세요!</span>
          </div>

          <div v-else class="deposit-mini">
            <button
              v-for="p in topDeposits"
              :key="p.fin_prdt_cd || p.id || p.fin_prdt_nm"
              class="deposit-row"
              @click="goDepositDetail(p)"
            >
              <div class="deposit-left">
                <div class="deposit-name">{{ p.fin_prdt_nm || p.product_name || '예적금 상품' }}</div>
                <div class="deposit-bank">{{ p.kor_co_nm || p.bank_name || '은행' }}</div>
              </div>

              <div class="deposit-right">
                <span v-if="pickRate(p) !== null" class="rate-badge">최대 {{ pickRate(p) }}%</span>
                <span v-else class="rate-badge rate-badge--muted">상세 보기</span>
              </div>
            </button>
          </div>
        </div>

        <!-- ✅ 2) (AI 맞춤 추천 카드 완전 삭제) → 목표 달성 계산기 배치 -->
        <div class="summary-card calc-panel">
          <div class="summary-head">
            <div class="summary-title">💰 목표 달성 계산기</div>
          </div>

          <div class="calc-body">
            <div class="calc-input-row">
              <label>매달 <b>{{ (calcAmount / 10000).toLocaleString() }}만</b>원씩</label>
              <input type="range" v-model.number="calcAmount" min="100000" max="2000000" step="100000" />
            </div>

            <div class="calc-input-row">
              <label><b>{{ calcMonths }}개월</b> 동안 모으면?</label>
              <input type="range" v-model.number="calcMonths" min="6" max="36" step="6" />
            </div>

            <div class="calc-result-box">
              <span class="result-label">만기 예상 수령액(세전)</span>
              <div class="result-value">약 <span>{{ expectedResult }}</span>원</div>
            </div>
          </div>
        </div>

        <!-- 3) 금/은 시세 -->
        <div class="summary-card">
          <div class="summary-head">
            <div class="summary-title">금/은 시세</div>
            <RouterLink class="summary-link" :to="{ name: 'GoldView' }">자세히 →</RouterLink>
          </div>

          <div v-if="loadingSpot" class="mini-loading">불러오는 중...</div>

          <div v-else class="spot-mini">
            <div class="spot-top">
              <span class="spot-date" v-if="spotBaseDate">기준일: {{ spotBaseDate }}</span>
              <span class="spot-date" v-else>데이터 없음</span>
            </div>

            <div class="spot-row">
              <span class="spot-label">🟡 금 <span class="text-xs">/oz</span></span>
              <span class="spot-price">
                <span>$</span>
                {{ goldSpot ? Number(goldSpot.price).toLocaleString() : '—' }}
              </span>
            </div>

            <div class="spot-row">
              <span class="spot-label">⚪ 은 <span class="text-xs">/oz</span></span>
              <span class="spot-price">
                <span>$</span>
                {{ silverSpot ? Number(silverSpot.price).toLocaleString() : '—' }}
              </span>
            </div>

            <RouterLink class="cta cta--mini" :to="{ name: 'GoldView' }">시세 페이지로 →</RouterLink>
          </div>
        </div>
      </div>

      <!-- 아래 2단 -->
      <div class="dash-grid">
        <!-- 커뮤니티 최신글 -->
        <div class="panel">
          <div class="panel-head">
            <div class="panel-title">커뮤니티 최신글</div>
            <RouterLink class="panel-link" :to="{ name: 'CommunityListView' }">더보기 →</RouterLink>
          </div>

          <div v-if="loadingPosts" class="mini-loading">불러오는 중...</div>
          <div v-else-if="latestPosts.length === 0" class="mini-empty">아직 게시글이 없어요.</div>

          <div v-else class="post-list">
            <button
              v-for="p in latestPosts"
              :key="p.id"
              class="post-row"
              @click="router.push({ name: 'CommunityDetailView', params: { id: p.id } })"
            >
              <div class="post-title">{{ p.title }}</div>
              <div class="post-meta">
                <span>{{ p.author_nickname || p.author_username }}</span>
                <span class="dot">·</span>
                <span>{{ formatDate(p.created_at) }}</span>
              </div>
            </button>
          </div>
        </div>

        <!-- 빠른 시작 가이드 -->
        <div class="panel">
          <div class="panel-head">
            <div class="panel-title">빠른 시작</div>
          </div>

          <ol class="steps">
            <li class="step">
              <span class="step-ico" aria-hidden="true">✅</span>
              <div class="step-body">
                <div class="step-title">회원가입 / 로그인</div>
                <div class="step-desc">기능 이용을 위한 기본 설정</div>
              </div>
              <RouterLink v-if="!store.isLogin" class="step-link" :to="{ name: 'LogInView' }">로그인 →</RouterLink>
              <span v-else class="step-done">완료</span>
            </li>

            <li class="step">
              <span class="step-ico" aria-hidden="true">🔎</span>
              <div class="step-body">
                <div class="step-title">상품 탐색 & 비교/찜</div>
                <div class="step-desc">검색/필터/정렬로 빠르게 선택</div>
              </div>
              <RouterLink class="step-link" :to="{ name: 'DepositView' }">탐색 →</RouterLink>
            </li>

            <li class="step">
              <span class="step-ico" aria-hidden="true">🤖</span>
              <div class="step-body">
                <div class="step-title">AI 추천 받기</div>
                <div class="step-desc">추천 + 사유로 선택을 돕기</div>
              </div>
              <RouterLink class="step-link" :to="{ name: 'AIRecommendView' }">추천 →</RouterLink>
            </li>
          </ol>
        </div>

        <!-- ✅ 기존 맨 아래 목표달성 계산기 패널은 이제 "요약 카드 영역"으로 이동했으므로 여기서는 삭제 -->
      </div>
    </section>

    <!-- ✅ AI 플로팅 버튼 -->
    <button
      class="ai-fab"
      type="button"
      aria-label="AI 맞춤 추천 바로가기"
      @click="router.push({ name: 'AIRecommendView' })"
    >
      🤖
    </button>



  </main>
</template>



<style scoped>
.home {
  min-height: calc(100vh - 56px);
  padding: 34px 18px 44px;
}





.hero {
  position: relative;
  max-width: 980px;
  margin: 0 auto 8px;        /* ✅ 더 줄임 */
  padding: 20px 18px 6px;    /* ✅ 위/아래 패딩 더 줄임 */
  text-align: center;

  min-height: 62vh;          /* ✅ 70 → 62로 확 줄여서 배너가 위로 붙음 */
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  gap: 8px;                  /* ✅ 문구 덩어리 간격 살짝 줄임 */
}


/* 좌/우 일러스트 */
.hero::before,
.hero::after {
  content: "";
  position: absolute;
  top: -8px;
  width: 360px;
  height: 220px;
  background-repeat: no-repeat;
  background-size: contain;
  opacity: 0.92;
  pointer-events: none;
}

.hero::before {
  left: -70px;
  background-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D'http%3A//www.w3.org/2000/svg'%20width%3D'420'%20height%3D'260'%20viewBox%3D'0%200%20420%20260'%3E%0A%20%20%3Cdefs%3E%0A%20%20%20%20%3ClinearGradient%20id%3D'sleeve'%20x1%3D'0'%20y1%3D'0'%20x2%3D'1'%20y2%3D'1'%3E%0A%20%20%20%20%20%20%3Cstop%20offset%3D'0'%20stop-color%3D'rgb(120%2C190%2C255)'/%3E%0A%20%20%20%20%20%20%3Cstop%20offset%3D'1'%20stop-color%3D'rgb(70%2C130%2C220)'/%3E%0A%20%20%20%20%3C/linearGradient%3E%0A%20%20%3C/defs%3E%0A%20%20%3Ccircle%20cx%3D'135'%20cy%3D'115'%20r%3D'46'%20fill%3D'rgb(255%2C210%2C110)'%20stroke%3D'rgb(237%2C176%2C70)'%20stroke-width%3D'10'/%3E%0A%20%20%3Ccircle%20cx%3D'135'%20cy%3D'115'%20r%3D'24'%20fill%3D'none'%20stroke%3D'rgb(237%2C176%2C70)'%20stroke-width%3D'6'/%3E%0A%20%20%3Crect%20x%3D'10'%20y%3D'150'%20width%3D'170'%20height%3D'70'%20rx%3D'20'%20fill%3D'url(%23sleeve)'/%3E%0A%20%20%3Cpath%20d%3D'M140%20150%20c40%200%2070%2016%2070%2036%20s-30%2036-70%2036%20h-35%20c-20%200-38-9-38-20%20s12-22%2028-24%20c6-1%2010-3%2012-7%20c4-12%2016-21%2033-21%20z'%0A%20%20%20%20%20%20fill%3D'rgb(252%2C214%2C181)'%20stroke%3D'rgb(226%2C170%2C136)'%20stroke-width%3D'6'%20stroke-linejoin%3D'round'/%3E%0A%20%20%3Crect%20x%3D'230'%20y%3D'52'%20width%3D'74'%20height%3D'42'%20rx%3D'10'%20fill%3D'rgb(214%2C255%2C226)'%20stroke%3D'rgb(150%2C220%2C175)'%20stroke-width%3D'5'%20opacity%3D'0.9'/%3E%0A%20%20%3Ccircle%20cx%3D'267'%20cy%3D'73'%20r%3D'10'%20fill%3D'rgb(150%2C220%2C175)'%20opacity%3D'0.6'/%3E%0A%3C/svg%3E");
}

.hero::after {
  right: -70px;
  background-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D'http%3A//www.w3.org/2000/svg'%20width%3D'420'%20height%3D'260'%20viewBox%3D'0%200%20420%20260'%3E%0A%20%20%3Cpath%20d%3D'M120%2085%20L210%2035%20L300%2085%20Z'%20fill%3D'rgb(232%2C236%2C246)'%20stroke%3D'rgb(206%2C214%2C230)'%20stroke-width%3D'6'%20stroke-linejoin%3D'round'/%3E%0A%20%20%3Crect%20x%3D'120'%20y%3D'85'%20width%3D'180'%20height%3D'120'%20rx%3D'18'%20fill%3D'rgb(252%2C253%2C255)'%20stroke%3D'rgb(206%2C214%2C230)'%20stroke-width%3D'6'/%3E%0A%20%20%3Ccircle%20cx%3D'325'%20cy%3D'165'%20r%3D'28'%20fill%3D'rgb(255%2C210%2C110)'%20stroke%3D'rgb(237%2C176%2C70)'%20stroke-width%3D'8'/%3E%0A%20%20%3Ccircle%20cx%3D'360'%20cy%3D'185'%20r%3D'22'%20fill%3D'rgb(255%2C210%2C110)'%20stroke%3D'rgb(237%2C176%2C70)'%20stroke-width%3D'7'/%3E%0A%20%20%3Cpath%20d%3D'M334%2078%20l8%2016%20l16%208%20l-16%208%20l-8%2016%20l-8-16%20l-16-8%20l16-8z'%20fill%3D'rgb(132%2C202%2C255)'%20opacity%3D'0.9'/%3E%0A%3C/svg%3E");
}



.welcome {
  margin: 0 auto;
  display: inline-flex;
  align-items: center;
  gap: 6px;

  /* ✅ 흰색 배경(알약) 제거 */
  background: transparent;
  border: none;
  box-shadow: none;
  padding: 0;

  font-size: 0.95rem;
  color: rgba(49, 34, 20, 0.75);
  opacity: 0.9;

}



.title {
  margin: 0;
  line-height: 1.12;
  letter-spacing: -0.8px;
  display: inline-flex;
  flex-direction: column;
  gap: 6px;
}

.title-weak {
  font-size: 1.25rem;
  font-weight: 850;
  color: rgba(49, 34, 20, 0.7);
}

.title-strong {
  font-size: clamp(2rem, 3.4vw, 3.1rem);
  font-weight: 950;
  color: #223a5e;
}

.subtitle {
  margin: 0; /* ✅ 기존 10px 상단 여백 제거하고 hero gap으로 통일 */
  font-size: 0.95rem;
  color: rgba(49, 34, 20, 0.62);
}


.subtitle b {
  color: rgba(34, 58, 94, 0.9);
}

.banner-grid {
  width: 100%;
  max-width: 980px;
  margin: 6px auto 0;       /* ✅ 18 → 10 : 배너를 위로 당김 */
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 0px !important;     /* ✅ 위쪽 여백 제거 */
  transform: translateY(-40px);                  /* ✅ 14 → 12 : 살짝 더 촘촘하게 */
}



.banner {
  display: grid;
  grid-template-columns: 54px 1fr; /* ✅ 아이콘 칸 살짝 줄여서 텍스트 당김 */
  align-items: center;
  column-gap: 12px;

  padding: 14px 16px;        /* ✅ 18px → 14/16 : 내부 여백 줄여 균형 */
  border-radius: 20px;

  border: 1px solid rgba(49, 34, 20, 0.10);
  box-shadow: 0 10px 26px rgba(49, 34, 20, 0.10);

  text-decoration: none;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
  min-height: 76px;          /* ✅ 카드 높이를 통일해서 들쭉날쭉 방지 */
}



.banner:hover {
  transform: translateY(-5px);
  box-shadow: 0 16px 34px rgba(49, 34, 20, 0.14);
  border-color: rgba(34, 58, 94, 0.22);
}

.icon-box {
  width: 46px;               /* ✅ 52 → 46 : 너무 커서 어색한 느낌 줄임 */
  height: 46px;
  border-radius: 14px;

  display: grid;
  place-items: center;
  font-size: 1.35rem;        /* ✅ 살짝 줄여서 통일감 */

  justify-self: start;

  background: rgba(255, 255, 255, 0.55);
  border: 1px solid rgba(49, 34, 20, 0.10);
}


/* .banner-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
} */

.banner-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
  text-align: left;        /* ✅ 모두 왼쪽 정렬 */
  justify-self: start;
}

.banner-title {
  font-weight: 950;
  letter-spacing: -0.2px;
  color: rgba(49, 34, 20, 0.92);
  line-height: 1.15;       /* ✅ 줄간격 통일 */
}

.banner-desc {
  font-size: 0.88rem;
  color: rgba(49, 34, 20, 0.58);
  line-height: 1.15;       /* ✅ AI 배너만 달라 보이던 문제 해결 */
}


.banner--deposit {
  --accent-soft: rgba(255, 197, 120, 0.62);
}

.banner--metal {
  --accent-soft: rgba(255, 223, 128, 0.68);
}

.banner--map {
  --accent-soft: rgba(168, 214, 255, 0.72);
}

.banner--youtube {
  --accent-soft: rgba(255, 199, 181, 0.68);
}

.banner--community {
  --accent-soft: rgba(205, 199, 255, 0.70);
}

.banner--ai {
  --accent-soft: rgba(170, 214, 255, 0.70);
}

/* 하단 대시보드 */
/* .bottom {
  max-width: 980px;
  margin: 22px auto 0;
  padding-top: 8px;
} */

.bottom {
  max-width: 980px;
  margin: 0 auto 0; /* ✅ hero가 화면 대부분 먹도록 아래 여백 제거 */
  padding-top: 48px; /* ✅ 스크롤 내려야 카드가 등장하는 느낌 */
}


.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-top: 14px;
}

.summary-card {
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.74);
  border: 1px solid rgba(49, 34, 20, 0.10);
  box-shadow: 0 12px 28px rgba(49, 34, 20, 0.10);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  padding: 16px 16px 14px;
}

.summary-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.summary-title {
  font-weight: 950;
  letter-spacing: -0.3px;
  color: rgba(49, 34, 20, 0.92);
}

.summary-link,
.panel-link {
  font-weight: 900;
  font-size: 0.88rem;
  color: rgba(34, 58, 94, 0.92);
}

.summary-desc {
  margin: 6px 0 10px;
  color: rgba(49, 34, 20, 0.64);
  font-size: 0.92rem;
}

.summary-note {
  margin-top: 10px;
  font-size: 0.82rem;
  color: rgba(49, 34, 20, 0.52);
}

.cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 12px;
  border-radius: 14px;
  font-weight: 950;
  border: 1px solid rgba(34, 58, 94, 0.16);
  background: rgba(168, 214, 255, 0.42);
  color: rgba(34, 58, 94, 0.95);
  box-shadow: 0 10px 22px rgba(49, 34, 20, 0.08);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.cta:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 30px rgba(49, 34, 20, 0.12);
}

.cta--mini {
  margin-top: 10px;
  width: 100%;
}

.mini-loading,
.mini-empty {
  padding: 10px 0 4px;
  color: rgba(49, 34, 20, 0.62);
  font-size: 0.92rem;
}

.mini-hint {
  color: rgba(34, 58, 94, 0.88);
  font-weight: 800;
}

.deposit-mini {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.deposit-row {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px;
  border-radius: 14px;
  background: rgba(255, 246, 232, 0.55);
  border: 1px solid rgba(49, 34, 20, 0.10);
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.deposit-row:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 26px rgba(49, 34, 20, 0.10);
}

.deposit-left {
  text-align: left;
}

.deposit-name {
  font-weight: 950;
  letter-spacing: -0.2px;
  color: rgba(49, 34, 20, 0.92);
  font-size: 0.94rem;
}

.deposit-bank {
  font-size: 0.84rem;
  color: rgba(49, 34, 20, 0.58);
  margin-top: 2px;
}

.rate-badge {
  font-weight: 950;
  font-size: 0.84rem;
  padding: 7px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255, 197, 120, 0.55);
  background: rgba(255, 197, 120, 0.42);
  color: rgba(49, 34, 20, 0.92);
  white-space: nowrap;
}

.rate-badge--muted {
  border-color: rgba(49, 34, 20, 0.10);
  background: rgba(255, 255, 255, 0.55);
  color: rgba(49, 34, 20, 0.70);
}

/* 금/은 미니 */
.spot-mini {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.spot-top {
  display: flex;
  justify-content: flex-end;
}

.spot-date {
  font-size: 0.82rem;
  color: rgba(49, 34, 20, 0.55);
  font-weight: 800;
}

.spot-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid rgba(49, 34, 20, 0.10);
  background: rgba(255, 255, 255, 0.60);
}

.spot-label {
  font-weight: 950;
  color: rgba(49, 34, 20, 0.90);
}

.spot-price {
  font-weight: 950;
  color: rgba(34, 58, 94, 0.92);
}

/* 대시보드 그리드 조정 (패널들이 꽉 차 보이게) */
.dash-grid {
  margin-top: 16px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  /* 유동적으로 꽉 채움 */
  gap: 16px;
}

/* 계산기 전용 스타일 */
.calc-panel {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(255, 246, 232, 0.9)) !important;
}

.calc-body {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 10px;
}

.calc-input-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.calc-input-row label {
  font-size: 0.95rem;
  color: #5a4b3c;
  font-weight: 700;
}

.calc-input-row label b {
  color: #ff9f43;
}

.calc-result-box {
  padding: 20px;
  background: white;
  border-radius: 16px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

.result-value span {
  color: #ff9f43;
  font-size: 1.5rem;
  font-weight: 900;
}

.panel {
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.74);
  border: 1px solid rgba(49, 34, 20, 0.10);
  box-shadow: 0 12px 28px rgba(49, 34, 20, 0.10);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  padding: 16px;
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.panel-title {
  font-weight: 950;
  letter-spacing: -0.3px;
  color: rgba(49, 34, 20, 0.92);
}

.post-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.post-row {
  text-align: left;
  width: 100%;
  border: 1px solid rgba(49, 34, 20, 0.10);
  background: rgba(255, 255, 255, 0.60);
  border-radius: 14px;
  padding: 12px;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.post-row:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 26px rgba(49, 34, 20, 0.10);
}

.post-title {
  font-weight: 950;
  letter-spacing: -0.2px;
  color: rgba(49, 34, 20, 0.92);
  margin-bottom: 6px;
}

.post-meta {
  font-size: 0.84rem;
  color: rgba(49, 34, 20, 0.60);
  display: flex;
  align-items: center;
  gap: 8px;
}

.dot {
  opacity: 0.6;
}

.steps {
  list-style: none;
  padding: 0;
  margin: 6px 0 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.step {
  display: grid;
  grid-template-columns: 34px 1fr auto;
  gap: 10px;
  align-items: center;
  padding: 12px;
  border-radius: 14px;
  border: 1px solid rgba(49, 34, 20, 0.10);
  background: rgba(255, 246, 232, 0.52);
}

.step-ico {
  font-size: 1.1rem;
}

.step-title {
  font-weight: 950;
  color: rgba(49, 34, 20, 0.92);
}

.step-desc {
  font-size: 0.84rem;
  color: rgba(49, 34, 20, 0.58);
  margin-top: 2px;
}

.step-link {
  font-weight: 950;
  font-size: 0.86rem;
  color: rgba(34, 58, 94, 0.92);
  padding: 8px 10px;
  border-radius: 12px;
  background: rgba(168, 214, 255, 0.38);
  border: 1px solid rgba(34, 58, 94, 0.14);
}

.step-done {
  font-weight: 950;
  font-size: 0.86rem;
  color: rgba(16, 122, 77, 0.92);
}

@media (max-width: 980px) {
  .hero::before {
    left: -120px;
    opacity: 0.65;
  }

  .hero::after {
    right: -120px;
    opacity: 0.65;
  }
}

@media (max-width: 820px) {
  .banner-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .hero::before,
  .hero::after {
    display: none;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }

  .dash-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .home {
    padding: 26px 14px 34px;
  }

  .banner-grid {
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .banner {
    padding: 16px;
  }
}



/* ✅ 오늘의 팁 바 디자인 추가 */
.tip-bar {
  max-width: 980px;
  margin: 0 auto 30px;
  /* 배너 그리드와의 간격 */
  padding: 0 10px;
  animation: fadeInDown 0.8s ease-out;
  /* 부드럽게 나타나는 효과 */
  margin-top: 22px;
}

.tip-content {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 14px 24px;
  background: rgba(255, 255, 255, 0.6);
  /* 반투명 흰색 */
  border: 1px solid rgba(255, 197, 120, 0.4);
  /* 연한 주황색 테두리 */
  border-radius: 99px;
  /* 알약 모양 */
  box-shadow: 0 6px 20px rgba(49, 34, 20, 0.05);
}

.tip-badge {
  background: #ff9f43;
  /* 포인트 오렌지 색상 */
  color: white;
  font-size: 0.8rem;
  font-weight: 900;
  padding: 4px 12px;
  border-radius: 12px;
  white-space: nowrap;
}

.tip-text {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: #5a4b3c;
  /* 진한 브라운 톤 */
  letter-spacing: -0.3px;
}

/* 나타나는 애니메이션 */
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 모바일 대응 */
@media (max-width: 600px) {
  .tip-content {
    padding: 10px 16px;
    flex-direction: column;
    text-align: center;
    border-radius: 20px;
  }
}


/* ✅ Tip fade-up transition */
.fade-up-enter-active {
  transition: opacity 0.35s ease, transform 0.35s ease;
}
.fade-up-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.fade-up-enter-to {
  opacity: 1;
  transform: translateY(0);
}


/* ✅ AI 플로팅 버튼(FAB) */
/* .ai-fab {
  position: fixed;
  right: 18px;
  bottom: 18px;
  width: 56px;
  height: 56px;
  border-radius: 999px;

  display: grid;
  place-items: center;

  font-size: 1.35rem;
  font-weight: 900;

  border: 1px solid rgba(34, 58, 94, 0.18);
  background: rgba(168, 214, 255, 0.70);
  color: rgba(34, 58, 94, 0.95);

  box-shadow: 0 14px 30px rgba(49, 34, 20, 0.16);
  cursor: pointer;
  z-index: 9999;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
} */


.ai-fab {
  position: fixed;
  right: 28px;   /* ✅ 더 안쪽 */
  bottom: 88px;  /* ✅ 더 위쪽 */

  width: 56px;
  height: 56px;
  border-radius: 999px;

  display: grid;
  place-items: center;

  font-size: 1.35rem;
  font-weight: 900;

  border: 1px solid rgba(34, 58, 94, 0.18);
  background: rgba(168, 214, 255, 0.70);
  color: rgba(34, 58, 94, 0.95);

  box-shadow: 0 14px 30px rgba(49, 34, 20, 0.16);
  cursor: pointer;
  z-index: 9999;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}


.ai-fab:hover {
  transform: translateY(-3px);
  box-shadow: 0 20px 36px rgba(49, 34, 20, 0.20);
}

.ai-fab:active {
  transform: translateY(-1px);
}

/* ✅ 첫 화면 하단 6개 배너 그리드 */
.banner-grid {
  width: 100%;
  max-width: 980px;
  margin: 26px auto 0;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.banner {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 18px;
  border-radius: 20px;

  border: 1px solid rgba(49, 34, 20, 0.10);
  box-shadow: 0 10px 26px rgba(49, 34, 20, 0.10);

  text-decoration: none;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.banner:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 34px rgba(49, 34, 20, 0.14);
}

.icon-box {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  font-size: 1.55rem;
  background: rgba(255, 255, 255, 0.55);
  border: 1px solid rgba(49, 34, 20, 0.10);
}

.banner-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.banner-title {
  font-weight: 950;
  letter-spacing: -0.2px;
  color: rgba(49, 34, 20, 0.92);
}

.banner-desc {
  font-size: 0.88rem;
  color: rgba(49, 34, 20, 0.58);
}

/* ✅ 배너 개별 색상 (너가 준 값 그대로) */
.b-orange { background-color: #ffcc95; }
.b-yellow { background-color: #ffecb3; }
.b-blue   { background-color: #d1e9ff; }
.b-peach  { background-color: #ffd8c4; }
.b-sky    { background-color: #d6ebff; }
.b-purple { background-color: #f3e5f5; }

/* ✅ 반응형 */
@media (max-width: 820px) {
  .banner-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 480px) {
  .banner-grid {
    grid-template-columns: 1fr;
    gap: 14px;
  }
}

/* ✅ 배너 정렬 강제 (hero의 text-align:center 상속 문제 해결) */
.banner {
  display: grid !important;              /* flex로 덮여도 grid로 고정 */
  grid-template-columns: 56px 1fr;       /* 아이콘/텍스트 시작선 통일 */
  column-gap: 12px;
  align-items: center;
  justify-items: start;
  text-align: left !important;           /* ✅ 핵심: 텍스트 좌측 정렬 강제 */
}

.icon-box {
  justify-self: start;                   /* 아이콘 박스를 왼쪽에 고정 */
}

.banner-text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;               /* ✅ 텍스트 덩어리 왼쪽 정렬 */
  text-align: left !important;
}

.banner-title,
.banner-desc {
  text-align: left !important;           /* ✅ AI 포함 전부 동일한 시작선 */
}

</style>
