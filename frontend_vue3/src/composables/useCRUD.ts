/**
 * 通用 CRUD 操作 Composable
 * 封装创建、更新、删除等通用逻辑
 */
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { showErrorMessage, handleBusinessError } from '@/utils/errorHandler'

export interface CRUDOptions<T = any> {
  createApi: (data: any) => Promise<any>
  updateApi: (id: number | string, data: any) => Promise<any>
  deleteApi: (id: number | string) => Promise<any>
  batchDeleteApi?: (ids: (number | string)[]) => Promise<any>
  resourceName?: string
  idKey?: string
  onSuccess?: () => void
  onError?: (error: any) => void
  transformRequestData?: (formData: Partial<T>) => any
  transformResponseData?: (data: any) => Partial<T>
  defaultFormData?: Partial<T>
  silentError?: boolean  // 是否静默错误（不显示消息）
}

export function useCRUD<T extends Record<string, any>>(
  options: CRUDOptions<T>
) {
  const {
    createApi,
    updateApi,
    deleteApi,
    batchDeleteApi,
    resourceName = 'Record',
    idKey = 'id',
    onSuccess,
    onError,
    transformRequestData,
    transformResponseData,
    defaultFormData,
    silentError = false
  } = options

  // 状态
  const dialogVisible = ref(false)
  const dialogTitle = ref(`Create ${resourceName}`)
  const submitLoading = ref(false)
  const formRef = ref<FormInstance>()
  
  // 表单数据
  const formData = reactive<Partial<T>>({})
  const isEditMode = ref(false)

  /**
   * 打开创建对话框
   */
  function handleAdd(initialData?: Partial<T>) {
    isEditMode.value = false
    dialogTitle.value = `Create ${resourceName}`
    // 使用 defaultFormData 或 initialData 初始化表单
    const dataToAssign = initialData || defaultFormData || {}
    Object.assign(formData, dataToAssign)
    dialogVisible.value = true
  }

  /**
   * 打开编辑对话框
   */
  function handleEdit(row: T) {
    isEditMode.value = true
    dialogTitle.value = `Edit ${resourceName}`
    
    // 使用转换函数或直接复制
    const dataToAssign = transformResponseData ? transformResponseData(row) : row
    Object.assign(formData, dataToAssign)
    dialogVisible.value = true
  }

  /**
   * 提交表单
   */
  async function handleSubmit(formRules?: any) {
    if (!formRef.value) return
    
    try {
      const valid = await formRef.value.validate()
      
      if (valid) {
        submitLoading.value = true
        try {
          // 转换请求数据
          const requestData = transformRequestData 
            ? transformRequestData(formData)
            : formData

          // 使用 idKey 获取 ID
          const recordId = formData[idKey as keyof T]
          if (isEditMode.value && recordId) {
            await updateApi(recordId as any, requestData)
            ElMessage.success(`${resourceName} updated successfully`)
          } else {
            await createApi(requestData)
            ElMessage.success(`${resourceName} created successfully`)
          }
          
          dialogVisible.value = false
          onSuccess?.()
        } catch (error: any) {
          // 错误已经在 request.ts 中处理，这里不再重复显示
          // 只调用错误回调
          if (!silentError) {
            const action = isEditMode.value ? 'update' : 'create'
            // 只在 request.ts 没有处理时才显示
            if (error.message && !error.response) {
              showErrorMessage(`Failed to ${action} ${resourceName.toLowerCase()}`)
            }
          }
          onError?.(error)
        } finally {
          submitLoading.value = false
        }
      }
    } catch (error: any) {
      // 表单验证失败
      showErrorMessage('Please check form input', { type: 'warning' })
    }
  }

  /**
   * 删除单条记录
   */
  async function handleDelete(row: T, idField: keyof T = 'id' as keyof T) {
    try {
      await ElMessageBox.confirm(
        `Are you sure you want to delete this ${resourceName.toLowerCase()}?`,
        'Delete Confirmation',
        {
          confirmButtonText: 'Confirm',
          cancelButtonText: 'Cancel',
          type: 'warning',
        }
      )

      const id = row[idField]
      await deleteApi(id as any)
      ElMessage.success(`${resourceName} deleted successfully`)
      onSuccess?.()
    } catch (error: any) {
      if (error !== 'cancel') {
        // 错误已经在 request.ts 中处理
        if (!silentError && error.message && !error.response) {
          showErrorMessage(`Failed to delete ${resourceName.toLowerCase()}`)
        }
        onError?.(error)
      }
    }
  }

  /**
   * 批量删除
   */
  async function handleBatchDelete(
    selectedRows: T[], 
    idField: keyof T = 'id' as keyof T
  ) {
    if (selectedRows.length === 0) {
      ElMessage.warning('Please select items to delete')
      return
    }

    if (!batchDeleteApi) {
      ElMessage.error('Batch delete function is not configured')
      return
    }

    try {
      await ElMessageBox.confirm(
        `Are you sure you want to delete the selected ${selectedRows.length} ${resourceName.toLowerCase()}(s)?`,
        'Batch Delete Confirmation',
        {
          confirmButtonText: 'Confirm',
          cancelButtonText: 'Cancel',
          type: 'warning',
        }
      )

      const ids = selectedRows.map(row => row[idField] as any)
      await batchDeleteApi(ids)
      ElMessage.success(`Successfully deleted ${selectedRows.length} record(s)`)
      onSuccess?.()
    } catch (error: any) {
      if (error !== 'cancel') {
        // 错误已经在 request.ts 中处理
        if (!silentError && error.message && !error.response) {
          showErrorMessage('Failed to delete selected items')
        }
        onError?.(error)
      }
    }
  }

  /**
   * 关闭对话框
   */
  function handleDialogClose() {
    formRef.value?.resetFields()
    formRef.value?.clearValidate()
    // 清空表单数据，并重新初始化为 defaultFormData
    Object.keys(formData).forEach(key => {
      delete formData[key]
    })
    if (defaultFormData) {
      Object.assign(formData, defaultFormData)
    }
  }

  /**
   * 重置表单
   */
  function resetForm() {
    formRef.value?.resetFields()
  }

  return {
    // 状态
    dialogVisible,
    dialogTitle,
    submitLoading,
    formRef,
    formData,
    isEditMode,
    
    // 方法
    handleAdd,
    handleEdit,
    handleSubmit,
    handleDelete,
    handleBatchDelete,
    handleDialogClose,
    resetForm
  }
}

