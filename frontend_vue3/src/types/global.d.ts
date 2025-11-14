/**
 * 全局类型定义
 */

declare global {
  /**
   * 环境变量类型
   */
  interface ImportMetaEnv {
    readonly VITE_APP_PORT: string
    readonly VITE_APP_BASE_API: string
    readonly VITE_API_BASE_URL: string
    readonly VITE_APP_TITLE: string
  }

  interface ImportMeta {
    readonly env: ImportMetaEnv
  }

  /**
   * 分页参数
   */
  interface PageParams {
    page?: number
    page_size?: number
  }

  /**
   * 分页响应
   */
  interface PageResult<T> {
    items: T[]
    total: number
    page: number
    page_size: number
    total_pages: number
  }

  /**
   * API响应
   */
  interface ApiResponse<T = any> {
    code: number
    msg: string
    data: T
    success: boolean
  }

  /**
   * 列表查询参数
   */
  interface ListQueryParams extends PageParams {
    [key: string]: any
  }
}

export {}

