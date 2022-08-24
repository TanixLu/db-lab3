import { createApp } from 'vue'
import App from './App.vue'
import installElementPlus from './plugins/element'
import router from './router'

const app = createApp(App)
app.use(router)
installElementPlus(app)
app.mount('#app')
