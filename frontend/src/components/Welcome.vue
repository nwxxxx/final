<template>
  <!-- 欢迎页面根容器 -->
  <div class="welcome-container">
    <!-- 使用Element UI的Card组件作为欢迎卡片容器 -->
    <el-card class="welcome-card">
      <template #header>
        <div class="card-header">
          <h2>欢迎使用论坛系统</h2>
          <div class="time-display">
            <span class="current-time">{{ currentTime }}</span>
            <span class="current-date">{{ currentDate }}</span>
          </div>
        </div>
      </template>
      
      <div class="card-content">
        <!-- 只在登录后显示用户信息 -->
        <div v-if="isLoggedIn" class="user-info">
          <p>当前用户：{{ username }}</p>
          <p>登录时间：{{ loginTime }}</p>
        </div>
        <div v-else class="login-prompt">
          <p>请登录系统以查看个人信息</p>
          <el-button 
            type="primary" 
            size="small"
            @click="navigateToLogin"
          >
            立即登录
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'Welcome',  // 组件名称(必须)
  
  // 组件数据
  data() {
    return {
      loginTime: '',
      currentTime: '',
      currentDate: '',
      timer: null
    }
  },
  
  computed: {
    // 检查用户是否已登录
    isLoggedIn() {
      return localStorage.getItem('token') && localStorage.getItem('username')
    },
    
    // 从本地存储获取用户名
    username() {
      return localStorage.getItem('username') || ''
    }
  },
  
  // 生命周期钩子 - 组件创建时调用
  created() {
    this.updateTime()
    this.timer = setInterval(this.updateTime, 1000)
    
    // 如果已登录，设置登录时间
    if (this.isLoggedIn) {
      this.loginTime = new Date().toLocaleString()
    }
  },
  
  // 方法定义
  methods: {
    updateTime() {
      const now = new Date()
      this.currentTime = now.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      })
      this.currentDate = now.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long'
      })
    },
    
    // 导航到登录页面
    navigateToLogin() {
      this.$router.push('/login')
    }
  },
  
  // 组件销毁时清除定时器
  beforeUnmount() {
    if (this.timer) {
      clearInterval(this.timer)
    }
  }
}
</script>

<style scoped>
/* 页面容器样式 */
.welcome-container {
  max-width: 800px;
  margin: 20px auto;
  padding: 0 20px;
}

/* 卡片样式 */
.welcome-card {
  background: white;
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  color: #333;
}

.time-display {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.current-time {
  font-size: 1.2rem;
  font-weight: bold;
  color: #409EFF;
}

.current-date {
  font-size: 0.9rem;
  color: #666;
}

.card-content {
  padding: 20px 0;
}

.user-info {
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 4px;
}

.user-info p {
  margin: 5px 0;
  color: #666;
}

.login-prompt {
  text-align: center;
  padding: 30px 0;
  color: #606266;
}

.login-prompt p {
  margin-bottom: 15px;
}
</style>