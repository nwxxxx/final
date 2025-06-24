<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>股票估值系统 - DCF模型分析</title>
  <!-- 引入Element UI样式 -->
  <link rel="stylesheet" href="https://unpkg.com/element-ui/lib/theme-chalk/index.css">
  <!-- 引入Vue和Element UI -->
  <script src="https://cdn.jsdelivr.net/npm/vue@2.6.14/dist/vue.js"></script>
  <script src="https://unpkg.com/element-ui/lib/index.js"></script>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: 'Helvetica Neue', Arial, sans-serif;
    }
    
    body {
      background: linear-gradient(135deg, #f5f7fa 0%, #e4edf5 100%);
      min-height: 100vh;
      padding: 20px;
      color: #333;
    }
    
    .stock-app {
      max-width: 1200px;
      margin: 0 auto;
    }
    
    .app-header {
      text-align: center;
      padding: 30px 0;
      margin-bottom: 30px;
    }
    
    .app-title {
      font-size: 36px;
      color: #2c3e50;
      margin-bottom: 10px;
      font-weight: 600;
      letter-spacing: 1px;
      text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    .app-subtitle {
      font-size: 18px;
      color: #7f8c8d;
      max-width: 800px;
      margin: 0 auto;
      line-height: 1.6;
    }
    
    .main-container {
      display: flex;
      gap: 25px;
      margin-bottom: 40px;
    }
    
    .input-section {
      flex: 1;
      background: white;
      border-radius: 12px;
      box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
      padding: 25px;
      transition: transform 0.3s ease;
    }
    
    .input-section:hover {
      transform: translateY(-5px);
    }
    
    .results-section {
      flex: 1;
      background: white;
      border-radius: 12px;
      box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
      padding: 25px;
      transition: transform 0.3s ease;
    }
    
    .results-section:hover {
      transform: translateY(-5px);
    }
    
    .section-title {
      font-size: 22px;
      color: #2c3e50;
      margin-bottom: 25px;
      padding-bottom: 15px;
      border-bottom: 2px solid #3498db;
      font-weight: 600;
    }
    
    .form-row {
      margin-bottom: 22px;
    }
    
    .form-label {
      display: block;
      margin-bottom: 8px;
      font-weight: 600;
      color: #2c3e50;
      font-size: 16px;
    }
    
    .input-with-button {
      display: flex;
      gap: 12px;
    }
    
    .input-with-button .el-input {
      flex: 1;
    }
    
    .stage-container {
      background: #f8f9fa;
      border-radius: 8px;
      padding: 18px;
      margin-bottom: 18px;
      border-left: 4px solid #3498db;
    }
    
    .stage-title {
      font-size: 18px;
      color: #2c3e50;
      margin-bottom: 15px;
      font-weight: 600;
    }
    
    .financial-table {
      width: 100%;
      border-collapse: collapse;
      margin: 25px 0;
      box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .financial-table th {
      background: #3498db;
      color: white;
      text-align: left;
      padding: 15px;
      font-weight: 600;
    }
    
    .financial-table td {
      padding: 14px 15px;
      border-bottom: 1px solid #eaeaea;
    }
    
    .financial-table tr:nth-child(even) {
      background-color: #f8fafc;
    }
    
    .financial-table tr:hover {
      background-color: #f1f7fd;
    }
    
    .valuation-result {
      text-align: center;
      padding: 30px;
      background: linear-gradient(135deg, #f8fafc 0%, #e3f2fd 100%);
      border-radius: 10px;
      margin: 25px 0;
      border: 1px solid #e0e7ff;
    }
    
    .result-title {
      font-size: 20px;
      color: #3498db;
      margin-bottom: 15px;
      font-weight: 600;
    }
    
    .result-value {
      font-size: 42px;
      color: #2c3e50;
      font-weight: 700;
      margin: 15px 0;
    }
    
    .result-label {
      font-size: 18px;
      color: #7f8c8d;
    }
    
    .positive {
      color: #27ae60;
    }
    
    .negative {
      color: #e74c3c;
    }
    
    .buttons-container {
      display: flex;
      justify-content: center;
      gap: 15px;
      margin-top: 30px;
    }
    
    .explanation-box {
      background: #e3f2fd;
      border-radius: 8px;
      padding: 20px;
      margin-top: 25px;
      border-left: 4px solid #3498db;
    }
    
    .explanation-title {
      font-size: 18px;
      color: #2c3e50;
      margin-bottom: 12px;
      font-weight: 600;
    }
    
    .explanation-content {
      line-height: 1.7;
      color: #555;
    }
    
    .highlight {
      background: linear-gradient(120deg, #e0f7fa, #bbdefb);
      padding: 2px 6px;
      border-radius: 4px;
      font-weight: 600;
    }
    
    .footer {
      text-align: center;
      padding: 25px;
      color: #7f8c8d;
      font-size: 15px;
      border-top: 1px solid #eaeaea;
      margin-top: 20px;
    }
    
    @media (max-width: 900px) {
      .main-container {
        flex-direction: column;
      }
      
      .input-section, .results-section {
        width: 100%;
      }
    }
  </style>
</head>
<body>
  <div id="app" class="stock-app">
    <div class="app-header">
      <h1 class="app-title">股票估值分析系统</h1>
      <p class="app-subtitle">基于自由现金流折现模型（DCF）的专业股票估值工具，帮助您评估股票内在价值，做出明智投资决策</p>
    </div>
    
    <div class="main-container">
      <!-- 输入参数区域 -->
      <div class="input-section">
        <h2 class="section-title">估值参数设置</h2>
        
        <div class="form-row">
          <label class="form-label">股票代码/公司名称</label>
          <div class="input-with-button">
            <el-input v-model="stockInput" placeholder="输入股票代码(如:600000)或公司名称"></el-input>
            <el-button type="primary" @click="fetchStockData">查询</el-button>
          </div>
        </div>
        
        <div v-if="companyInfo" class="company-info">
          <el-alert title="已查询到公司信息" type="success" :closable="false">
            <p>{{ companyInfo.name }} ({{ companyInfo.code }})</p>
          </el-alert>
        </div>
        
        <div class="form-row">
          <label class="form-label">折现率 (WACC)</label>
          <el-slider 
            v-model="discountRate" 
            :min="0.01" 
            :max="0.2" 
            :step="0.01"
            show-input
            input-size="small"
            :format-tooltip="formatPercent">
          </el-slider>
        </div>
        
        <div class="form-row">
          <label class="form-label">估值阶段选择</label>
          <el-radio-group v-model="stage" size="medium">
            <el-radio-button label="1">单阶段</el-radio-button>
            <el-radio-button label="2">两阶段</el-radio-button>
            <el-radio-button label="3">三阶段</el-radio-button>
          </el-radio-group>
        </div>
        
        <!-- 第一阶段参数 -->
        <div class="stage-container">
          <h3 class="stage-title">第一阶段（高速增长期）</h3>
          <div class="form-row">
            <label class="form-label">增长年限</label>
            <el-input-number 
              v-model="stage1.years" 
              :min="1" 
              :max="20"
              size="medium"
              controls-position="right">
            </el-input-number>
          </div>
          <div class="form-row">
            <label class="form-label">年增长率</label>
            <el-slider 
              v-model="stage1.growth" 
              :min="0.01" 
              :max="0.3" 
              :step="0.01"
              show-input
              input-size="small"
              :format-tooltip="formatPercent">
            </el-slider>
          </div>
        </div>
        
        <!-- 第二阶段参数 -->
        <div class="stage-container" v-if="stage > 1">
          <h3 class="stage-title">第二阶段（过渡期）</h3>
          <div class="form-row">
            <label class="form-label">增长年限</label>
            <el-input-number 
              v-model="stage2.years" 
              :min="1" 
              :max="15"
              size="medium"
              controls-position="right">
            </el-input-number>
          </div>
          <div class="form-row">
            <label class="form-label">年增长率</label>
            <el-slider 
              v-model="stage2.growth" 
              :min="0.01" 
              :max="0.15" 
              :step="0.01"
              show-input
              input-size="small"
              :format-tooltip="formatPercent">
            </el-slider>
          </div>
        </div>
        
        <!-- 第三阶段参数 -->
        <div class="stage-container" v-if="stage > 2">
          <h3 class="stage-title">第三阶段（稳定增长期）</h3>
          <div class="form-row">
            <label class="form-label">增长年限</label>
            <el-input-number 
              v-model="stage3.years" 
              :min="1" 
              :max="10"
              size="medium"
              controls-position="right">
            </el-input-number>
          </div>
          <div class="form-row">
            <label class="form-label">年增长率</label>
            <el-slider 
              v-model="stage3.growth" 
              :min="0.01" 
              :max="0.08" 
              :step="0.01"
              show-input
              input-size="small"
              :format-tooltip="formatPercent">
            </el-slider>
          </div>
        </div>
        
        <div class="buttons-container">
          <el-button type="primary" size="large" @click="calculateValuation">计算估值</el-button>
          <el-button type="info" size="large" @click="resetForm">重置参数</el-button>
        </div>
      </div>
      
      <!-- 结果展示区域 -->
      <div class="results-section">
        <h2 class="section-title">财务数据与估值结果</h2>
        
        <div v-if="financeData.length > 0">
          <h3>近三年财务数据（单位：亿元）</h3>
          <table class="financial-table">
            <thead>
              <tr>
                <th>财务指标</th>
                <th v-for="year in financeYears" :key="year">{{ year }}年</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>净利润</td>
                <td v-for="(data, index) in financeData" :key="index">{{ formatNumber(data.netIncome) }}</td>
              </tr>
              <tr>
                <td>利息费用</td>
                <td v-for="(data, index) in financeData" :key="index">{{ formatNumber(data.interestExpense) }}</td>
              </tr>
              <tr>
                <td>摊销</td>
                <td v-for="(data, index) in financeData" :key="index">{{ formatNumber(data.amortization) }}</td>
              </tr>
              <tr>
                <td>折旧</td>
                <td v-for="(data, index) in financeData" :key="index">{{ formatNumber(data.depreciation) }}</td>
              </tr>
              <tr>
                <td>流动资产</td>
                <td v-for="(data, index) in financeData" :key="index">{{ formatNumber(data.currentAssets) }}</td>
              </tr>
              <tr>
                <td>流动负债</td>
                <td v-for="(data, index) in financeData" :key="index">{{ formatNumber(data.currentLiabilities) }}</td>
              </tr>
              <tr>
                <td>资本支出</td>
                <td v-for="(data, index) in financeData" :key="index">{{ formatNumber(data.capitalExpenditure) }}</td>
              </tr>
              <tr style="font-weight:600; background-color:#e8f4fd;">
                <td>自由现金流(FCF)</td>
                <td v-for="(data, index) in financeData" :key="index">{{ formatNumber(calculateFCF(data)) }}</td>
              </tr>
            </tbody>
          </table>
          
          <div class="average-fcf">
            <el-alert title="平均自由现金流计算" type="info" :closable="false">
              <p>近三年平均自由现金流: <strong>{{ formatNumber(averageFCF) }}</strong> 亿元</p>
            </el-alert>
          </div>
        </div>
        
        <div v-else>
          <el-alert title="暂无财务数据" type="info" description="请先查询股票信息" :closable="false"></el-alert>
        </div>
        
        <div v-if="valuationResult" class="valuation-result">
          <h3 class="result-title">股票估值结果</h3>
          
          <div class="result-value" :class="valuationResult.undervalued ? 'positive' : 'negative'">
            {{ valuationResult.stockPrice }} 元
          </div>
          <p class="result-label">每股估值</p>
          
          <div class="result-comparison">
            <p v-if="valuationResult.undervalued" class="positive">
              <i class="el-icon-success"></i> 当前股价被低估 {{ valuationResult.differencePercent }}%
            </p>
            <p v-else class="negative">
              <i class="el-icon-warning"></i> 当前股价被高估 {{ valuationResult.differencePercent }}%
            </p>
          </div>
          
          <div style="margin-top: 25px;">
            <p>股权总价值: <strong>{{ formatNumber(valuationResult.equityValue) }}</strong> 亿元</p>
            <p>当前实际股价: <strong>{{ currentMarketPrice }}</strong> 元</p>
          </div>
        </div>
        <div v-else>
          <el-alert title="暂无估值结果" type="info" description="请设置参数并点击计算估值按钮" :closable="false"></el-alert>
        </div>
        
        <div class="explanation-box">
          <h4 class="explanation-title">自由现金流折现模型（DCF）说明</h4>
          <p class="explanation-content">
            自由现金流折现模型通过预测企业未来的自由现金流，并使用适当的折现率（通常为加权平均资本成本，WACC）将这些现金流折现到当前时点，从而计算企业的内在价值。计算公式为：
            <span class="highlight">企业价值 = Σ [FCFt / (1 + r)^t]</span>，其中FCFt是第t年的自由现金流，r是折现率。本系统支持<span class="highlight">多阶段增长模型</span>，更准确地反映企业不同发展阶段的增长特点。
          </p>
        </div>
      </div>
    </div>
    
    <div class="footer">
      <p>股票估值分析系统 © 2023 | 基于Vue.js和Element UI开发 | 数据仅供参考，不构成投资建议</p>
    </div>
  </div>

  <script>
    new Vue({
      el: '#app',
      data() {
        return {
          stockInput: '600000',
          companyInfo: null,
          financeData: [],
          discountRate: 0.08,
          stage: '2',
          stage1: { years: 5, growth: 0.12 },
          stage2: { years: 5, growth: 0.07 },
          stage3: { years: 5, growth: 0.03 },
          currentMarketPrice: 7.25,
          valuationResult: null
        }
      },
      computed: {
        financeYears() {
          const currentYear = new Date().getFullYear();
          return [currentYear - 2, currentYear - 1, currentYear];
        },
        averageFCF() {
          if (this.financeData.length === 0) return 0;
          const fcfSum = this.financeData.reduce((sum, data) => {
            return sum + this.calculateFCF(data);
          }, 0);
          return fcfSum / this.financeData.length;
        }
      },
      methods: {
        formatPercent(value) {
          return (value * 100).toFixed(1) + '%';
        },
        
        formatNumber(value) {
          return value.toFixed(2);
        },
        
        calculateFCF(data) {
          // FCF = 净利润 + 利息费用 + 摊销 + 折旧 - 营运资本变动 - 资本支出
          // 简化：营运资本变动 = (流动资产 - 流动负债) * 0.1 (占10%)
          const workingCapitalChange = (data.currentAssets - data.currentLiabilities) * 0.1;
          return data.netIncome + data.interestExpense + data.amortization + 
                 data.depreciation - workingCapitalChange - data.capitalExpenditure;
        },
        
        fetchStockData() {
          // 模拟API请求
          this.$message({
            message: '正在查询股票信息...',
            type: 'info'
          });
          
          setTimeout(() => {
            // 模拟数据
            this.companyInfo = {
              code: this.stockInput,
              name: this.stockInput === '600000' ? '浦发银行' : '示例公司'
            };
            
            // 模拟财务数据
            const baseValues = {
              netIncome: 500 + Math.random() * 100,
              interestExpense: 80 + Math.random() * 20,
              amortization: 30 + Math.random() * 10,
              depreciation: 40 + Math.random() * 15,
              currentAssets: 2000 + Math.random() * 500,
              currentLiabilities: 1800 + Math.random() * 400,
              capitalExpenditure: 60 + Math.random() * 20
            };
            
            this.financeData = [
              { ...baseValues, netIncome: baseValues.netIncome * 0.9 },
              { ...baseValues },
              { ...baseValues, netIncome: baseValues.netIncome * 1.1 }
            ];
            
            this.$message({
              message: '股票数据获取成功',
              type: 'success'
            });
          }, 800);
        },
        
        calculateValuation() {
          if (!this.companyInfo) {
            this.$message.error('请先查询股票信息');
            return;
          }
          
          if (this.financeData.length === 0) {
            this.$message.error('没有可用的财务数据');
            return;
          }
          
          // 模拟估值计算
          const baseValue = this.averageFCF * 100; // 放大倍数模拟估值
          
          // 根据阶段计算估值
          let equityValue = baseValue;
          
          // 第一阶段折现
          equityValue *= (1 + this.stage1.growth) * this.stage1.years;
          
          // 第二阶段折现
          if (this.stage > 1) {
            equityValue *= (1 + this.stage2.growth) * this.stage2.years;
          }
          
          // 第三阶段折现
          if (this.stage > 2) {
            equityValue *= (1 + this.stage3.growth) * this.stage3.years;
          }
          
          // 应用折现率
          equityValue /= (1 + this.discountRate);
          
          // 计算每股价格（简化：总股本按100亿股计算）
          const stockPrice = equityValue / 100;
          
          // 与当前市价比较
          const differencePercent = Math.abs(((stockPrice - this.currentMarketPrice) / this.currentMarketPrice) * 100).toFixed(1);
          const undervalued = stockPrice > this.currentMarketPrice;
          
          this.valuationResult = {
            equityValue,
            stockPrice: stockPrice.toFixed(2),
            differencePercent,
            undervalued
          };
          
          this.$message({
            message: '估值计算完成',
            type: 'success'
          });
        },
        
        resetForm() {
          this.stockInput = '';
          this.companyInfo = null;
          this.financeData = [];
          this.discountRate = 0.08;
          this.stage = '2';
          this.stage1 = { years: 5, growth: 0.12 };
          this.stage2 = { years: 5, growth: 0.07 };
          this.stage3 = { years: 5, growth: 0.03 };
          this.valuationResult = null;
        }
      },
      mounted() {
        // 初始化时加载示例数据
        this.fetchStockData();
      }
    });
  </script>
</body>
</html>