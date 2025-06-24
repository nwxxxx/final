// 导入Vue 3的createApp函数，用于创建Vue应用实例
import { createApp } from 'vue'
// 导入Element Plus库，这是一个基于Vue 3的UI组件库
import ElementPlus from 'element-plus'
// 导入Element Plus的样式文件，确保UI组件能正确显示样式
import 'element-plus/dist/index.css'
// 导入根组件App，这是应用的入口组件
import App from './App.vue'
// 导入路由配置，用于设置应用的路由规则
import router from './router'
// 导入axios库
import axios from 'axios'

// 配置axios默认值
axios.defaults.baseURL = 'http://localhost:5000'
axios.defaults.headers.common['Content-Type'] = 'application/json'

// 从localStorage获取token
const token = localStorage.getItem('token')
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

// 创建Vue应用实例
const app = createApp(App)
// 将Element Plus库应用到Vue实例中，使其组件可以在应用中使用
app.use(ElementPlus)
// 将路由配置应用到Vue实例中，启用Vue Router功能
app.use(router)
// 将Vue应用挂载到页面中id为'app'的元素上，启动应用
app.mount('#app')