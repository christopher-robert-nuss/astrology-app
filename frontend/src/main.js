import { createApp } from 'vue'
import PrimeVue from 'primevue/config'
import Aura from '@primeuix/themes/aura'
import 'primeicons/primeicons.css'
import './style.css'
import App from './App.vue'

// import router from './router'
// import { createPinia } from 'pinia'

const app = createApp(App)

// app.use(createPinia())
// app.use(router)
app.use(PrimeVue, {
  ripple: true,
  theme: {
    preset: Aura,
    options: {
      prefix: 'p',
      darkModeSelector: '.dark', // Supports dark mode
      cssLayer: false,
    },
  },
})

app.mount('#app')
