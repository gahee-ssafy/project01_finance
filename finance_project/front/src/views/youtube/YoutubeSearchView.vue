<template>
  <div class="search-page">
    <div class="top-row">
      <h1 class="page-title">관심 종목 영상 검색</h1>
      <RouterLink :to="{ name: 'YoutubeSavedView' }" class="saved-link">저장 목록</RouterLink>
    </div>

    <div class="search-bar">
      <input
        v-model="query"
        @keyup.enter="searchVideos"
        type="text"
        placeholder="검색어를 입력하세요 (예: 예적금 추천, 재테크 입문, 월급 관리)"
      />
      <button @click="searchVideos">찾기</button>
    </div>

    <p v-if="hasSearched && videos.length === 0" class="empty-text">
      검색 결과가 없습니다.
    </p>

    <div class="video-grid">
      <VideoCard
        v-for="video in videos"
        :key="video.id"
        :video="video"
        @click="goToDetail(video)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import VideoCard from '@/components/youtube/VideoCard.vue'

const router = useRouter()
const route = useRoute()

const query = ref('')
const videos = ref([])
const hasSearched = ref(false)

const API_KEY = import.meta.env.VITE_YOUTUBE_API_KEY

const searchVideos = async () => {
  const trimmed = query.value.trim()
  if (!trimmed) return

  // ✅ 현재 검색어를 URL에 남겨두기 (/youtube?q=...)
  if (route.query.q !== trimmed) {
    router.replace({ name: 'YoutubeSearchView', query: { q: trimmed } }).catch(() => {})
  }

  const params = new URLSearchParams({
    key: API_KEY,
    part: 'snippet',
    q: trimmed,
    type: 'video',
    maxResults: '12',
  })

  try {
    const res = await fetch(`https://www.googleapis.com/youtube/v3/search?${params.toString()}`)
    const data = await res.json()

    videos.value = (data.items || []).map((item) => ({
      id: item.id.videoId,
      title: item.snippet.title,
      channelTitle: item.snippet.channelTitle,
      thumbnail:
        item.snippet.thumbnails.medium?.url ||
        item.snippet.thumbnails.default?.url,
    }))

    hasSearched.value = true
  } catch (error) {
    console.error('검색 중 오류 발생:', error)
    hasSearched.value = true
  }
}

const goToDetail = (video) => {
  const trimmed = query.value.trim()
  router.push({
    name: 'YoutubeVideoDetailView',
    params: { id: video.id },
    // ✅ 상세로 갈 때도 검색어(query)를 같이 들고 간다
    query: trimmed ? { q: trimmed } : {},
  })
}

// ✅ 페이지 진입 시 URL에 q가 있으면 자동 검색
onMounted(() => {
  const q = (route.query.q || '').toString().trim()
  if (q) {
    query.value = q
    searchVideos()
  }
})
</script>


<style scoped>
.search-page { max-width: 1100px; margin: 0 auto; }

.top-row{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
}

.page-title { font-size: 24px; margin-bottom: 16px; }
.saved-link{
  font-size: 14px;
  color:#0077cc;
  text-decoration:none;
}
.saved-link:hover{ text-decoration: underline; }

.search-bar { display: flex; gap: 8px; margin-bottom: 24px; }

.search-bar input {
  flex: 1;
  padding: 8px 12px;
  font-size: 14px;
  border-radius: 4px;
  border: 1px solid #cccccc;
}

.search-bar button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  background-color: #1ba34a;
  color: white;
  font-weight: 600;
  cursor: pointer;
}

.search-bar button:hover { opacity: 0.9; }
.empty-text { color: #777777; margin-top: 16px; }

.video-grid {
  margin-top: 12px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}
</style>
