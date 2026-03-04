<template>
  <div class="detail-page">
    <!-- ✅ 검색어(q) 그대로 들고 SearchView로 돌아가기 -->
    <RouterLink :to="backTo" class="back-link">
      ← 뒤로가기
    </RouterLink>

    <div v-if="isLoading" class="status">불러오는 중...</div>
    <div v-else-if="!video" class="status">영상을 찾을 수 없습니다.</div>
    <div v-else>
      <h1 class="title">{{ video.title }}</h1>
      <p class="channel">채널명: {{ video.channelTitle }}</p>

      <div class="player-wrapper">
        <iframe
          :src="embedUrl"
          frameborder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen
        ></iframe>
      </div>

      <div class="bottom-box">
        <button class="save-btn" @click="toggleSave">
          {{ isSaved ? '저장 취소' : '저장' }}
        </button>

        <p class="description">
          {{ video.description }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const backTo = computed(() => {
  // ✅ Saved 목록에서 들어온 경우
  if (route.query.from === 'saved') {
    return { name: 'YoutubeSavedView' }
  }

  // ✅ 기본: 검색 화면(q 유지)
  const q = route.query.q ? route.query.q.toString() : ''
  return {
    name: 'YoutubeSearchView',
    query: q ? { q } : {},
  }
})

const API_KEY = import.meta.env.VITE_YOUTUBE_API_KEY

const STORAGE_KEY = 'firstsalary_youtube_watch_later'

const video = ref(null)
const isLoading = ref(false)
const isSaved = ref(false)

const embedUrl = computed(() => {
  if (!video.value) return ''
  return `https://www.youtube.com/embed/${video.value.id}`
})

const checkIsSaved = () => {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return (isSaved.value = false)

  try {
    const list = JSON.parse(raw)
    isSaved.value = list.some((item) => item.id === video.value?.id)
  } catch {
    isSaved.value = false
  }
}

const toggleSave = () => {
  if (!video.value) return

  const raw = localStorage.getItem(STORAGE_KEY)
  let list = []
  if (raw) {
    try { list = JSON.parse(raw) } catch { list = [] }
  }

  if (isSaved.value) {
    list = list.filter((item) => item.id !== video.value.id)
    isSaved.value = false
  } else {
    const dataToSave = {
      id: video.value.id,
      title: video.value.title,
      channelTitle: video.value.channelTitle,
      thumbnail: video.value.thumbnail,
    }
    if (!list.some((item) => item.id === dataToSave.id)) list.push(dataToSave)
    isSaved.value = true
  }

  localStorage.setItem(STORAGE_KEY, JSON.stringify(list))
}

const fetchVideoDetail = async () => {
  const id = route.params.id
  if (!id) return

  isLoading.value = true

  const params = new URLSearchParams({
    key: API_KEY,
    part: 'snippet',
    id: id,
  })

  try {
    const res = await fetch(`https://www.googleapis.com/youtube/v3/videos?${params.toString()}`)
    const data = await res.json()

    if (data.items && data.items.length > 0) {
      const item = data.items[0]
      video.value = {
        id: item.id,
        title: item.snippet.title,
        channelTitle: item.snippet.channelTitle,
        description: item.snippet.description,
        thumbnail:
          item.snippet.thumbnails.medium?.url ||
          item.snippet.thumbnails.default?.url,
      }
      checkIsSaved()
    } else {
      video.value = null
    }
  } catch (error) {
    console.error('상세 정보 불러오는 중 오류:', error)
    video.value = null
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchVideoDetail)
</script>

<style scoped>
.detail-page { max-width: 900px; margin: 0 auto; }

.back-link {
  display: inline-block;
  margin-bottom: 12px;
  font-size: 14px;
  color: #0077cc;
  text-decoration: none;
}
.back-link:hover { text-decoration: underline; }

.status { margin-top: 24px; color: #666666; }
.title { font-size: 22px; font-weight: 700; margin-bottom: 4px; }
.channel { font-size: 14px; color: #666666; margin-bottom: 16px; }

.player-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%;
  margin-bottom: 16px;
}
.player-wrapper iframe {
  position: absolute;
  width: 100%;
  height: 100%;
  border: none;
}

.save-btn {
  display: inline-block;
  margin-bottom: 12px;
  padding: 8px 16px;
  background-color: #1ba34a;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}
.save-btn:hover { opacity: 0.9; }

.description { white-space: pre-wrap; font-size: 13px; line-height: 1.5; }
</style>
