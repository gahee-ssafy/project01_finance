<template>
  <div class="wrap" v-if="loaded">
    <h2>글 수정</h2>

    <div class="form">
      <input v-model.trim="title" class="input" placeholder="제목" />
      <textarea v-model.trim="content" class="textarea" placeholder="내용"></textarea>

      <div class="actions">
        <button class="btn" @click="save" :disabled="saving">저장</button>
        <button class="btn ghost" @click="goDetail">취소</button>
      </div>
    </div>
  </div>

  <div class="wrap" v-else>
    <p>불러오는 중...</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const title = ref('')
const content = ref('')
const loaded = ref(false)
const saving = ref(false)

const id = route.params.id

const fetchPost = async () => {
  const res = await axios.get(`${auth.API_URL}/api/v1/community/posts/${id}/`)
  title.value = res.data.title
  content.value = res.data.content
  loaded.value = true
}

const save = async () => {
  saving.value = true
  try {
    await axios.patch(
      `${auth.API_URL}/api/v1/community/posts/${id}/`,
      { title: title.value, content: content.value },
      { headers: auth.authHeader }
    )
    router.push({ name: 'CommunityDetailView', params: { id } })
  } catch (e) {
    console.log('수정 실패', e?.response?.status, e?.response?.data)
    alert('수정 실패')
  } finally {
    saving.value = false
  }
}

const goDetail = () => router.push({ name: 'CommunityDetailView', params: { id } })

onMounted(async () => {
  if (auth.isLogin && !auth.user?.username) await auth.fetchMe()
  await fetchPost()
})
</script>

<style scoped>
.wrap { max-width: 900px; margin: 0 auto; padding: 24px; }
.form { display:flex; flex-direction:column; gap: 12px; margin-top: 14px; }
.input { padding: 10px 12px; border:1px solid #ddd; border-radius: 10px; }
.textarea { min-height: 240px; padding: 10px 12px; border:1px solid #ddd; border-radius: 10px; resize: vertical; }
.actions { display:flex; gap: 10px; }
.btn { padding: 10px 14px; border:none; border-radius: 10px; cursor:pointer; }
.ghost { background: transparent; border: 1px solid #ddd; }
</style>
