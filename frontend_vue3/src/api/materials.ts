/**
 * 原料管理相关API
 */
import request from '@/utils/request'

/**
 * 原料信息
 */
export interface MaterialInfo {
  MaterialID: number
  MaterialName: string
  EnglishName?: string
  CAS?: string
  Supplier?: string
  Specification?: string
  Unit?: string
  Density?: number
  Viscosity?: number
  Category?: string
  Remark?: string
  CreatedAt?: string
  UpdatedAt?: string
}

/**
 * 原料查询参数
 */
export interface MaterialQueryParams extends ListQueryParams {
  MaterialName?: string
  Category?: string
  Supplier?: string
  CAS?: string
}

/**
 * 获取原料列表
 */
export function getMaterialListApi(params?: MaterialQueryParams) {
  return request<PageResult<MaterialInfo>>({
    url: '/api/v1/materials/list',
    method: 'get',
    params,
  })
}

/**
 * 获取原料详情
 */
export function getMaterialDetailApi(id: number) {
  return request<MaterialInfo>({
    url: `/api/v1/materials/${id}`,
    method: 'get',
  })
}

/**
 * 创建原料
 */
export function createMaterialApi(data: Partial<MaterialInfo>) {
  return request<MaterialInfo>({
    url: '/api/v1/materials/create',
    method: 'post',
    data,
  })
}

/**
 * 更新原料
 */
export function updateMaterialApi(id: number, data: Partial<MaterialInfo>) {
  return request<MaterialInfo>({
    url: `/api/v1/materials/${id}`,
    method: 'put',
    data,
  })
}

/**
 * 删除原料
 */
export function deleteMaterialApi(id: number) {
  return request({
    url: `/api/v1/materials/${id}`,
    method: 'delete',
  })
}

/**
 * 批量删除原料
 */
export function batchDeleteMaterialsApi(ids: number[]) {
  return request({
    url: '/api/v1/materials/batch-delete',
    method: 'delete',
    data: { material_ids: ids },
  })
}

/**
 * 获取原料类别列表
 */
export function getMaterialCategoriesApi() {
  return request<string[]>({
    url: '/api/v1/materials/categories',
    method: 'get',
  })
}

/**
 * 获取供应商列表
 */
export function getMaterialSuppliersApi() {
  return request<string[]>({
    url: '/api/v1/materials/suppliers',
    method: 'get',
  })
}

