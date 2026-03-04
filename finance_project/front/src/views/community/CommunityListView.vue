<template>
  <div class="wrap">
    <div class="top">
      <h2>커뮤니티</h2>
      <button v-if="auth.isLogin" class="btn" @click="goCreate">글쓰기</button>
    </div>

    <p v-if="loading">불러오는 중...</p>
    <p v-else-if="posts.length === 0">게시글이 없습니다.</p>

    <ul class="list">
      <li v-for="p in posts" :key="p.id" class="item" @click="goDetail(p.id)">
        <div class="title">{{ p.title }}</div>
        <div class="meta">
          <span>{{ p.author_nickname || p.author_username }}</span>
          <span>·</span>
          <span>{{ formatDate(p.created_at) }}</span>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const loading = ref(false)
const posts = ref([])

const fetchPosts = async () => {
  loading.value = true
  try {
    const res = await axios.get(`${auth.API_URL}/api/v1/community/posts/`)
    posts.value = Array.isArray(res.data) ? res.data : []
  } catch (e) {
    console.log('posts 로드 실패', e)
    posts.value = []
  } finally {
    loading.value = false
  }
}

const goDetail = (id) => router.push({ name: 'CommunityDetailView', params: { id } })
const goCreate = () => router.push({ name: 'CommunityCreateView' })

const formatDate = (iso) => (iso ? iso.slice(0, 10) : '')

onMounted(fetchPosts)
</script>

<!-- <style scoped>
.wrap { max-width: 900px; margin: 0 auto; padding: 24px; }
.top { display:flex; align-items:center; justify-content:space-between; }
.btn { padding: 8px 12px; border: none; border-radius: 8px; cursor:pointer; }
.list { list-style:none; padding:0; margin-top: 16px; }
.item { padding: 14px 12px; border: 1px solid #eee; border-radius: 10px; margin-bottom: 10px; cursor:pointer; }
.title { font-weight: 800; margin-bottom: 6px; }
.meta { color:#777; font-size: 12px; display:flex; gap:6px; }
</style> -->


<style scoped>
.wrap {
  max-width: 980px;
  margin: 0 auto;
  padding: 34px 18px 50px;
}

.top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}

.top h2 {
  margin: 0;
  font-size: 1.6rem;
  font-weight: 950;
  letter-spacing: -0.5px;
  color: rgba(47, 36, 26, 0.92);
}

/* 글쓰기 버튼: 글래스 느낌 + 그림자 */
.btn {
  border: 1px solid rgba(47, 36, 26, 0.12);
  background: rgba(255, 255, 255, 0.78);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);

  padding: 10px 14px;
  border-radius: 14px;

  font-weight: 900;
  cursor: pointer;

  box-shadow: 0 10px 22px rgba(47, 36, 26, 0.10);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 30px rgba(47, 36, 26, 0.14);
}
.btn:active {
  transform: translateY(0);
}

/* 리스트: 카드 사이 간격으로 구분감 확 만들기 */
.list {
  list-style: none;
  padding: 0;
  margin: 14px 0 0;
  display: flex;
  flex-direction: column;
  gap: 14px; /* ✅ 핵심: 간격 */
}

/* 게시글 카드 */
.item {
  position: relative;
  overflow: hidden;

  padding: 16px 18px;
  border-radius: 16px;

  background: rgba(255, 255, 255, 0.78); /* ✅ 배경보다 더 밝게 */
  border: 1px solid rgba(47, 36, 26, 0.10);
  box-shadow: 0 10px 22px rgba(47, 36, 26, 0.10);

  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}

/* 왼쪽 포인트 바(선택이지만 구분감/완성도 크게 올라감) */
.item::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 6px;
  background: rgba(255, 200, 120, 0.9);
}

.item:hover {
  transform: translateY(-3px);
  box-shadow: 0 16px 34px rgba(47, 36, 26, 0.14);
  border-color: rgba(34, 58, 94, 0.22);
}

.title {
  font-weight: 950;
  letter-spacing: -0.2px;
  color: rgba(47, 36, 26, 0.92);
  margin-bottom: 8px;
}

/* 메타는 조금 더 연하게 + 한 줄 정돈 */
.meta {
  color: rgba(47, 36, 26, 0.60);
  font-size: 0.88rem;
  display: flex;
  gap: 8px;
  align-items: center;
}

/* 반응형 */
@media (max-width: 480px) {
  .wrap {
    padding: 26px 14px 34px;
  }
  .item {
    padding: 14px 14px;
  }
}
</style>
