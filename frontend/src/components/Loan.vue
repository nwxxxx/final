<!-- 模板部分 -->
<template>
  <!-- 贷款计算器的容器 -->
  <div class="loan-calculator">
    <!-- Element UI 的卡片组件，用于展示表单和表格 -->
    <el-card class="box-card">
      <!-- 表单头部 -->
      <div slot="header" class="clearfix">
        <h2>贷款计算器</h2>
       </div>
      <el-form :model="loanForm" :rules="rules" ref="loanForm" label-width="120px">
        <!-- 贷款金额输入项（添加单位说明） -->
        <el-form-item label="贷款金额" prop="amount">
          <el-input 
            v-model.number="loanForm.amount" 
            placeholder="例如：100000"
            type="number"
            step="1000"
            min="0"
          >
            <template slot="append">元</template>
            <template slot="prefix">¥</template>
          </el-input>
          <div class="unit-hint">请输入贷款总金额（单位：人民币元）</div>
        </el-form-item>

        <!-- 贷款期数输入项（明确单位为月） -->
        <el-form-item label="贷款期数" prop="term">
          <el-input 
            v-model.number="loanForm.term" 
            placeholder="例如：120"
            type="number"
            step="1"
            min="1"
          >
            <template slot="append">个月</template>
          </el-input>
          <div class="unit-hint">请输入还款总月数（如120个月=10年）</div>
        </el-form-item>

        <!-- 年利率输入项（支持小数） -->
        <el-form-item label="年利率" prop="rate">
          <el-input 
            v-model.number="loanForm.rate" 
            placeholder="例如：3.5"
            type="number"
            step="0.1"
            min="0.1"
          >
            <template slot="append">%</template>
          </el-input>
          <div class="unit-hint">请输入年利率百分比（如3.5表示3.5%）</div>
        </el-form-item>

        <el-form-item label="贷款方式" prop="type">
          <el-radio-group v-model="loanForm.type">
            <el-radio label="equal_principal">等额本金</el-radio>
            <el-radio label="equal_installment">等额本息</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="calculate">计算还款计划</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 还款计划表格，用于展示计算结果 -->
      <el-table :data="paymentPlan" v-if="paymentPlan.length > 0" border style="width: 100%; margin-top: 20px;">
        <el-table-column prop="period" label="期数" width="120"></el-table-column>
        <el-table-column prop="payment" label="还款金额" width="180"></el-table-column>
        <el-table-column prop="principal" label="本金" width="180"></el-table-column>
        <el-table-column prop="interest" label="利息" width="180"></el-table-column>
        <el-table-column prop="remaining" label="剩余本金" width="200"></el-table-column>
      </el-table>
    </el-card>
    
  </div>
</template>

<!-- 脚本部分 -->
<script>
export default {
  name: 'Loan', // 组件名称
  data() {
    return {
      loanForm: { // 表单数据模型
        amount: '', // 贷款金额
        term: '', // 贷款期数
        rate: '', // 年利率
        type: 'equal_principal' // 贷款方式，默认为等额本金
      },
      rules: { // 表单验证规则
        amount: [ // 贷款金额的验证规则
          { required: true, message: '请输入贷款金额', trigger: 'blur' },
          { type: 'number', message: '贷款金额必须为数字' }
        ],
        term: [ // 贷款期数的验证规则
          { required: true, message: '请输入贷款期数', trigger: 'blur' },
          { type: 'number', message: '贷款期数必须为数字' }
        ],
        rate: [ // 年利率的验证规则
          { required: true, message: '请输入年利率', trigger: 'blur' },
          { type: 'number', message: '年利率必须为数字' }
        ]
      },
      paymentPlan: [] // 还款计划数组
    }
  },
  methods: { // 组件方法
    calculate() { // 计算还款计划的方法
      this.$refs.loanForm.validate((valid) => { // 验证表单
        if (valid) {
          if (this.loanForm.type === 'equal_principal') {
            this.calculateEqualPrincipal() // 等额本金计算
          } else {
            this.calculateEqualInstallment() // 等额本息计算
          }
        }
      })
    },
    calculateEqualPrincipal() { // 等额本金计算方法
      const amount = this.loanForm.amount
      const term = this.loanForm.term
      const monthlyRate = this.loanForm.rate / 100 / 12
      const principalPerMonth = amount / term
      
      this.paymentPlan = []
      let remaining = amount
      
      for (let i = 1; i <= term; i++) {
        const interest = remaining * monthlyRate
        const payment = principalPerMonth + interest
        remaining -= principalPerMonth
        
        this.paymentPlan.push({
          period: i,
          payment: payment.toFixed(2),
          principal: principalPerMonth.toFixed(2),
          interest: interest.toFixed(2),
          remaining: remaining > 0 ? remaining.toFixed(2) : '0.00'
        })
      }
    },
    calculateEqualInstallment() { // 等额本息计算方法
      const amount = this.loanForm.amount
      const term = this.loanForm.term
      const monthlyRate = this.loanForm.rate / 100 / 12
      const temp = Math.pow(1 + monthlyRate, term)
      const payment = amount * monthlyRate * temp / (temp - 1)
      
      this.paymentPlan = []
      let remaining = amount
      
      for (let i = 1; i <= term; i++) {
        const interest = remaining * monthlyRate
        const principal = payment - interest
        remaining -= principal
        
        this.paymentPlan.push({
          period: i,
          payment: payment.toFixed(2),
          principal: principal.toFixed(2),
          interest: interest.toFixed(2),
          remaining: remaining > 0 ? remaining.toFixed(2) : '0.00'
        })
      }
    },
    resetForm() { // 重置表单方法
      this.$refs.loanForm.resetFields() // 重置表单字段
      this.paymentPlan = [] // 清空还款计划
    }
  }
}
</script>

<!-- 样式部分 -->
<style scoped>
.loan-calculator {
  padding: 20px;
}
.box-card {
  max-width: 900px;
  margin: 0 auto;
}
</style>