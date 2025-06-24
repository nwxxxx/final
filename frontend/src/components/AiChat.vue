<template>
  <div class="ai-chat-container">
    <div class="chat-header">
      <h2>大模型问答</h2>
      <p class="chat-subtitle">智能问答系统</p>
    </div>

    <div class="chat-content">
      <div class="chat-messages" ref="chatMessages">
        <div 
          v-for="(message, index) in messages" 
          :key="index"
          :class="['message', message.isUser ? 'user-message' : 'ai-message']"
        >
          <div class="message-avatar">
            <i :class="message.isUser ? 'el-icon-user' : 'el-icon-cpu'"></i>
          </div>
          <div class="message-content">
            <div class="message-text" v-html="formatMessage(message.content)"></div>
            <div class="message-time">{{ formatTime(message.timestamp) }}</div>
          </div>
        </div>
        
        <!-- 加载状态 -->
        <div v-if="isLoading" class="message ai-message">
          <div class="message-avatar">
            <i class="el-icon-cpu"></i>
          </div>
          <div class="message-content">
            <div class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>

      <div class="chat-input">
        <el-input
          v-model="inputText"
          type="textarea"
          :rows="3"
          placeholder="请输入您的问题..."
          @keydown.ctrl.enter="sendMessage"
          :disabled="isLoading"
        />
        <div class="input-actions">
          <el-button 
            type="primary" 
            @click="sendMessage"
            :loading="isLoading"
            :disabled="!inputText.trim()"
          >
            <i class="el-icon-s-promotion"></i>
            发送 (Ctrl+Enter)
          </el-button>
          <el-button @click="clearChat">
            <i class="el-icon-delete"></i>
            清空
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AiChat',
  data() {
    return {
      messages: [],
      inputText: '',
      isLoading: false,
      apiKey: '03bfe97952bb441c9c3fc77487a10d33.v1OMdQCoSdYQjRr3' // API密钥
    }
  },
  mounted() {
    // 添加欢迎消息
    this.addWelcomeMessage()
    // 从localStorage恢复聊天记录
    this.loadChatHistory()
  },
  methods: {
    addWelcomeMessage() {
      const welcomeMessage = {
        content: '您好！我是AI助手。我可以回答各种问题，包括但不限于：\n\n• 知识问答\n• 技术咨询\n• 文本分析\n• 编程帮助\n• 创意写作\n\n请随时向我提问！',
        isUser: false,
        timestamp: new Date()
      }
      this.messages.push(welcomeMessage)
    },

    async sendMessage() {
      if (!this.inputText.trim() || this.isLoading) return

      const userMessage = {
        content: this.inputText.trim(),
        isUser: true,
        timestamp: new Date()
      }

      this.messages.push(userMessage)
      const questionText = this.inputText.trim()
      this.inputText = ''
      this.isLoading = true

      // 滚动到底部
      this.$nextTick(() => {
        this.scrollToBottom()
      })

      try {
        // 调用智谱清言API
        const response = await fetch('https://open.bigmodel.cn/api/paas/v4/chat/completions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.apiKey}`
          },
          body: JSON.stringify({
            "model": "glm-4-plus",
            "messages": [
              {
                "role": "user",
                "content": questionText
              }
            ],
            "do_sample": false,
            "temperature": 0.7,
            "max_tokens": 2048
          })
        })

        if (!response.ok) {
          throw new Error(`API请求失败: ${response.status}`)
        }

        const data = await response.json()
        console.log('API响应:', data)

        if (data.choices && data.choices.length > 0) {
          const aiResponse = data.choices[0].message.content
          const aiMessage = {
            content: aiResponse,
            isUser: false,
            timestamp: new Date()
          }
          this.messages.push(aiMessage)
        } else {
          throw new Error('API返回格式不正确: ' + JSON.stringify(data))
        }
      } catch (error) {
        console.error('调用智谱清言API时出错:', error)
        const errorMessage = {
          content: '很抱歉，我暂时无法回答您的问题。请稍后再试。\n\n错误信息：' + error.message,
          isUser: false,
          timestamp: new Date()
        }
        this.messages.push(errorMessage)
      } finally {
        this.isLoading = false
        this.saveChatHistory()
        this.$nextTick(() => {
          this.scrollToBottom()
        })
      }
    },

    clearChat() {
      this.$confirm('确定要清空聊天记录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.messages = []
        this.addWelcomeMessage()
        this.saveChatHistory()
        this.$message.success('聊天记录已清空')
      }).catch(() => {
        // 用户取消
      })
    },

    formatMessage(content) {
      // 简单的格式化：将换行符转换为<br>
      return content.replace(/\n/g, '<br>')
    },

    formatTime(timestamp) {
      const now = new Date()
      const time = new Date(timestamp)
      const diff = now - time

      if (diff < 60000) { // 1分钟内
        return '刚刚'
      } else if (diff < 3600000) { // 1小时内
        return Math.floor(diff / 60000) + '分钟前'
      } else if (diff < 86400000) { // 24小时内
        return Math.floor(diff / 3600000) + '小时前'
      } else {
        return time.toLocaleDateString() + ' ' + time.toLocaleTimeString()
      }
    },

    scrollToBottom() {
      const container = this.$refs.chatMessages
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    },

    saveChatHistory() {
      try {
        localStorage.setItem('ai-chat-history', JSON.stringify(this.messages))
      } catch (error) {
        console.warn('保存聊天记录失败:', error)
      }
    },

    loadChatHistory() {
      try {
        const history = localStorage.getItem('ai-chat-history')
        if (history) {
          const messages = JSON.parse(history)
          // 只保留非欢迎消息的历史记录
          this.messages = this.messages.concat(messages.filter(msg => 
            !msg.content.includes('您好！我是基于智谱清言')
          ))
        }
      } catch (error) {
        console.warn('加载聊天记录失败:', error)
      }
    }
  }
}
</script>

<style scoped>
.ai-chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 1200px;
  margin: 0 auto;
  background: #f5f5f5;
}

.chat-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.chat-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
}

.chat-subtitle {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: white;
}

.message {
  display: flex;
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease-in;
}

.user-message {
  justify-content: flex-end;
}

.ai-message {
  justify-content: flex-start;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 12px;
  font-size: 18px;
}

.user-message .message-avatar {
  background: #409eff;
  color: white;
  order: 2;
}

.ai-message .message-avatar {
  background: #67c23a;
  color: white;
}

.message-content {
  max-width: 70%;
  background: white;
  border-radius: 12px;
  padding: 12px 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  position: relative;
}

.user-message .message-content {
  background: #409eff;
  color: white;
}

.user-message .message-content::after {
  content: '';
  position: absolute;
  right: -8px;
  top: 12px;
  width: 0;
  height: 0;
  border: 8px solid transparent;
  border-left-color: #409eff;
}

.ai-message .message-content::after {
  content: '';
  position: absolute;
  left: -8px;
  top: 12px;
  width: 0;
  height: 0;
  border: 8px solid transparent;
  border-right-color: white;
}

.message-text {
  line-height: 1.6;
  word-wrap: break-word;
}

.message-time {
  font-size: 12px;
  opacity: 0.7;
  margin-top: 8px;
  text-align: right;
}

.user-message .message-time {
  color: rgba(255,255,255,0.8);
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #409eff;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.chat-input {
  background: white;
  padding: 20px;
  border-top: 1px solid #eee;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .message-content {
    max-width: 85%;
  }
  
  .chat-header {
    padding: 15px;
  }
  
  .chat-header h2 {
    font-size: 20px;
  }
  
  .chat-messages {
    padding: 15px;
  }
  
  .input-actions {
    flex-direction: column;
    gap: 10px;
  }
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style> 