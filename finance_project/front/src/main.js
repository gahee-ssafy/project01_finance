import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

import App from './App.vue'
import router from './router'

import './assets/main.css'


const app = createApp(App)

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate) // ✅ 이거 없으면 persist 안 됨

app.use(pinia)
app.use(router)

app.mount('#app')
