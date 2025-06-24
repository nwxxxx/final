<template>
  <div class="home">
    <header class="header">
      <h1>论坛首页</h1>
      <div class="user-info">
        <div class="time-info">
          <span class="current-time">{{ currentTime }}</span>
          <span class="current-date">{{ currentDate }}</span>
        </div>
        <div class="user-welcome">
          欢迎，{{ username }}
          <button @click="handleLogout" class="logout-btn">退出登录</button>
        </div>
      </div>
    </header>
    <div class="content">
      <h2>帖子列表</h2>
      <!-- 这里后续会添加帖子列表 -->
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home',
  data() {
    return {
      username: '',
      currentTime: '',
      currentDate: '',
      timer: null
    }
  },
  created() {
    // 从localStorage获取用户信息
    this.username = localStorage.getItem('username') || ''
    // 初始化时间
    this.updateTime()
    // 设置定时器，每秒更新一次时间
    this.timer = setInterval(this.updateTime, 1000)
  },
  beforeUnmount() {
    // 组件销毁前清除定时器
    if (this.timer) {
      clearInterval(this.timer)
    }
  },
  methods: {
    updateTime() {
      const now = new Date()
      // 格式化时间：HH:mm:ss
      this.currentTime = now.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      })
      // 格式化日期：YYYY年MM月DD日 星期X
      this.currentDate = now.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long'
      })
    },
    handleLogout() {
      // 清除本地存储的token和用户信息
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('userId')
      // 跳转到登录页
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.header {
  background-color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.time-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  color: #666;
}

.current-time {
  font-size: 1.2rem;
  font-weight: bold;
  color: #409EFF;
}

.current-date {
  font-size: 0.9rem;
}

.user-welcome {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logout-btn {
  padding: 0.5rem 1rem;
  background-color: #ff4444;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.logout-btn:hover {
  background-color: #cc0000;
}

.content {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 1rem;
}

h1 {
  margin: 0;
  color: #333;
}

h2 {
  color: #666;
  margin-bottom: 1rem;
}
</style> 