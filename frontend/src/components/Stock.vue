<template>
  <div class="stock-valuation">
    <div class="header">
      <h1>股票DCF估值系统</h1>
      <p class="subtitle">基于自由现金流折现模型的股票估值分析</p>
    </div>

    <!-- 股票搜索区域 -->
    <div class="search-section">
      <el-card class="search-card">
        <div slot="header">
          <span>股票信息</span>
        </div>
        <div class="search-content">
          <div class="search-input">
            <el-input
              v-model="stockInput"
              placeholder="请输入股票代码或公司名称（如：000001 或 平安银行）"
              @keyup.enter="searchStock"
              :loading="searching"
            >
              <el-button slot="append" @click="searchStock" :loading="searching">
                <i class="el-icon-search"></i>
                搜索
              </el-button>
            </el-input>
          </div>
          
          <div v-if="stockInfo.code" class="stock-info">
            <el-alert
              :title="`${stockInfo.name} (${stockInfo.code})`"
              type="success"
              :closable="false"
              show-icon
            />
            <div class="market-data" v-if="marketData">
              <div class="price-info">
                <span class="current-price">¥{{ marketData.current_price }}</span>
                <span :class="['price-change', marketData.change_percent >= 0 ? 'positive' : 'negative']">
                  {{ marketData.change_percent >= 0 ? '+' : '' }}{{ marketData.change_percent }}%
                </span>
              </div>
              <div class="market-metrics">
                <span>PE: {{ marketData.pe_ratio || 'N/A' }}</span>
                <span>PB: {{ marketData.pb_ratio || 'N/A' }}</span>
                <span>成交量: {{ formatNumber(marketData.volume) }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- DCF参数设置区域 -->
    <div class="parameters-section" v-if="stockInfo.code">
      <el-card class="parameters-card">
        <div slot="header">
          <span>DCF模型参数设置</span>
          <el-button 
            type="text" 
            @click="resetParameters"
            style="float: right; padding: 3px 0"
          >
            重置默认值
          </el-button>
        </div>
        <div class="parameters-content">
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="param-group">
                <h4>基础参数</h4>
                <el-form :model="dcfParams" label-width="120px">
                  <el-form-item label="折现率 (%)">
                    <el-input-number
                      v-model="dcfParams.discount_rate"
                      :min="0.01"
                      :max="0.30"
                      :step="0.01"
                      :precision="2"
                      size="small"
                    />
                    <span class="param-help">建议范围：8%-15%</span>
                  </el-form-item>
                </el-form>
              </div>
            </el-col>
                         <el-col :span="12">
               <div class="param-group">
                 <h4>增长阶段设置</h4>
                 <div class="stage-params">
                   <!-- 第一阶段 -->
                   <div class="stage-section">
                     <h5>第一阶段（高增长期）</h5>
                     <el-form :model="dcfParams" label-width="80px" size="small">
                       <el-row :gutter="10">
                         <el-col :span="12">
                           <el-form-item label="年数">
                             <el-input-number v-model="dcfParams.stage1_years" :min="1" :max="10" />
                           </el-form-item>
                         </el-col>
                         <el-col :span="12">
                           <el-form-item label="增长率">
                             <el-input-number 
                               v-model="dcfParams.stage1_growth" 
                               :min="0" 
                               :max="1" 
                               :step="0.01" 
                               :precision="2" 
                             />
                           </el-form-item>
                         </el-col>
                       </el-row>
                     </el-form>
                   </div>

                   <!-- 第二阶段 -->
                   <div class="stage-section">
                     <h5>第二阶段（中期增长）</h5>
                     <el-form :model="dcfParams" label-width="80px" size="small">
                       <el-row :gutter="10">
                         <el-col :span="12">
                           <el-form-item label="年数">
                             <el-input-number v-model="dcfParams.stage2_years" :min="0" :max="10" />
                           </el-form-item>
                         </el-col>
                         <el-col :span="12">
                           <el-form-item label="增长率">
                             <el-input-number 
                               v-model="dcfParams.stage2_growth" 
                               :min="0" 
                               :max="1" 
                               :step="0.01" 
                               :precision="2" 
                             />
                           </el-form-item>
                         </el-col>
                       </el-row>
                     </el-form>
                   </div>

                   <!-- 第三阶段（永续增长） -->
                   <div class="stage-section">
                     <h5>永续增长期</h5>
                     <el-form :model="dcfParams" label-width="80px" size="small">
                       <el-form-item label="增长率">
                         <el-input-number 
                           v-model="dcfParams.stage3_growth" 
                           :min="0" 
                           :max="0.05" 
                           :step="0.001" 
                           :precision="3" 
                         />
                         <div class="param-help">建议不超过GDP增长率（约3%）</div>
                       </el-form-item>
                     </el-form>
                   </div>
                 </div>
               </div>
             </el-col>
          </el-row>
          
          <div class="calculate-section">
            <el-button 
              type="primary" 
              size="large"
              @click="calculateValuation"
              :loading="calculating"
              :disabled="!stockInfo.code"
            >
              <i class="el-icon-s-finance"></i>
              开始估值计算
            </el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 估值结果展示区域 -->
    <div class="results-section" v-if="valuationResult">
      <el-card class="results-card">
        <div slot="header">
          <span>估值结果</span>
          <el-tag 
            :type="getValuationTag()"
            style="float: right;"
          >
            {{ getValuationText() }}
          </el-tag>
        </div>
        <div class="results-content">
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="result-item">
                <div class="result-label">DCF估值价格</div>
                <div class="result-value primary">¥{{ valuationResult.price_per_share }}</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="result-item">
                <div class="result-label">当前市价</div>
                <div class="result-value">¥{{ valuationResult.current_market_price }}</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="result-item">
                <div class="result-label">估值倍数</div>
                <div :class="['result-value', getValueClass()]">{{ valuationResult.valuation_ratio }}x</div>
              </div>
            </el-col>
          </el-row>

          <el-divider />

          <el-row :gutter="20">
            <el-col :span="12">
              <div class="detail-section">
                <h4>财务数据概览</h4>
                <el-descriptions :column="1" border size="small">
                  <el-descriptions-item label="平均自由现金流">{{ valuationResult.avg_fcf }}亿元</el-descriptions-item>
                  <el-descriptions-item label="企业价值">{{ valuationResult.enterprise_value }}亿元</el-descriptions-item>
                  <el-descriptions-item label="总股本">{{ valuationResult.total_shares }}亿股</el-descriptions-item>
                  <el-descriptions-item label="数据年份">{{ valuationResult.financial_years }}年</el-descriptions-item>
                </el-descriptions>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="detail-section">
                <h4>历年自由现金流</h4>
                <div class="fcf-chart">
                  <div 
                    v-for="(fcf, index) in valuationResult.fcf_history" 
                    :key="index"
                    class="fcf-bar"
                  >
                    <div class="fcf-value">{{ fcf }}亿</div>
                    <div 
                      class="fcf-bar-fill"
                      :style="{height: Math.max(20, Math.min(120, Math.abs(fcf) * 2)) + 'px', backgroundColor: fcf >= 0 ? '#67c23a' : '#f56c6c'}"
                    ></div>
                    <div class="fcf-year">{{ 2024 - index }}年</div>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>

          <el-divider />

          <div class="parameters-summary">
            <h4>计算参数</h4>
            <el-tag v-for="(value, key) in formatParameters()" :key="key" style="margin-right: 10px; margin-bottom: 5px;">
              {{ key }}: {{ value }}
            </el-tag>
          </div>

          <!-- 数据来源警告 -->
          <div v-if="valuationResult.warning" class="data-warning">
            <el-alert
              :title="valuationResult.warning"
              type="warning"
              :closable="false"
              show-icon
            />
          </div>

          <div class="investment-advice">
            <el-alert
              :title="getInvestmentAdvice()"
              :type="getAdviceType()"
              :closable="false"
              show-icon
            />
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Stock',
  data() {
    return {
      stockInput: '',
      searching: false,
      calculating: false,
      stockInfo: {
        code: '',
        name: ''
      },
             marketData: null,
       dcfParams: {
        discount_rate: 0.10,  // 10%
        stage1_years: 5,
        stage1_growth: 0.10,  // 10%
        stage2_years: 5,
        stage2_growth: 0.05,  // 5%
        stage3_years: 0,      // 永续
        stage3_growth: 0.025  // 2.5%
      },
      valuationResult: null
    }
  },
  methods: {
    async searchStock() {
      if (!this.stockInput.trim()) {
        this.$message.warning('请输入股票代码或公司名称')
        return
      }

      this.searching = true
      try {
        const token = localStorage.getItem('token')
                 const response = await fetch('http://localhost:5000/stock/search', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            stock_input: this.stockInput.trim()
          })
        })

        const data = await response.json()
        if (response.ok && data.success) {
          this.stockInfo = {
            code: data.stock_code,
            name: data.stock_name
          }
          await this.getMarketData()
          this.$message.success('股票信息获取成功')
        } else {
          this.$message.error(data.error || '搜索失败')
          this.stockInfo = { code: '', name: '' }
          this.marketData = null
        }
      } catch (error) {
        this.$message.error('网络请求失败')
        console.error('搜索股票失败:', error)
      } finally {
        this.searching = false
      }
    },

    async getMarketData() {
      if (!this.stockInfo.code) return

      try {
        const token = localStorage.getItem('token')
                 const response = await fetch(`http://localhost:5000/stock/market-data/${this.stockInfo.code}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        const data = await response.json()
        if (response.ok && data.success) {
          this.marketData = data.market_data
        }
      } catch (error) {
        console.error('获取市场数据失败:', error)
      }
    },

    async calculateValuation() {
      if (!this.stockInfo.code) {
        this.$message.warning('请先搜索股票')
        return
      }

      this.calculating = true
      try {
        const token = localStorage.getItem('token')
                 const response = await fetch('http://localhost:5000/stock/valuation', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            stock_code: this.stockInfo.code,
            ...this.dcfParams
          })
        })

        const data = await response.json()
        if (response.ok && data.success) {
          this.valuationResult = data.valuation_result
          this.$message.success('估值计算完成')
          
          // 滚动到结果区域
          this.$nextTick(() => {
            const resultsSection = document.querySelector('.results-section')
            if (resultsSection) {
              resultsSection.scrollIntoView({ behavior: 'smooth' })
            }
          })
        } else {
          this.$message.error(data.error || '估值计算失败')
        }
      } catch (error) {
        this.$message.error('网络请求失败')
        console.error('计算估值失败:', error)
      } finally {
        this.calculating = false
      }
    },

    resetParameters() {
      this.dcfParams = {
        discount_rate: 0.10,
        stage1_years: 5,
        stage1_growth: 0.10,
        stage2_years: 5,
        stage2_growth: 0.05,
        stage3_years: 0,
        stage3_growth: 0.025
      }
      this.$message.success('参数已重置为默认值')
    },

    getValuationTag() {
      if (!this.valuationResult) return 'info'
      const ratio = this.valuationResult.valuation_ratio
      if (ratio > 1.2) return 'success'
      if (ratio > 0.8) return 'warning'
      return 'danger'
    },

    getValuationText() {
      if (!this.valuationResult) return '未估值'
      const ratio = this.valuationResult.valuation_ratio
      if (ratio > 1.2) return '被低估'
      if (ratio > 0.8) return '合理估值'
      return '被高估'
    },

    getValueClass() {
      if (!this.valuationResult) return ''
      const ratio = this.valuationResult.valuation_ratio
      if (ratio > 1.2) return 'positive'
      if (ratio < 0.8) return 'negative'
      return ''
    },

    getInvestmentAdvice() {
      if (!this.valuationResult) return ''
      const ratio = this.valuationResult.valuation_ratio
      const price = this.valuationResult.price_per_share
      const marketPrice = this.valuationResult.current_market_price
      
      if (ratio > 1.3) {
        return `根据DCF模型，该股票被严重低估。理论价值¥${price}，当前市价¥${marketPrice}，具有较高投资价值。`
      } else if (ratio > 1.1) {
        return `根据DCF模型，该股票被适度低估。理论价值¥${price}，当前市价¥${marketPrice}，可考虑逢低买入。`
      } else if (ratio > 0.9) {
        return `根据DCF模型，该股票估值合理。理论价值¥${price}，当前市价¥${marketPrice}，可持有观望。`
      } else if (ratio > 0.7) {
        return `根据DCF模型，该股票被适度高估。理论价值¥${price}，当前市价¥${marketPrice}，建议谨慎投资。`
      } else {
        return `根据DCF模型，该股票被严重高估。理论价值¥${price}，当前市价¥${marketPrice}，建议回避。`
      }
    },

    getAdviceType() {
      if (!this.valuationResult) return 'info'
      const ratio = this.valuationResult.valuation_ratio
      if (ratio > 1.2) return 'success'
      if (ratio > 0.8) return 'warning'
      return 'error'
    },

    formatParameters() {
      const params = this.valuationResult?.parameters || this.dcfParams
      return {
        '折现率': (params.discount_rate * 100).toFixed(1) + '%',
        '第一阶段': `${params.stage1_years}年 ${(params.stage1_growth * 100).toFixed(1)}%`,
        '第二阶段': `${params.stage2_years}年 ${(params.stage2_growth * 100).toFixed(1)}%`,
        '永续增长': (params.stage3_growth * 100).toFixed(1) + '%'
      }
    },

    formatNumber(num) {
      if (!num) return '0'
      if (num >= 100000000) {
        return (num / 100000000).toFixed(1) + '亿'
      } else if (num >= 10000) {
        return (num / 10000).toFixed(1) + '万'
      }
      return num.toString()
    }
  }
}
</script>

<style scoped>
.stock-valuation {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  background: #f5f7fa;
  min-height: 100vh;
}

.header {
  text-align: center;
  margin-bottom: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.header h1 {
  margin: 0 0 10px 0;
  font-size: 32px;
  font-weight: 600;
}

.subtitle {
  margin: 0;
  font-size: 16px;
  opacity: 0.9;
}

.search-section,
.parameters-section,
.results-section {
  margin-bottom: 30px;
}

.search-card,
.parameters-card,
.results-card {
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}

.search-content {
  text-align: center;
}

.search-input {
  max-width: 600px;
  margin: 0 auto 20px;
}

.stock-info {
  max-width: 600px;
  margin: 0 auto;
  text-align: left;
}

.market-data {
  margin-top: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.price-info {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
}

.current-price {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.price-change {
  font-size: 16px;
  font-weight: 500;
}

.price-change.positive {
  color: #67c23a;
}

.price-change.negative {
  color: #f56c6c;
}

.market-metrics {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #606266;
}

.param-group h4 {
  margin: 0 0 15px 0;
  color: #303133;
  border-bottom: 2px solid #409eff;
  padding-bottom: 8px;
}

.stage-params {
  margin-top: 15px;
}

.stage-section {
  background: #fafafa;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
}

.stage-section h5 {
  margin: 0 0 15px 0;
  color: #409eff;
  font-size: 14px;
  font-weight: 600;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 8px;
}

.param-help {
  font-size: 12px;
  color: #909399;
  margin-left: 10px;
}

.calculate-section {
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.results-content {
  padding: 20px;
}

.result-item {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.result-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.result-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.result-value.primary {
  color: #409eff;
}

.result-value.positive {
  color: #67c23a;
}

.result-value.negative {
  color: #f56c6c;
}

.detail-section h4 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 16px;
}

.fcf-chart {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 180px;
  background: linear-gradient(to top, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.fcf-bar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  min-width: 70px;
}

.fcf-value {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  background: rgba(255, 255, 255, 0.9);
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  white-space: nowrap;
}

.fcf-bar-fill {
  width: 40px;
  border-radius: 6px 6px 0 0;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
  border: 1px solid rgba(255,255,255,0.3);
}

.fcf-bar-fill:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.fcf-year {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.8);
  padding: 2px 6px;
  border-radius: 4px;
}

.parameters-summary {
  margin: 20px 0;
}

.parameters-summary h4 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 16px;
}

.data-warning {
  margin: 20px 0;
}

.investment-advice {
  margin-top: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stock-valuation {
    padding: 10px;
  }
  
  .header {
    padding: 20px;
  }
  
  .header h1 {
    font-size: 24px;
  }
  
  .current-price {
    font-size: 20px;
  }
  
  .market-metrics {
    flex-direction: column;
    gap: 8px;
  }
  
  .fcf-chart {
    height: 100px;
    padding: 15px;
  }
}

/* 动画效果 */
.search-card,
.parameters-card,
.results-card {
  transition: all 0.3s ease;
}

.search-card:hover,
.parameters-card:hover,
.results-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}

.result-item {
  transition: all 0.3s ease;
}

.result-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
</style>
