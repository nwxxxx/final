<template>
  <div class="nav-menu">
    <el-menu
      mode="horizontal"
      :router="true"
      :default-active="activeIndex"
    >
      <el-menu-item index="/">首页</el-menu-item>
      <el-menu-item index="/forum">论坛</el-menu-item>
      <div class="nav-right">
        <template v-if="isLoggedIn">
          <el-menu-item index="/profile">{{ username }}</el-menu-item>
          <el-menu-item @click="handleLogout">退出</el-menu-item>
        </template>
        <template v-else>
          <el-menu-item index="/login">登录</el-menu-item>
          <el-menu-item index="/register">注册</el-menu-item>
        </template>
      </div>
    </el-menu>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

export default {
  name: 'NavMenu',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const activeIndex = computed(() => route.path)
    const isLoggedIn = ref(false)
    const username = ref('')

    const checkLoginStatus = () => {
      const token = localStorage.getItem('token')
      const storedUsername = localStorage.getItem('username')
      isLoggedIn.value = !!token
      username.value = storedUsername || ''
    }

    const handleLogout = () => {
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('userId')
      isLoggedIn.value = false
      username.value = ''
      router.push('/login')
    }

    onMounted(() => {
      checkLoginStatus()
    })

    return {
      activeIndex,
      isLoggedIn,
      username,
      handleLogout
    }
  }
}
</script>

<style scoped>
.nav-menu {
  width: 100%;
}

.nav-right {
  float: right;
  display: flex;
  align-items: center;
}

.el-menu {
  border-bottom: none;
}
</style> 