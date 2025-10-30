<template>
  <el-form :inline="inline" :model="modelValue" class="search-bar">
    <el-form-item
      v-for="field in fields"
      :key="field.prop"
      :label="field.label"
      :label-width="field.labelWidth"
    >
      <!-- 输入框 -->
      <el-input
        v-if="field.type === 'input' || !field.type"
        v-model="modelValue[field.prop]"
        :placeholder="field.placeholder || `请输入${field.label}`"
        :clearable="field.clearable !== false"
        :disabled="field.disabled"
        @keyup.enter="handleQuery"
      />

      <!-- 下拉选择 -->
      <el-select
        v-else-if="field.type === 'select'"
        v-model="modelValue[field.prop]"
        :placeholder="field.placeholder || `请选择${field.label}`"
        :clearable="field.clearable !== false"
        :disabled="field.disabled"
        :filterable="field.filterable"
        :multiple="field.multiple"
        :style="{ width: field.width || '200px' }"
      >
        <el-option
          v-for="option in field.options"
          :key="option.value"
          :label="option.label"
          :value="option.value"
          :disabled="option.disabled"
        />
      </el-select>

      <!-- 日期选择 -->
      <el-date-picker
        v-else-if="field.type === 'date'"
        v-model="modelValue[field.prop]"
        :type="field.dateType || 'date'"
        :placeholder="field.placeholder || `请选择${field.label}`"
        :clearable="field.clearable !== false"
        :disabled="field.disabled"
        :value-format="field.valueFormat || 'YYYY-MM-DD'"
        :style="{ width: field.width || '200px' }"
      />

      <!-- 日期范围 -->
      <el-date-picker
        v-else-if="field.type === 'daterange'"
        v-model="modelValue[field.prop]"
        type="daterange"
        :start-placeholder="field.startPlaceholder || '开始日期'"
        :end-placeholder="field.endPlaceholder || '结束日期'"
        :clearable="field.clearable !== false"
        :disabled="field.disabled"
        :value-format="field.valueFormat || 'YYYY-MM-DD'"
        :style="{ width: field.width || '240px' }"
      />

      <!-- 数字输入 -->
      <el-input-number
        v-else-if="field.type === 'number'"
        v-model="modelValue[field.prop]"
        :placeholder="field.placeholder"
        :min="field.min"
        :max="field.max"
        :step="field.step"
        :disabled="field.disabled"
        :controls-position="field.controlsPosition || 'right'"
      />

      <!-- 级联选择 -->
      <el-cascader
        v-else-if="field.type === 'cascader'"
        v-model="modelValue[field.prop]"
        :options="field.options"
        :placeholder="field.placeholder || `请选择${field.label}`"
        :clearable="field.clearable !== false"
        :disabled="field.disabled"
        :props="field.cascaderProps"
        :style="{ width: field.width || '200px' }"
      />
    </el-form-item>

    <!-- 操作按钮 -->
    <el-form-item v-if="showActions">
      <el-button
        type="primary"
        :icon="Search"
        :loading="loading"
        @click="handleQuery"
      >
        {{ queryText }}
      </el-button>
      <el-button
        :icon="Refresh"
        @click="handleReset"
      >
        {{ resetText }}
      </el-button>
      <slot name="actions" />
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { Search, Refresh } from '@element-plus/icons-vue'

export interface SearchField {
  prop: string
  label: string
  type?: 'input' | 'select' | 'date' | 'daterange' | 'number' | 'cascader'
  placeholder?: string
  labelWidth?: string
  clearable?: boolean
  disabled?: boolean
  filterable?: boolean
  multiple?: boolean
  width?: string
  // Select options
  options?: Array<{ label: string; value: any; disabled?: boolean }>
  // Date picker
  dateType?: 'date' | 'datetime' | 'year' | 'month' | 'week'
  valueFormat?: string
  startPlaceholder?: string
  endPlaceholder?: string
  // Number input
  min?: number
  max?: number
  step?: number
  controlsPosition?: 'right' | ''
  // Cascader
  cascaderProps?: any
}

interface Props {
  modelValue: Record<string, any>
  fields: SearchField[]
  inline?: boolean
  showActions?: boolean
  queryText?: string
  resetText?: string
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  inline: true,
  showActions: true,
  queryText: '查询',
  resetText: '重置',
  loading: false
})

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, any>]
  query: []
  reset: []
}>()

function handleQuery() {
  emit('query')
}

function handleReset() {
  emit('reset')
}
</script>

<style scoped lang="scss">
.search-bar {
  :deep(.el-form-item) {
    margin-bottom: 16px;
  }
}
</style>

