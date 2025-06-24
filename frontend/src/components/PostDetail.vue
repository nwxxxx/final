<template>
  <div class="post-detail">
    <el-card v-if="post" class="post-card">
      <template #header>
        <div class="post-header">
          <h2>{{ post.title }}</h2>
          <div class="post-meta">
            <span>作者: {{ post.username }}</span>
            <span>发布时间: {{ formatDate(post.created) }}</span>
          </div>
        </div>
      </template>
      <div class="post-body">
        {{ post.body }}
      </div>
      <div class="post-actions" v-if="canEditPost">
        <el-button type="primary" @click="editPost">编辑</el-button>
        <el-button type="danger" @click="deletePost">删除</el-button>
      </div>
    </el-card>
  </div>
</template>

<script>
import {ref, computed, onMounted} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {ElMessage, ElMessageBox} from 'element-plus'

export default {
  name: 'PostDetail',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const post = ref(null)
    const userId = ref(null)
    
    const initUser = () => {
      const storedUserId = localStorage.getItem('userId')
      
      if (storedUserId && storedUserId !== 'null' && storedUserId !== 'undefined') {
        const parsedId = parseInt(storedUserId)
        if (!isNaN(parsedId)) {
          userId.value = parsedId
        } else {
          clearInvalidSession()
        }
      } else {
        const token = localStorage.getItem('token')
        if (token) {
          clearInvalidSession()
        }
      }
    }

    const clearInvalidSession = () => {
      localStorage.removeItem('userId')
      localStorage.removeItem('user_id')
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      ElMessage.warning('用户信息异常，请重新登录')
      router.push('/login')
    }

    const canEditPost = computed(() => {
      if (!post.value || !userId.value) return false
      return Number(post.value.author_id) === Number(userId.value)
    })

    const fetchPost = async () => {
      try {
        const response = await fetch(`http://localhost:5000/api/blog/${route.params.id}`)
        if (!response.ok) {
          throw new Error('Post not found')
        }
        post.value = await response.json()
      } catch (error) {
        console.error('Error fetching post:', error)
        ElMessage.error('获取帖子详情失败')
        router.push('/forum')
      }
    }

    const editPost = () => {
      router.push({
        path: '/forum',
        query: { editPostId: route.params.id }
      })
    }

    const deletePost = async () => {
      try {
        await ElMessageBox.confirm('确定要删除这篇帖子吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        const token = localStorage.getItem('token')
        const response = await fetch(`http://localhost:5000/api/blog/${route.params.id}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        if (response.ok) {
          ElMessage.success('删除成功')
          router.push('/forum')
        } else {
          const error = await response.json()
          ElMessage.error(error.error || '删除失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Error deleting post:', error)
          ElMessage.error('删除失败')
        }
      }
    }

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    onMounted(() => {
      initUser()
      fetchPost()
    })

    return {
      post,
      userId,
      canEditPost,
      editPost,
      deletePost,
      formatDate
    }
  }
}
</script>

<style scoped>
.post-detail {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.post-card {
  margin-bottom: 30px;
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.post-header h2 {
  margin: 0;
  color: #303133;
}

.post-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  font-size: 14px;
  color: #909399;
}

.post-body {
  margin: 20px 0;
  color: #606266;
  white-space: pre-wrap;
  line-height: 1.6;
}

.post-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}
</style>
