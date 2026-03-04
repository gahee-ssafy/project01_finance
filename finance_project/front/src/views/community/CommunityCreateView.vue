<template>
  <div class="wrap">
    <h2>글쓰기</h2>

    <div class="form">
      <input v-model.trim="title" placeholder="제목" class="input" />
      <textarea v-model.trim="content" placeholder="내용" class="textarea"></textarea>

      <div class="actions">
        <button class="btn" @click="submit" :disabled="saving">
          {{ saving ? '등록중...' : '등록' }}
        </button>
        <button class="btn ghost" @click="goBack" :disabled="saving">취소</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const title = ref('')
const content = ref('')
const saving = ref(false)

const submit = async () => {
  if (!auth.isLogin) return window.alert('로그인이 필요합니다.')
  if (!title.value?.trim() || !content.value?.trim()) {
    return window.alert('제목/내용을 입력해주세요.')
  }

  saving.value = true
  try {
    const res = await axios({
      method: 'post',
      url: `${auth.API_URL}/api/v1/community/posts/`,
      data: { title: title.value.trim(), content: content.value.trim() },
      // ✅ Pinia store에서 authHeader가 computed면 보통 auth.authHeader로 사용 가능
      // 혹시 환경에 따라 ref로 들어오면 value로도 대비
      headers: auth.authHeader?.value ?? auth.authHeader,
    })

    // ✅ 작성 자체는 성공(201). 실패 알림은 절대 여기서 띄우면 안 됨.
    window.alert('작성 완료!')

    // 서버가 id를 안 주는 경우가 있으니 안전 처리
    const newId = res.data?.id ?? res.data?.pk ?? res.data?.article_id

    if (newId) {
      // 상세로 이동 (라우팅 실패하면 목록으로)
      router
        .push({ name: 'CommunityDetailView', params: { id: newId } })
        .catch(() => router.push({ name: 'CommunityListView' }))
    } else {
      // id가 없으면 목록으로
      router.push({ name: 'CommunityListView' })
    }
  } catch (e) {
    console.log('작성 실패', e?.response?.status, e?.response?.data, e)
    window.alert('작성에 실패했습니다.')
  } finally {
    saving.value = false
  }
}

const goBack = () => router.push({ name: 'CommunityListView' })
</script>

<style scoped>
.wrap { max-width: 900px; margin: 0 auto; padding: 24px; }
.form { display:flex; flex-direction:column; gap: 12px; margin-top: 14px; }
.input { padding: 10px 12px; border:1px solid #ddd; border-radius: 10px; }
.textarea { min-height: 240px; padding: 10px 12px; border:1px solid #ddd; border-radius: 10px; resize: vertical; }
.actions { display:flex; gap: 10px; }
.btn { padding: 10px 14px; border:none; border-radius: 10px; cursor:pointer; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.ghost { background: transparent; border: 1px solid #ddd; }
</style>
