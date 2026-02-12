/**
 * 通用导出功能 Composable
 * 封装CSV/TXT导出、图片导出等通用逻辑
 */
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

export interface ExportOptions {
  exportApi?: (format: string, params: any) => Promise<Blob>
  exportImageApi?: (id: number | string) => Promise<Blob>
  defaultParams?: Record<string, any>
  resourceName?: string
}

export function useExport(options: ExportOptions = {}) {
  const {
    exportApi,
    exportImageApi,
    defaultParams = {},
    resourceName = '数据'
  } = options

  const exportLoading = ref(false)

  /**
   * 下载文件
   */
  function downloadFile(blob: Blob, filename: string) {
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  /**
   * 导出全部数据（CSV/TXT）
   */
  async function handleExport(format: string, additionalParams: Record<string, any> = {}) {
    if (format === 'image') {
      ElMessage.warning(`图片报告仅支持单个${resourceName}导出，请从详情页或操作列导出`)
      return
    }

    exportLoading.value = true
    try {
      const params = { ...defaultParams, ...additionalParams, format }
      
      let response: Blob
      if (exportApi) {
        response = await exportApi(format, params)
      } else {
        // 使用默认的request方法
        const queryString = new URLSearchParams(params).toString()
        response = await request.get(`/api/v1/export?${queryString}`, {
          responseType: 'blob'
        })
      }

      const filename = `${resourceName}_export_${Date.now()}.${format}`
      downloadFile(response, filename)
      ElMessage.success('导出成功')
    } catch (error) {
      console.error('导出失败:', error)
      ElMessage.error('导出失败')
    } finally {
      exportLoading.value = false
    }
  }

  /**
   * 导出选中数据（前端生成CSV/TXT）
   */
  function handleExportSelected<T = any>(
    format: string,
    selectedRows: T[],
    columns: { key: keyof T; label: string }[],
    formatters?: Partial<Record<keyof T, (value: any) => string>>
  ) {
    if (selectedRows.length === 0) {
      ElMessage.warning('请先选择要导出的数据')
      return
    }

    try {
      const separator = format === 'csv' ? ',' : '\t'
      
      // 生成表头
      const headers = columns.map(col => col.label)
      let content = headers.join(separator) + '\n'
      
      // 生成数据行
      selectedRows.forEach(row => {
        const values = columns.map(col => {
          let value = row[col.key]
          
          // 使用自定义格式化器
          if (formatters && formatters[col.key]) {
            value = formatters[col.key]!(value) as any
          }
          
          // 处理特殊字符
          if (typeof value === 'string' && format === 'csv') {
            // CSV中包含逗号或换行符的字段需要用引号包裹
            if (value.includes(',') || value.includes('\n') || value.includes('"')) {
              value = `"${value.replace(/"/g, '""')}"` as any
            }
          }
          
          return value ?? ''
        })
        content += values.join(separator) + '\n'
      })
      
      // 创建Blob并下载
      const blob = new Blob(['\ufeff' + content], { 
        type: format === 'csv' ? 'text/csv;charset=utf-8' : 'text/plain;charset=utf-8' 
      })
      const filename = `${resourceName}_selected_${Date.now()}.${format}`
      downloadFile(blob, filename)
      
      ElMessage.success(`成功导出 ${selectedRows.length} 条记录`)
    } catch (error) {
      console.error('导出失败:', error)
      ElMessage.error('导出失败')
    }
  }

  /**
   * 导出图片
   */
  async function handleExportImage(id: number | string, loadingRef?: any) {
    if (!exportImageApi) {
      ElMessage.error('图片导出功能未配置')
      return
    }

    const loading = loadingRef || { value: false }
    loading.value = true

    try {
      const blob = await exportImageApi(id)
      const filename = `${resourceName}_report_${id}_${Date.now()}.png`
      downloadFile(blob, filename)
      ElMessage.success('图片导出成功')
    } catch (error) {
      console.error('图片导出失败:', error)
      ElMessage.error('图片导出失败')
    } finally {
      loading.value = false
    }
  }

  /**
   * 批量导出图片
   */
  async function handleBatchExportImages(ids: (number | string)[], maxCount = 5) {
    if (ids.length === 0) {
      ElMessage.warning('请选择要导出的数据')
      return
    }

    if (ids.length > maxCount) {
      ElMessage.warning(`一次最多导出 ${maxCount} 个图片报告`)
      return
    }

    exportLoading.value = true
    try {
      for (const id of ids) {
        await handleExportImage(id)
      }
    } finally {
      exportLoading.value = false
    }
  }

  return {
    exportLoading,
    handleExport,
    handleExportSelected,
    handleExportImage,
    handleBatchExportImages,
    downloadFile
  }
}

