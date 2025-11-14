<template>
  <el-dropdown @command="handleCommand" :disabled="disabled" :loading="loading">
    <el-button :type="type" :icon="icon" :loading="loading">
      {{ label }}
      <el-icon class="el-icon--right">
        <arrow-down />
      </el-icon>
    </el-button>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item 
          v-for="option in exportOptions" 
          :key="option.value"
          :command="option.value"
          :disabled="option.disabled"
        >
          <el-icon v-if="option.icon"><component :is="option.icon" /></el-icon>
          {{ option.label }}
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { ArrowDown, Document, Picture } from '@element-plus/icons-vue'
import type { Component } from 'vue'

export interface ExportOption {
  label: string
  value: string
  icon?: Component
  disabled?: boolean
}

interface Props {
  label?: string
  type?: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'default'
  icon?: Component
  loading?: boolean
  disabled?: boolean
  options?: ExportOption[]
  showImage?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  label: 'Export',
  type: 'default',
  loading: false,
  disabled: false,
  showImage: true,
  options: () => []
})

const emit = defineEmits<{
  export: [format: string]
}>()

// 默认导出选项
const defaultOptions: ExportOption[] = [
  { label: 'Export as CSV', value: 'csv', icon: Document },
  { label: 'Export as TXT', value: 'txt', icon: Document },
]

// 如果显示图片选项
if (props.showImage) {
  defaultOptions.push({ label: 'Export as Image', value: 'image', icon: Picture })
}

// 合并用户自定义选项
const exportOptions = props.options.length > 0 ? props.options : defaultOptions

function handleCommand(command: string) {
  emit('export', command)
}
</script>

<style scoped lang="scss">
.el-dropdown {
  vertical-align: middle;
}
</style>

