<template>
  <header class="topbar">
    <div class="topbar-inner">
      <RouterLink to="/" class="brand-link">JJuns 메이트</RouterLink>

      <!-- ✅ 데스크탑 메뉴(가로) -->
      <nav class="nav desktop">
        <RouterLink class="nav-link" :to="{ name: 'DepositView' }">🏦 예적금</RouterLink>
        <RouterLink class="nav-link" :to="{ name: 'GoldView' }">🥇 금/은</RouterLink>
        <RouterLink class="nav-link" :to="{ name: 'MapView' }">🗺️ 내 주변 은행</RouterLink>
        <RouterLink class="nav-link" :to="{ name: 'YoutubeSearchView' }">📺 관심 종목 검색</RouterLink>
        <RouterLink class="nav-link" :to="{ name: 'CommunityListView' }">💬 커뮤니티</RouterLink>
        <RouterLink class="nav-link" :to="{ name: 'AIRecommendView' }">🤖 AI</RouterLink>
      </nav>

      <!-- ✅ 우측(계정 + 햄버거) -->
      <div class="right">
        <!-- 비로그인 -->
        <template v-if="!auth.isLogin">
          <RouterLink class="right-link" :to="{ name: 'LogInView' }">로그인</RouterLink>
          <RouterLink class="right-link" :to="{ name: 'SignUpView' }">회원가입</RouterLink>
        </template>

        <!-- 로그인 -->
        <template v-else>
          <RouterLink class="right-link" :to="{ name: 'ProfileView' }">마이페이지</RouterLink>
          <button class="right-btn" @click="auth.logOut()">로그아웃</button>
        </template>

        <!-- ✅ 햄버거(모바일에서만 표시) -->
        <button class="hamburger" type="button" @click="toggleMobile" aria-label="메뉴 열기">
          ☰
        </button>
      </div>
    </div>

    <!-- ✅ 모바일 오버레이 -->
    <div v-if="mobileOpen" class="mobile-backdrop" @click="closeMobile"></div>

    <!-- ✅ 모바일 드롭다운 메뉴 -->
    <nav class="nav mobile" :class="{ open: mobileOpen }">
      <RouterLink class="nav-link" :to="{ name: 'DepositView' }">🏦 예적금 조회</RouterLink>
      <RouterLink class="nav-link" :to="{ name: 'GoldView' }">🥇 금/은 시세</RouterLink>
      <RouterLink class="nav-link" :to="{ name: 'MapView' }">🗺️ 지도 조회</RouterLink>
      <RouterLink class="nav-link" :to="{ name: 'YoutubeSearchView' }">📺 유튜브</RouterLink>
      <RouterLink class="nav-link" :to="{ name: 'CommunityListView' }">💬 커뮤니티</RouterLink>
      <RouterLink class="nav-link" :to="{ name: 'AIRecommendView' }">🤖 AI 추천</RouterLink>

      <div class="mobile-divider"></div>

      <template v-if="!auth.isLogin">
        <RouterLink class="nav-link" :to="{ name: 'LogInView' }">🔑 로그인</RouterLink>
        <RouterLink class="nav-link" :to="{ name: 'SignUpView' }">📝 회원가입</RouterLink>
      </template>

      <template v-else>
        <RouterLink class="nav-link" :to="{ name: 'ProfileView' }">👤 마이페이지</RouterLink>
        <button class="nav-link danger" @click="auth.logOut()">🚪 로그아웃</button>
      </template>
    </nav>
  </header>

  <main class="container">
    <RouterView />
  </main>
</template>

<script setup>
import { RouterView, RouterLink, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { onMounted, ref, watch } from 'vue'

const auth = useAuthStore()
const route = useRoute()

const mobileOpen = ref(false)
const closeMobile = () => (mobileOpen.value = false)
const toggleMobile = () => (mobileOpen.value = !mobileOpen.value)

watch(
  () => route.fullPath,
  () => closeMobile()
)

// 로그인 상태인데 user 정보(닉네임 등)가 비어있으면 서버에서 받아오기
onMounted(() => {
  if (auth.isLogin && !auth.user?.nickname) {
    auth.fetchMe?.()
  }
})
</script>

<style scoped>
/* 상단바 */
.topbar {
  height: 56px;
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(255, 246, 232, 0.82);
  border-bottom: 1px solid rgba(47, 36, 26, 0.10);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.topbar-inner {
  max-width: 1100px;
  margin: 0 auto;
  height: 56px;
  padding: 0 22px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
}

/* 로고 */
.brand-link {
  font-weight: 950;
  letter-spacing: -0.4px;
  color: rgba(34, 58, 94, 0.95);
  white-space: nowrap;
}

/* 네비 */
.nav {
  display: flex;
  align-items: center;
  gap: 10px;
}

.nav-link {
  padding: 9px 10px;
  border-radius: 12px;
  font-weight: 900;
  font-size: 0.92rem;
  color: rgba(47, 36, 26, 0.88);
  border: 1px solid transparent;
  transition: transform 0.15s ease, background 0.15s ease, border-color 0.15s ease;
}

.nav-link:hover {
  transform: translateY(-1px);
  background: rgba(255, 255, 255, 0.55);
  border-color: rgba(47, 36, 26, 0.10);
}

.nav-link.router-link-active {
  background: rgba(168, 214, 255, 0.38);
  border-color: rgba(34, 58, 94, 0.16);
  color: rgba(34, 58, 94, 0.95);
}

/* 우측 */
.right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.right-link {
  font-weight: 900;
  padding: 8px 10px;
  border-radius: 12px;
  color: rgba(47, 36, 26, 0.86);
}
.right-link:hover {
  background: rgba(255, 255, 255, 0.55);
  border: 1px solid rgba(47, 36, 26, 0.10);
}

.right-btn {
  border: 1px solid rgba(47, 36, 26, 0.12);
  background: rgba(255, 255, 255, 0.65);
  padding: 8px 10px;
  border-radius: 12px;
  font-weight: 900;
  cursor: pointer;
}

/* 햄버거 */
.hamburger {
  display: none;
  border: 1px solid rgba(47, 36, 26, 0.12);
  background: rgba(255, 255, 255, 0.70);
  border-radius: 12px;
  padding: 8px 10px;
  font-size: 1.05rem;
  cursor: pointer;
}

/* 모바일 메뉴 */
.nav.mobile {
  position: fixed;
  top: 56px;
  right: 14px;
  width: min(320px, calc(100vw - 28px));
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(47, 36, 26, 0.10);
  box-shadow: 0 18px 40px rgba(47, 36, 26, 0.16);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);

  transform: translateY(-8px);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.nav.mobile.open {
  transform: translateY(0);
  opacity: 1;
  pointer-events: auto;
}

.mobile-divider {
  height: 1px;
  background: rgba(47, 36, 26, 0.10);
  margin: 6px 0;
}

.nav-link.danger {
  background: rgba(255, 199, 181, 0.35);
  border-color: rgba(255, 199, 181, 0.55);
  cursor: pointer;
}

/* backdrop */
.mobile-backdrop {
  position: fixed;
  inset: 56px 0 0 0;
  background: rgba(0, 0, 0, 0.12);
  z-index: 25;
}

/* 본문 컨테이너(기존 유지) */
.container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 18px 18px 26px;
}

/* 반응형 */
@media (max-width: 980px) {
  .nav.desktop {
    display: none;
  }
  .hamburger {
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }
}

/* 모바일에서 간격 */
@media (max-width: 480px) {
  .topbar-inner {
    padding: 0 14px;
  }
}
</style>
