// 从vue-router导入createRouter和createWebHistory
// createRouter用于创建路由器实例，createWebHistory用于创建基于HTML5 History API的history对象
import {createRouter, createWebHistory} from 'vue-router'

// 导入各个组件，这些组件将用作路由的匹配组件
import Welcome from './components/Welcome.vue'
import Loan from './components/Loan.vue'
import Stock from './components/Stock.vue'
import Report from './components/Report.vue'
import Login from './components/Login.vue'
import Register from './components/Register.vue'
import Forum from './components/Forum.vue'
import Home from './components/Home.vue'
import AiChat from './components/AiChat.vue'

// 定义路由配置数组routes
// 每个路由对象包含path属性（路由路径）和component属性（对应路径下的组件）
const routes = [
    // 根路径'/'对应显示Welcome组件
    {
        path: '/',
        component: Welcome,
        meta: {requiresAuth: false}
    },
    // 路径'/loan'对应显示Loan组件
    {
        path: '/loan',
        component: Loan,
        meta: {requiresAuth: true}
    },
    // 路径'/stock'对应显示Stock组件
    {
        path: '/stock',
        component: Stock,
        meta: {requiresAuth: true}
    },
    // 路径'/report'对应显示Report组件
    {
        path: '/report',
        component: Report,
        meta: {requiresAuth: true}
    },
    // 路径'/ai-chat'对应显示AiChat组件
    {
        path: '/ai-chat',
        component: AiChat,
        meta: {requiresAuth: true}
    },
    {
        path: '/forum',
        name: 'Forum',
        component: Forum,
        meta: {requiresAuth: true}
    },
    {
        path: '/forum/post/:id',
        name: 'PostDetail',
        component: () => import('./components/PostDetail.vue'),
        meta: {requiresAuth: true}
    },
    {
        path: '/login',
        name: 'Login',
        component: Login,
        meta: {requiresAuth: false}
    },
    {
        path: '/register',
        name: 'Register',
        component: Register,
        meta: {requiresAuth: false}
    },
    {
        path: '/',
        name: 'Home',
        component: Home,
        meta: {requiresAuth: true}
    }
]

// 使用createRouter函数和createWebHistory创建路由器实例
// 并导出这个实例供其他文件使用
const router = createRouter({
    // 指定history模式为基于HTML5 History API的history模式
    history: createWebHistory(),
    // 将定义的路由配置传入路由器实例
    routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token')

    if (to.meta.requiresAuth && !token) {
        // 需要登录但未登录，重定向到登录页
        next('/login')
    } else if (!to.meta.requiresAuth && token && (to.path === '/login' || to.path === '/register')) {
        // 已登录但访问登录/注册页，重定向到首页
        next('/')
    } else {
        next()
    }
})

export default router
