<template>
  <div class="ai-container">
    <header class="ai-header">
      <h1>🤖 AI 금융 비서</h1>
      <p>당신의 꿈을 응원합니다. 고민을 들려주시면 최적의 상품을 찾아드릴게요.</p>
    </header>

    <section class="input-section">
      <textarea 
        v-model="userInput" 
        placeholder="예: 20대 사회초년생인데, 첫 월급으로 시작하기 좋은 고금리 적금 추천해줘"
        :disabled="isLoading"
      ></textarea>
      <button @click="getRecommendation" :disabled="isLoading">
        {{ isLoading ? 'AI가 분석 중...' : '맞춤 상품 찾기 ✨' }}
      </button>
    </section>

    <div v-if="isLoading" class="loading-spinner">
      <p>데이터 공간에서 가장 닮은 상품을 찾고 있어요... 🔍</p>
    </div>

    <section v-if="recommendations.length > 0" class="results-section">
      <h3>🎯 추천 상품 TOP 3</h3>
      <div class="card-grid">
        <div v-for="(item, index) in recommendations" :key="index" class="product-card">
          <div class="rank-badge">{{ index + 1 }}위</div>
          <div class="product-info">
            <span class="bank-name">{{ item.bank }}</span>
            <h4 class="product-name">{{ item.name }}</h4>
            <h4 class="product-rates">{{ item.max_rate }} %</h4>
          </div>
          <div class="similarity-score">
            AI 매칭률: <strong>{{ (item.similarity * 100).toFixed(1) }}%</strong>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const userInput = ref('')
const recommendations = ref([])
const isLoading = ref(false)

const getRecommendation = async () => {
  if (!userInput.value.trim()) {
    alert("고민 내용을 입력해 주세요!")
    return
  }

  isLoading.value = true
  recommendations.value = [] // 이전 결과 초기화

  try {
    const response = await axios.post('http://127.0.0.1:8000/api/v1/products/recommend/', {
      message: userInput.value
    })
    
    // 백엔드에서 준 JsonResponse의 'recommendations' 키값을 받아옵니다.
    recommendations.value = response.data.recommendations
  } catch (error) {
    console.error("데이터 로드 실패:", error)
    alert("서버와 통신 중 문제가 발생했습니다. (CORS 설정을 확인해 보세요!)")
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.ai-container { max-width: 800px; margin: 0 auto; padding: 20px; font-family: 'Pretendard', sans-serif; }
.input-section textarea { width: 100%; height: 100px; padding: 15px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 10px; resize: none; }
.input-section button { width: 100%; padding: 15px; background: #4a90e2; color: white; border: none; border-radius: 10px; cursor: pointer; font-size: 1.1rem; }
.card-grid { display: grid; gap: 15px; margin-top: 20px; }
.product-card { position: relative; padding: 20px; border: 1px solid #e1e1e1; border-radius: 15px; background: #fff; transition: transform 0.3s; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
.product-card:hover { transform: translateY(-5px); }
.rank-badge { position: absolute; top: 10px; right: 10px; background: #ff6b6b; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; }
.bank-name { color: #888; font-size: 0.9rem; }
.product-name { margin: 5px 0; color: #333; }
.similarity-score { margin-top: 10px; font-size: 0.9rem; color: #4a90e2; }
</style>