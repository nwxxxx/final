<template>
  <div class="post-detail-container">
    <div v-if="post" class="post-content">
      <div class="post-header">
        <h1>{{ post.title }}</h1>
        <div class="post-meta">
          <span>作者: {{ post.username }}</span>
          <span>发布时间: {{ formatDate(post.created) }}</span>
          <div v-if="isAuthor" class="post-actions">
            <el-button type="primary" size="small" @click="showEditDialog">编辑</el-button>
            <el-button type="danger" size="small" @click="confirmDelete">删除</el-button>
          </div>
        </div>
      </div>
      
      <div class="post-body">
        {{ post.body }}
      </div>

      <!-- 评论区 -->
<!--      <div class="comments-section">-->
<!--        <h3>评论</h3>-->

<!--        &lt;!&ndash; 发表评论 &ndash;&gt;-->
<!--        <div class="comment-form">-->
<!--          <el-input-->
<!--            type="textarea"-->
<!--            v-model="newComment"-->
<!--            :rows="3"-->
<!--            placeholder="写下你的评论..."-->
<!--          ></el-input>-->
<!--          <el-button-->
<!--            type="primary"-->
<!--            @click="submitComment"-->
<!--            :loading="submitting"-->
<!--            :disabled="!newComment.trim()"-->
<!--          >-->
<!--            发表评论-->
<!--          </el-button>-->
<!--        </div>-->

<!--        &lt;!&ndash; 评论列表 &ndash;&gt;-->
<!--        <div class="comments-list">-->
<!--          <div v-for="comment in comments" :key="comment.id" class="comment-item">-->
<!--            <div class="comment-header">-->
<!--              <span class="comment-author">{{ comment.username }}</span>-->
<!--              <span class="comment-time">{{ formatDate(comment.created) }}</span>-->
<!--            </div>-->
<!--            <div class="comment-content">{{ comment.content }}</div>-->
<!--          </div>-->
<!--        </div>-->
<!--      </div>-->
    </div>

    <div v-else class="loading">
      <el-skeleton :rows="6" animated />
    </div>

    <!-- 编辑帖子对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑帖子"
      width="50%"
    >
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="editForm.title" placeholder="请输入标题"></el-input>
        </el-form-item>
        <el-form-item label="内容" required>
          <el-input
            type="textarea"
            v-model="editForm.body"
            :rows="6"
            placeholder="请输入内容"
          ></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="updatePost" :loading="submitting">
            保存
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'
import { ElMessageBox } from 'element-plus'

export default {
  name: 'PostDetail',
  data() {
    return {
      post: null,
      comments: [],
      newComment: '',
      submitting: false,
      editDialogVisible: false,
      editForm: {
        title: '',
        body: ''
      }
    }
  },
  computed: {
    isAuthor() {
      const userId = localStorage.getItem('userId')
      return this.post && userId && this.post.author_id === parseInt(userId)
    }
  },
  created() {
    this.fetchPostDetail()
    // this.fetchComments()
  },
  methods: {
    async fetchPostDetail() {
      try {
        const postId = this.$route.params.id
        const response = await axios.get(`/api/blog/${postId}`)
        this.post = response.data
      } catch (error) {
        this.$message.error('获取帖子详情失败')
      }
    },
    async fetchComments() {
      try {
        const postId = this.$route.params.id
        const response = await axios.get(`/api/blog/${postId}/comments`)
        this.comments = response.data.comments
      } catch (error) {
        this.$message.error('获取评论失败')
      }
    },
    async submitComment() {
      if (!this.newComment.trim()) return

      this.submitting = true
      try {
        const postId = this.$route.params.id
        await axios.post(`/api/blog/${postId}/comments`, {
          content: this.newComment
        })
        this.$message.success('评论成功')
        this.newComment = ''
        this.fetchComments()
      } catch (error) {
        this.$message.error('评论失败')
      } finally {
        this.submitting = false
      }
    },
    showEditDialog() {
      this.editForm = {
        title: this.post.title,
        body: this.post.body
      }
      this.editDialogVisible = true
    },
    async updatePost() {
      if (!this.editForm.title.trim() || !this.editForm.body.trim()) {
        this.$message.warning('标题和内容不能为空')
        return
      }

      this.submitting = true
      try {
        const postId = this.$route.params.id
        const token = localStorage.getItem('token')
        await axios.put(`/api/blog/${postId}`, this.editForm, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        this.$message.success('更新成功')
        this.editDialogVisible = false
        this.fetchPostDetail()
      } catch (error) {
        this.$message.error('更新失败')
      } finally {
        this.submitting = false
      }
    },
    async confirmDelete() {
      try {
        await ElMessageBox.confirm('确定要删除这篇帖子吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await this.deletePost()
      } catch {
        // 用户取消删除
      }
    },
    async deletePost() {
      try {
        const postId = this.$route.params.id
        const token = localStorage.getItem('token')
        await axios.delete(`/api/blog/${postId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        this.$message.success('删除成功')
        this.$router.push('/forum')
      } catch (error) {
        this.$message.error('删除失败')
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
.post-detail-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.post-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.post-header {
  margin-bottom: 20px;
}

.post-header h1 {
  margin: 0 0 10px 0;
  color: #333;
}

.post-meta {
  color: #666;
  font-size: 0.9em;
  display: flex;
  align-items: center;
  gap: 20px;
}

.post-actions {
  margin-left: auto;
  display: flex;
  gap: 10px;
}

.post-body {
  color: #333;
  line-height: 1.6;
  margin-bottom: 30px;
}

.comments-section {
  margin-top: 30px;
  border-top: 1px solid #eee;
  padding-top: 20px;
}

.comments-section h3 {
  margin-bottom: 20px;
  color: #333;
}

.comment-form {
  margin-bottom: 30px;
}

.comment-form .el-button {
  margin-top: 10px;
  float: right;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.comment-item {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.comment-author {
  font-weight: bold;
  color: #333;
}

.comment-time {
  color: #999;
  font-size: 0.9em;
}

.comment-content {
  color: #666;
  line-height: 1.5;
}

.loading {
  padding: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style> 