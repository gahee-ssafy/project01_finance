import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore(
  'auth',
  () => {
    const router = useRouter()

    const API_URL = 'http://127.0.0.1:8000'

    const token = ref(null)
    const user = ref(null)

    const isLogin = computed(() => !!token.value)

    const authHeader = computed(() => {
      return token.value ? { Authorization: `Token ${token.value}` } : {}
    })

    // ✅ 내 정보 가져오기 (닉네임/username 등)
    const fetchMe = async () => {
      if (!token.value) return

      try {
        const res = await axios({
          method: 'get',
          url: `${API_URL}/accounts/me/`,
          headers: authHeader.value,
        })
        user.value = res.data
      } catch (err) {
        console.log('fetchMe 실패:', err?.response?.status, err?.response?.data)
        // 토큰이 만료/무효면 로그아웃 처리(선택)
        // token.value = null
        // user.value = null
      }
    }

    const signUp = (payload) => {
      axios({
        method: 'post',
        url: `${API_URL}/accounts/signup/`,
        data: payload,
      })
        .then((res) => {
          console.log('회원가입 성공!', res)
          window.alert('회원가입이 완료되었습니다. 로그인 해주세요.')
          router.push({ name: 'LogInView' }).catch(() => router.push({ name: 'home' }))
        })
        .catch((err) => {
          console.log('회원가입 실패', err)
          console.log('서버 응답:', err?.response?.status, err?.response?.data)
          window.alert('회원가입에 실패했습니다. 입력 정보를 확인해주세요.')
        })
    }

    const logIn = async (payload) => {
      try {
        const res = await axios({
          method: 'post',
          url: `${API_URL}/accounts/login/`,
          data: payload,
        })

        token.value = res.data.key || null
        await fetchMe()

        await router.push({ name: 'home' }).catch(() => router.push('/'))
      } catch (err) {
        console.log('로그인 실패', err)
        console.log('서버 응답:', err?.response?.status, err?.response?.data)
        window.alert('로그인 실패! 아이디와 비밀번호를 확인하세요.')
      }
    }

    const logOut = async () => {
      // 서버 로그아웃까지 하려면 아래 주석 해제 가능
      // try { await axios.post(`${API_URL}/accounts/logout/`, null, { headers: authHeader.value }) } catch {}

      token.value = null
      user.value = null
      router.push({ name: 'home' }).catch(() => router.push('/'))
    }

    return {
      API_URL,
      token,
      user,
      isLogin,
      authHeader,
      fetchMe,
      signUp,
      logIn,
      logOut,
    }
  },
  {
    persist: {
      key: 'auth',
      storage: localStorage,
      paths: ['token', 'user'],
    },
  }
)
