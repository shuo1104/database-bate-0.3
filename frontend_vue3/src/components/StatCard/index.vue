<template>
  <div class="stat-card" :class="`stat-${type}`">
    <div class="stat-icon">
      <el-icon :size="32">
        <component :is="icon" />
      </el-icon>
    </div>
    <div class="stat-content">
      <div class="stat-label">{{ label }}</div>
      <div class="stat-value">{{ value }}</div>
      <div v-if="trend" class="stat-trend" :class="trendClass">
        <el-icon :size="14">
          <component :is="trendIcon" />
        </el-icon>
        {{ trend }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, Component } from 'vue'
import { ArrowUp, ArrowDown } from '@element-plus/icons-vue'

interface Props {
  label: string
  value: string | number
  icon: Component
  type?: 'primary' | 'success' | 'warning' | 'danger'
  trend?: string
  trendUp?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'primary',
  trendUp: true
})

const trendClass = computed(() => {
  return props.trendUp ? 'trend-up' : 'trend-down'
})

const trendIcon = computed(() => {
  return props.trendUp ? ArrowUp : ArrowDown
})
</script>

<style scoped lang="scss">
.stat-card {
  display: flex;
  gap: 20px;
  padding: 24px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fbfd 100%);
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(15, 33, 53, 0.08);
  transition: all 0.3s;
  border-left: 4px solid;

  &:hover {
    box-shadow: 0 14px 28px rgba(15, 33, 53, 0.14);
    transform: translateY(-2px);
  }

  &.stat-primary {
    border-color: #0f82c5;

    .stat-icon {
      background: linear-gradient(135deg, #0f82c5 0%, #17a890 100%);
    }
  }

  &.stat-success {
    border-color: #67c23a;

    .stat-icon {
      background: linear-gradient(135deg, #1f9a5a 0%, #6ccf66 100%);
    }
  }

  &.stat-warning {
    border-color: #e6a23c;

    .stat-icon {
      background: linear-gradient(135deg, #da8d22 0%, #f2bf53 100%);
    }
  }

  &.stat-danger {
    border-color: #f56c6c;

    .stat-icon {
      background: linear-gradient(135deg, #d55353 0%, #ef8d5d 100%);
    }
  }

  .stat-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 64px;
    height: 64px;
    border-radius: 12px;
    color: #fff;
  }

  .stat-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;

    .stat-label {
      font-size: 14px;
      color: #909399;
      margin-bottom: 8px;
    }

    .stat-value {
      font-size: 28px;
      font-weight: bold;
      color: #303133;
      margin-bottom: 4px;
    }

    .stat-trend {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 12px;

      &.trend-up {
        color: #67c23a;
      }

      &.trend-down {
        color: #f56c6c;
      }
    }
  }
}
</style>

