<template>
  <div class="forum-container">
    <div class="forum-header">
      <h2>论坛</h2>
      <el-button type="primary" @click="showCreateDialog">发布新帖</el-button>
    </div>

    <div class="forum-content">
      <el-card v-for="post in posts" :key="post.id" class="post-card">
        <template #header>
          <div class="post-header">
            <h3>{{ post.title }}</h3>
            <div class="post-meta">
              <span>作者: {{ post.username }}</span>
              <span>发布时间: {{ formatDate(post.created) }}</span>
            </div>
          </div>
        </template>
        <div class="post-body">
          {{ post.body }}
        </div>
        <div class="post-actions">
          <el-button type="text" @click="viewPost(post.id)">查看详情</el-button>
          <template v-if="post.author_id === userId">
            <el-button type="text" @click="showEditDialog(post)">编辑</el-button>
            <el-button type="text" @click="deletePost(post.id)">删除</el-button>
          </template>
        </div>
      </el-card>
    </div>

    <!-- 帖子编辑/创建对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑帖子' : '发布新帖'"
      width="50%"
    >
      <el-form :model="postForm" :rules="rules" ref="postFormRef">
        <el-form-item label="标题" prop="title">
          <el-input v-model="postForm.title" placeholder="请输入标题"></el-input>
        </el-form-item>
        <el-form-item label="内容" prop="body">
          <el-input
            v-model="postForm.body"
            type="textarea"
            :rows="4"
            placeholder="请输入内容"
          ></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitPost">{{ isEditing ? '保存修改' : '发布' }}</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'Forum',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const posts = ref([])
    const dialogVisible = ref(false)
    const isEditing = ref(false)
    const postFormRef = ref(null)
    const postForm = ref({
      id: null,
      title: '',
      body: ''
    })
    const userId = ref(parseInt(localStorage.getItem('userId')))

    const rules = {
      title: [
        { required: true, message: '请输入标题', trigger: 'blur' },
        { min: 3, max: 100, message: '长度在 3 到 100 个字符', trigger: 'blur' }
      ],
      body: [
        { required: true, message: '请输入内容', trigger: 'blur' },
        { min: 10, message: '内容至少 10 个字符', trigger: 'blur' }
      ]
    }

    const fetchPosts = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/blog/')
        const data = await response.json()
        posts.value = data
      } catch (error) {
        console.error('Error fetching posts:', error)
        ElMessage.error('获取帖子列表失败')
      }
    }

    const showCreateDialog = () => {
      isEditing.value = false
      postForm.value = {
        id: null,
        title: '',
        body: ''
      }
      dialogVisible.value = true
    }

    const showEditDialog = (post) => {
      isEditing.value = true
      postForm.value = {
        id: post.id,
        title: post.title,
        body: post.body
      }
      dialogVisible.value = true
    }

    const handleEditFromQuery = () => {
      if (route.query.editPostId) {
        const postToEdit = posts.value.find(p => p.id == route.query.editPostId)
        if (postToEdit) {
          showEditDialog(postToEdit)
          // 清除query参数避免重复触发
          router.replace({ query: {} })
        }
      }
    }

    const submitPost = async () => {
      try {
        await postFormRef.value.validate()
        
        const token = localStorage.getItem('token')
        const url = isEditing.value 
          ? `http://localhost:5000/api/blog/${postForm.value.id}`
          : 'http://localhost:5000/api/blog/'
        
        const method = isEditing.value ? 'PUT' : 'POST'
        
        const response = await fetch(url, {
          method,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            title: postForm.value.title,
            body: postForm.value.body
          })
        })

        if (response.ok) {
          ElMessage.success(isEditing.value ? '修改成功' : '发布成功')
          dialogVisible.value = false
          await fetchPosts()
        } else {
          const error = await response.json()
          ElMessage.error(error.error || (isEditing.value ? '修改失败' : '发布失败'))
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Error submitting post:', error)
        }
      }
    }

    const viewPost = (id) => {
      router.push(`/forum/post/${id}`)
    }

    const deletePost = async (id) => {
      try {
        await ElMessageBox.confirm('确定要删除这篇帖子吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        const token = localStorage.getItem('token')
        const response = await fetch(`http://localhost:5000/api/blog/${id}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        if (response.ok) {
          ElMessage.success('删除成功')
          await fetchPosts()
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

    // 监听路由变化
    watch(() => route.query, (newQuery) => {
      if (newQuery.editPostId) {
        handleEditFromQuery()
      }
    })

    onMounted(() => {
      fetchPosts().then(() => {
        handleEditFromQuery()
      })
    })

    return {
      posts,
      dialogVisible,
      isEditing,
      postForm,
      postFormRef,
      userId,
      rules,
      showCreateDialog,
      showEditDialog,
      submitPost,
      viewPost,
      deletePost,
      formatDate
    }
  }
}
</script>

<style scoped>
.forum-container {
  padding: 20px;
}

.forum-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.forum-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.post-card {
  margin-bottom: 20px;
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.post-header h3 {
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
  margin: 10px 0;
  color: #606266;
  white-space: pre-wrap;
}

.post-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
