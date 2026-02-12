<template>
  <el-pagination
    v-model:current-page="currentPage"
    v-model:page-size="pageSize"
    :page-sizes="pageSizes"
    :total="total"
    :background="background"
    :layout="layout"
    @size-change="handleSizeChange"
    @current-change="handleCurrentChange"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  total: number
  page?: number
  limit?: number
  pageSizes?: number[]
  layout?: string
  background?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  page: 1,
  limit: 20,
  pageSizes: () => [10, 20, 30, 50],
  layout: 'total, sizes, prev, pager, next, jumper',
  background: true,
})

const emit = defineEmits(['pagination', 'update:page', 'update:limit'])

const currentPage = computed({
  get: () => props.page,
  set: (val) => emit('update:page', val),
})

const pageSize = computed({
  get: () => props.limit,
  set: (val) => emit('update:limit', val),
})

function handleSizeChange(val: number) {
  emit('pagination', { page: currentPage.value, limit: val })
}

function handleCurrentChange(val: number) {
  emit('pagination', { page: val, limit: pageSize.value })
}
</script>

