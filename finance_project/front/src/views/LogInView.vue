<template>
  <div>
    <h1>로그인</h1>
    <form @submit.prevent="submitForm">
      <div>
        <label for="username">ID: </label>
        <input type="text" id="username" v-model="username" required>
      </div>
      <div>
        <label for="password">PW: </label>
        <input type="password" id="password" v-model="password" required>
      </div>
      <button type="submit">로그인</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const username = ref('')
const password = ref('')

const submitForm = function () {
  const payload = {
    username: username.value,
    password: password.value
  }
  authStore.logIn(payload)
}
</script>