<template>
  <div class="wrap" v-if="post">
    <div class="head">
      <button class="link" @click="goList">← 목록</button>
      <div class="right" v-if="isOwner">
        <button class="btn ghost" @click="goEdit">수정</button>
        <button class="btn danger" @click="removePost">삭제</button>
      </div>
    </div>

    <h2 class="title">{{ post.title }}</h2>
    <div class="meta">
      <span>{{ post.author_nickname || post.author_username }}</span>
      <span>·</span>
      <span>{{ formatDate(post.created_at) }}</span>
    </div>

    <p class="content">{{ post.content }}</p>

    <hr />

    <h3>댓글</h3>
    <div v-if="auth.isLogin" class="comment-box">
      <input v-model.trim="commentText" class="input" placeholder="댓글을 입력하세요" />
      <button class="btn" @click="createComment">등록</button>
    </div>

    <ul class="comments">
      <li v-for="c in comments" :key="c.id" class="comment">
        <div class="c-top">
          <div class="c-meta">
            <b>{{ c.author_nickname || c.author_username }}</b>
            <span>·</span>
            <span>{{ formatDate(c.created_at) }}</span>
          </div>

          <div class="c-actions" v-if="isCommentOwner(c)">
            <button class="mini" @click="startEditComment(c)">수정</button>
            <button class="mini danger" @click="removeComment(c.id)">삭제</button>
          </div>
        </div>

        <div v-if="editingId === c.id" class="edit-row">
          <input v-model.trim="editingText" class="input" />
          <button class="mini" @click="saveComment(c.id)">저장</button>
          <button class="mini ghost" @click="cancelEdit">취소</button>
        </div>
        <p v-else class="c-content">{{ c.content }}</p>
      </li>
    </ul>
  </div>

  <div class="wrap" v-else>
    <p>불러오는 중...</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const post = ref(null)
const comments = ref([])

const commentText = ref('')
const editingId = ref(null)
const editingText = ref('')

const postId = computed(() => route.params.id)

const fetchPost = async () => {
  const res = await axios.get(`${auth.API_URL}/api/v1/community/posts/${postId.value}/`)
  post.value = res.data
  // 상세 serializer가 comments를 포함하므로 그대로 사용
  comments.value = Array.isArray(res.data.comments) ? res.data.comments : []
}

const isOwner = computed(() => {
  const meUsername = auth.user?.username
  return !!meUsername && meUsername === post.value?.author_username
})

const isCommentOwner = (c) => {
  const meUsername = auth.user?.username
  return !!meUsername && meUsername === c.author_username
}

const goList = () => router.push({ name: 'CommunityListView' })
const goEdit = () => router.push({ name: 'CommunityEditView', params: { id: postId.value } })

const removePost = async () => {
  if (!confirm('삭제할까요?')) return
  try {
    await axios.delete(`${auth.API_URL}/api/v1/community/posts/${postId.value}/`, {
      headers: auth.authHeader,
    })
    goList()
  } catch (e) {
    console.log('삭제 실패', e?.response?.status, e?.response?.data)
    alert('삭제 실패')
  }
}

const createComment = async () => {
  if (!commentText.value) return
  try {
    await axios.post(
      `${auth.API_URL}/api/v1/community/posts/${postId.value}/comments/`,
      { content: commentText.value },
      { headers: auth.authHeader }
    )
    commentText.value = ''
    await fetchPost()
  } catch (e) {
    console.log('댓글 작성 실패', e?.response?.status, e?.response?.data)
    alert('댓글 작성 실패')
  }
}

const startEditComment = (c) => {
  editingId.value = c.id
  editingText.value = c.content
}

const cancelEdit = () => {
  editingId.value = null
  editingText.value = ''
}

const saveComment = async (commentId) => {
  if (!editingText.value) return
  try {
    await axios.patch(
      `${auth.API_URL}/api/v1/community/comments/${commentId}/`,
      { content: editingText.value },
      { headers: auth.authHeader }
    )
    cancelEdit()
    await fetchPost()
  } catch (e) {
    console.log('댓글 수정 실패', e?.response?.status, e?.response?.data)
    alert('댓글 수정 실패')
  }
}

const removeComment = async (commentId) => {
  if (!confirm('댓글을 삭제할까요?')) return
  try {
    await axios.delete(`${auth.API_URL}/api/v1/community/comments/${commentId}/`, {
      headers: auth.authHeader,
    })
    await fetchPost()
  } catch (e) {
    console.log('댓글 삭제 실패', e?.response?.status, e?.response?.data)
    alert('댓글 삭제 실패')
  }
}

const formatDate = (iso) => (iso ? iso.slice(0, 10) : '')

onMounted(async () => {
  if (auth.isLogin && !auth.user?.username) {
    await auth.fetchMe()
  }
  await fetchPost()
})
</script>

<style scoped>
.wrap { max-width: 900px; margin: 0 auto; padding: 24px; }
.head { display:flex; justify-content:space-between; align-items:center; gap:10px; }
.link { background:transparent; border:none; color:#0077cc; cursor:pointer; padding:0; }
.right { display:flex; gap:10px; }
.btn { padding: 8px 12px; border:none; border-radius: 10px; cursor:pointer; }
.ghost { background:transparent; border: 1px solid #ddd; }
.danger { background:#e53935; color:white; }
.title { margin-top: 10px; font-weight: 800; }
.meta { color:#777; font-size: 12px; display:flex; gap:6px; margin-bottom: 14px; }
.content { white-space: pre-wrap; line-height: 1.6; }
.comment-box { display:flex; gap:10px; margin: 12px 0; }
.input { flex:1; padding: 10px 12px; border:1px solid #ddd; border-radius: 10px; }
.comments { list-style:none; padding:0; margin-top: 10px; display:flex; flex-direction:column; gap:10px; }
.comment { border:1px solid #eee; border-radius: 10px; padding: 12px; }
.c-top { display:flex; justify-content:space-between; align-items:center; gap:10px; }
.c-meta { font-size: 12px; color:#666; display:flex; gap:6px; align-items:center; }
.c-actions { display:flex; gap:6px; }
.mini { border:none; background:#f1f3f5; padding: 6px 8px; border-radius: 8px; cursor:pointer; font-size: 12px; }
.mini.ghost { background:transparent; border:1px solid #ddd; }
.mini.danger { background:#e53935; color:white; }
.c-content { margin-top: 8px; white-space: pre-wrap; }
.edit-row { display:flex; gap:8px; margin-top: 8px; }
</style>
