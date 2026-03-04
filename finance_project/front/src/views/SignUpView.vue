<template>
  <div>
    <h1>회원가입</h1>
    <form @submit.prevent="submitForm">
      <div>
        <label for="username">ID: </label>
        <input type="text" id="username" v-model="username" required>
      </div>
      <div>
        <label for="password">PW: </label>
        <input type="password" id="password" v-model="password" required>
      </div>
      <!-- [추가] 백에서 2개의 번호를 받으려고 함  -->
      <div>
        <label for="passwordConfirm">PW 확인: </label>
        <input type="password" id="passwordConfirm" v-model="passwordConfirm" required>
      </div>
      
      <div>
        <label for="nickname">닉네임: </label>
        <input type="text" id="nickname" v-model="nickname">
      </div>
      <div>
        <label for="money">현재 자산: </label>
        <input type="number" id="money" v-model="money">
      </div>
      <div>
        <label for="salary">연봉: </label>
        <input type="number" id="salary" v-model="salary">
      </div>

      <button type="submit">가입하기</button>
    </form>
  </div>
</template>

<script setup>
 
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const passwordConfirm = ref('') // [추가] 반응형 변수 추가
const nickname = ref('')
const money = ref(0)
const salary = ref(0)

const submitForm = function () {
  // [추가] 프론트엔드 유효성 검사 (두 비밀번호가 다르면 요청 안 보냄)
  if (password.value !== passwordConfirm.value) {
    window.alert('비밀번호가 일치하지 않습니다!')
    return
  }

  // [수정] 백엔드가 원하는 이름(key)으로 데이터 포장
  const payload = {
    username: username.value,
    password1: password.value,       // 백엔드는 password1을 원함
    password2: passwordConfirm.value, // 백엔드는 password2를 원함
    nickname: nickname.value,
    money: money.value,
    salary: salary.value
  }
  
  // Store의 회원가입 함수 호출
  authStore.signUp(payload)
}
</script>
