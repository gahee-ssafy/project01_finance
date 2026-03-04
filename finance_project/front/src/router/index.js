import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

import DepositView from '@/views/DepositView.vue'
import DepositDetailView from '@/views/DepositDetailView.vue'
import GoldView from '@/views/GoldView.vue'

import LogInView from '@/views/LogInView.vue'
import SignUpView from '@/views/SignUpView.vue'

import MapView from '@/views/MapView.vue'

// ✅ F08 마이페이지(새로 생성할 뷰)
import ProfileView from '@/views/ProfileView.vue'

// F05 유튜브 
import YoutubeSearchView from '@/views/youtube/YoutubeSearchView.vue'
import YoutubeVideoDetailView from '@/views/youtube/YoutubeVideoDetailView.vue'
import YoutubeSavedView from '@/views/youtube/YoutubeSavedView.vue'

// F07 커뮤니티
import CommunityListView from '@/views/community/CommunityListView.vue'
import CommunityDetailView from '@/views/community/CommunityDetailView.vue'
import CommunityCreateView from '@/views/community/CommunityCreateView.vue'
import CommunityEditView from '@/views/community/CommunityEditView.vue'

// ✅ auth store (가드용)
import { useAuthStore } from '@/stores/auth'


import AIRecommendView from '@/views/AIRecommendView.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },

    // ✅ 로그인 / 회원가입
    {
      path: '/login',
      name: 'LogInView',
      component: LogInView,
    },
    {
      path: '/signup',
      name: 'SignUpView',
      component: SignUpView,
    },

    // ✅ F08 마이페이지 (로그인 필요)
    {
      path: '/profile',
      name: 'ProfileView',
      component: ProfileView,
      meta: { requiresAuth: true },
    },

    // 예적금
    {
      path: '/deposit',
      name: 'DepositView',
      component: DepositView,
    },

    // 금/은
    {
      path: '/gold',
      name: 'GoldView',
      component: GoldView,
    },

    // 지도
    {
      path: '/map',
      name: 'MapView',
      component: MapView
    },

    // 유튜브
    {
      path: '/youtube',
      name: 'YoutubeSearchView',
      component: YoutubeSearchView,
    },
    {
      path: '/youtube/saved',
      name: 'YoutubeSavedView',
      component: YoutubeSavedView,
    },
    {
      path: '/youtube/video/:id',
      name: 'YoutubeVideoDetailView',
      component: YoutubeVideoDetailView,
    },

    // 커뮤니티
    {
      path: '/community',
      name: 'CommunityListView',
      component: CommunityListView,
    },
    {
      path: '/community/create',
      name: 'CommunityCreateView',
      component: CommunityCreateView,
    },
    {
      path: '/community/:id',
      name: 'CommunityDetailView',
      component: CommunityDetailView,
    },
    {
      path: '/community/:id/edit',
      name: 'CommunityEditView',
      component: CommunityEditView,
    },
    // 8. AI 상품 추천 페이지 (새로 추가!)
    {
      path: '/recommend',
      name: 'AIRecommendView',
      component: AIRecommendView,
    },
    
    // 목록상세조회
    {
      path: '/deposit/:fin_prdt_cd',
      name: 'DepositDetailView',
      component: DepositDetailView,
    },
  ],
})

/**
 * ✅ 로그인 가드
 * meta.requiresAuth === true 인 라우트는 로그인 안했으면 /login으로 이동
 */
router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta?.requiresAuth && !auth.isLogin) {
    return { name: 'LogInView' }
  }
})

export default router
