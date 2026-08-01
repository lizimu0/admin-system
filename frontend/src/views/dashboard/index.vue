<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'
import * as echarts from 'echarts'
import { Goods, TrendCharts, User, UserFilled } from '@element-plus/icons-vue'
import { getCategories, getGrowth, getSummary } from '../../api/dashboard'

const summary = ref({ user_count: 0, role_count: 0, product_count: 0, product_on_count: 0 })
let lineChart = null
let pieChart = null

const statCards = [
  { key: 'user_count', label: '用户总数', icon: User, color: '#409eff' },
  { key: 'role_count', label: '角色数量', icon: UserFilled, color: '#67c23a' },
  { key: 'product_count', label: '商品总数', icon: Goods, color: '#e6a23c' },
  { key: 'product_on_count', label: '在售商品', icon: TrendCharts, color: '#f56c6c' }
]

async function loadSummary() {
  summary.value = await getSummary()
}

async function loadGrowth() {
  const data = await getGrowth()
  lineChart?.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, top: 30, bottom: 30 },
    xAxis: { type: 'category', data: data.map((d) => d.date) },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      {
        name: '新增用户',
        type: 'line',
        smooth: true,
        data: data.map((d) => d.count),
        areaStyle: { opacity: 0.15 },
        itemStyle: { color: '#409eff' }
      }
    ]
  })
}

async function loadCategories() {
  const data = await getCategories()
  pieChart?.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [
      {
        name: '商品分类',
        type: 'pie',
        radius: ['40%', '65%'],
        avoidLabelOverlap: true,
        itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
        data
      }
    ]
  })
}

onMounted(() => {
  lineChart = echarts.init(document.getElementById('lineChart'))
  pieChart = echarts.init(document.getElementById('pieChart'))
  loadSummary()
  loadGrowth()
  loadCategories()
})

onBeforeUnmount(() => {
  lineChart?.dispose()
  pieChart?.dispose()
})
</script>

<template>
  <div>
    <el-row :gutter="16">
      <el-col v-for="card in statCards" :key="card.key" :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-inner">
            <div class="stat-icon" :style="{ background: card.color }">
              <el-icon :size="24" color="#fff"><component :is="card.icon" /></el-icon>
            </div>
            <div>
              <div class="stat-value">{{ summary[card.key] }}</div>
              <div class="stat-label">{{ card.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="chart-row">
      <el-col :span="14">
        <el-card shadow="never" header="近 7 日新增用户">
          <div id="lineChart" class="chart" />
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="never" header="商品分类分布">
          <div id="pieChart" class="chart" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.stat-card {
  margin-bottom: 16px;
}
.stat-inner {
  display: flex;
  align-items: center;
  gap: 16px;
}
.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: #333;
  line-height: 1.2;
}
.stat-label {
  color: #999;
  font-size: 13px;
}
.chart-row {
  margin-top: 4px;
}
.chart {
  height: 320px;
}
</style>
