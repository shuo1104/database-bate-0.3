/**
 * 填料管理相关API
 */
import { request } from '@/utils/request'

/**
 * 填料信息
 */
export interface FillerInfo {
  FillerID: number
  TradeName: string
  FillerType_FK?: number
  FillerTypeName?: string // For display
  Supplier?: string
  ParticleSize?: string
  IsSilanized?: number // 0 or 1
  CouplingAgent?: string
  SurfaceArea?: number
}

/**
 * 填料类型
 */
export interface FillerType {
  FillerTypeID: number
  FillerTypeName: string
}

/**
 * 填料查询参数
 */
export interface FillerQueryParams extends ListQueryParams {
  TradeName?: string
  FillerType_FK?: number
  Supplier?: string
}

/**
 * 获取填料列表
 */
export function getFillerListApi(params?: FillerQueryParams) {
  return request<PageResult<FillerInfo>>({
    url: '/api/v1/fillers/list',
    method: 'get',
    params,
  })
}

/**
 * 获取填料详情
 */
export function getFillerDetailApi(id: number) {
  return request<FillerInfo>({
    url: `/api/v1/fillers/${id}`,
    method: 'get',
  })
}

/**
 * 创建填料
 */
export function createFillerApi(data: Partial<FillerInfo>) {
  return request<FillerInfo>({
    url: '/api/v1/fillers/create',
    method: 'post',
    data,
  })
}

/**
 * 更新填料
 */
export function updateFillerApi(id: number, data: Partial<FillerInfo>) {
  return request<FillerInfo>({
    url: `/api/v1/fillers/${id}`,
    method: 'put',
    data,
  })
}

/**
 * 删除填料
 */
export function deleteFillerApi(id: number) {
  return request({
    url: `/api/v1/fillers/${id}`,
    method: 'delete',
  })
}

/**
 * 获取填料类型列表
 */
export function getFillerTypesApi() {
  return request<FillerType[]>({
    url: '/api/v1/fillers/config/types',
    method: 'get',
  })
}

/**
 * 批量删除填料
 */
export function batchDeleteFillersApi(ids: number[]) {
  return request({
    url: '/api/v1/fillers/batch-delete',
    method: 'delete',
    data: { ids },
  })
}

