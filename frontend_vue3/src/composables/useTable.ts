/**
 * 通用表格数据处理 Composable
 * 封装分页、加载状态、查询、重置等通用逻辑
 */
import { ref, reactive, computed } from 'vue'
import { showErrorMessage } from '@/utils/errorHandler'

export interface TableQueryParams {
  page: number
  page_size: number
  [key: string]: any
}

export interface TableOptions<T = any> {
  defaultPageSize?: number
  onSuccess?: (data: T[]) => void
  onError?: (error: any) => void
}

export function useTable<T = any>(
  fetchApi: (params: any) => Promise<{ list?: T[]; items?: T[]; total: number }>,
  options: TableOptions<T> = {}
) {
  const {
    defaultPageSize = 20,
    onSuccess,
    onError
  } = options

  // 状态
  const loading = ref(false)
  const tableData = ref<T[]>([])
  const total = ref(0)
  const selectedRows = ref<T[]>([])

  // 查询参数
  const queryParams = reactive<TableQueryParams>({
    page: 1,
    page_size: defaultPageSize
  })

  // 计算属性
  const hasSelection = computed(() => selectedRows.value.length > 0)
  const isEmpty = computed(() => tableData.value.length === 0)

  /**
   * 获取列表数据
   */
  async function fetchData() {
    loading.value = true
    try {
      const res = await fetchApi(queryParams)
      tableData.value = (res.list || res.items || []) as T[]
      total.value = res.total || 0
      
      onSuccess?.(tableData.value as T[])
    } catch (error: any) {
      // 错误已经在 request.ts 中处理，这里不再重复显示
      // 只在没有 response 时才显示（避免重复）
      if (error.message && !error.response) {
        showErrorMessage('Failed to fetch data')
      }
      onError?.(error)
    } finally {
      loading.value = false
    }
  }

  /**
   * 查询（重置到第一页）
   */
  function handleQuery() {
    queryParams.page = 1
    fetchData()
  }

  /**
   * 重置查询条件
   */
  function handleReset(keysToReset?: string[]) {
    queryParams.page = 1
    
    if (keysToReset) {
      // 只重置指定的字段
      keysToReset.forEach(key => {
        if (key in queryParams) {
          queryParams[key] = ''
        }
      })
    } else {
      // 重置除了 page 和 page_size 之外的所有字段
      Object.keys(queryParams).forEach(key => {
        if (key !== 'page' && key !== 'page_size') {
          queryParams[key] = ''
        }
      })
    }
    
    fetchData()
  }

  /**
   * 分页变化
   */
  function handlePageChange(page: number) {
    queryParams.page = page
    fetchData()
  }

  /**
   * 每页数量变化
   */
  function handleSizeChange(size: number) {
    queryParams.page = 1
    queryParams.page_size = size
    fetchData()
  }

  /**
   * 选择变化
   */
  function handleSelectionChange(selection: T[]) {
    selectedRows.value = selection
  }

  /**
   * 刷新当前页
   */
  function refresh() {
    fetchData()
  }

  /**
   * 重置选择
   */
  function clearSelection() {
    selectedRows.value = []
  }

  return {
    // 状态
    loading,
    tableData,
    total,
    selectedRows,
    queryParams,
    
    // 计算属性
    hasSelection,
    isEmpty,
    
    // 方法
    fetchData,
    handleQuery,
    handleReset,
    handlePageChange,
    handleSizeChange,
    handleSelectionChange,
    refresh,
    clearSelection
  }
}

