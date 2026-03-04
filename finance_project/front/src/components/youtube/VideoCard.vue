<template>
  <div class="video-card" @click="$emit('click')">
    <img :src="video.thumbnail" :alt="video.title" class="thumbnail" />
    <div class="info">
      <h3 class="title">{{ video.title }}</h3>
      <p class="channel">{{ video.channelTitle }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  video: {
    type: Object,
    required: true,
  },
})
</script>

<style scoped>
.video-card {
  background-color: white;
  border-radius: 6px;
  padding: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.thumbnail {
  width: 100%;
  border-radius: 4px;
  object-fit: cover;
}

.info {
  margin-top: 8px;
}

.title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
}

.channel {
  font-size: 12px;
  color: #666666;
}
</style>
