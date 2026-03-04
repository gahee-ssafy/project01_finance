<template>
  <section class="hero">
    <h1 class="title">준비 중입니다</h1>
    <p class="subtitle">다음 요구사항에서 기능을 채워갈 예정!</p>
    <RouterLink class="btn" to="/">홈으로</RouterLink>
  </section>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.hero { padding: 16px 0 24px; }
.title { margin:0 0 10px; font-size:28px; }
.subtitle { margin:0; color:#555; line-height:1.5; }
.btn { display:inline-block; margin-top:12px; padding:10px 14px; border-radius:12px; border:1px solid #ddd; text-decoration:none; color:#111; }
</style>
