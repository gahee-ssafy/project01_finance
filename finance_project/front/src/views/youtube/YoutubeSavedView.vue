<template>
  <div class="saved-page">
    <RouterLink :to="{ name: 'YoutubeSearchView' }" class="back-link">← 뒤로가기</RouterLink>

    <h1 class="page-title">나중에 볼 동영상</h1>

    <p v-if="videos.length === 0" class="empty-text">
      등록된 비디오 없음
    </p>

    <div v-else class="video-grid">
      <div v-for="video in videos" :key="video.id" class="video-item">
        <VideoCard :video="video" @click="goToDetail(video)" />
        <button class="delete-btn" @click="removeVideo(video.id)">삭제</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import VideoCard from '@/components/youtube/VideoCard.vue'

const router = useRouter()
const STORAGE_KEY = 'firstsalary_youtube_watch_later'
const videos = ref([])

const loadVideos = () => {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return (videos.value = [])
  try {
    videos.value = JSON.parse(raw)
  } catch {
    videos.value = []
  }
}

const removeVideo = (id) => {
  videos.value = videos.value.filter((v) => v.id !== id)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(videos.value))
}

const goToDetail = (video) => {
  router.push({
    name: 'YoutubeVideoDetailView',
    params: { id: video.id },
    query: { from: 'saved' }, 
  })
}

onMounted(loadVideos)
</script>

<style scoped>
.saved-page { max-width: 1100px; margin: 0 auto; }

.back-link {
  display: inline-block;
  margin-bottom: 12px;
  font-size: 14px;
  color: #0077cc;
  text-decoration: none;
}
.back-link:hover { text-decoration: underline; }

.page-title { font-size: 24px; margin-bottom: 16px; }
.empty-text { color: #777777; font-size: 14px; }

.video-grid {
  margin-top: 12px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.video-item { display: flex; flex-direction: column; }

.delete-btn {
  margin-top: 8px;
  padding: 6px 8px;
  border: none;
  border-radius: 4px;
  background-color: #e53935;
  color: white;
  font-size: 12px;
  cursor: pointer;
}
.delete-btn:hover { opacity: 0.9; }
</style>
