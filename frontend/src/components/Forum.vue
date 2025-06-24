<template>
  <div class="forum-container">
    <div class="forum-header">
      <h2>论坛</h2>
      <el-button type="primary" @click="showCreateDialog">发布新帖</el-button>
    </div>

    <div class="posts-list">
      <el-card v-for="post in posts" :key="post.id" class="post-card">
        <template #header>
          <div class="post-header">
            <router-link :to="`/forum/post/${post.id}`" class="post-title">
              {{ post.title }}
            </router-link>
            <span class="post-author">作者: {{ post.username }}</span>
          </div>
        </template>
        <div class="post-preview">{{ post.body }}</div>
        <div class="post-meta">
          <span class="post-time">发布时间: {{ formatDate(post.created) }}</span>
        </div>
      </el-card>
    </div>

    <!-- 发帖对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="发布新帖"
      width="50%"
    >
      <el-form :model="newPost" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="newPost.title" placeholder="请输入标题"></el-input>
        </el-form-item>
        <el-form-item label="内容" required>
          <el-input
            type="textarea"
            v-model="newPost.body"
            :rows="6"
            placeholder="请输入内容"
          ></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createPost" :loading="submitting">
            发布
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Forum',
  data() {
    return {
      posts: [],
      dialogVisible: false,
      newPost: {
        title: '',
        body: ''
      },
      submitting: false
    }
  },
  created() {
    this.fetchPosts()
  },
  methods: {
    async fetchPosts() {
      try {
        const response = await axios.get('/api/blog/')
        this.posts = response.data.posts
      } catch (error) {
        this.$message.error('获取帖子列表失败')
      }
    },
    showCreateDialog() {
      this.dialogVisible = true
      this.newPost = {
        title: '',
        body: ''
      }
    },
    async createPost() {
      if (!this.newPost.title.trim() || !this.newPost.body.trim()) {
        this.$message.warning('标题和内容不能为空')
        return
      }

      this.submitting = true
      try {
        const token = localStorage.getItem('token')
        await axios.post('/api/blog/', this.newPost, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        this.$message.success('发布成功')
        this.dialogVisible = false
        this.fetchPosts()
      } catch (error) {
        this.$message.error('发布失败')
      } finally {
        this.submitting = false
      }
    },
    formatDate(dateStr) {
      const date = new Date(dateStr)
      return date.toLocaleString()
    }
  }
}
</script>

<style scoped>
.forum-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.forum-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.forum-header h2 {
  margin: 0;
  color: #333;
}

.posts-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.post-card {
  transition: transform 0.2s;
}

.post-card:hover {
  transform: translateY(-2px);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.post-title {
  font-size: 1.2em;
  color: #333;
  text-decoration: none;
  font-weight: bold;
}

.post-title:hover {
  color: #409EFF;
}

.post-author {
  color: #666;
  font-size: 0.9em;
}

.post-preview {
  color: #666;
  margin: 10px 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-meta {
  color: #999;
  font-size: 0.9em;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style> 