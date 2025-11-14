/**
 * 项目管理相关API
 */
import { request } from '@/utils/request'

/**
 * 项目信息
 */
export interface ProjectInfo {
  ProjectID: number
  ProjectName: string
  ProjectType_FK?: number
  TypeName?: string
  SubstrateApplication?: string
  FormulatorName?: string
  FormulationDate?: string
  FormulaCode?: string
  CreatedAt?: string
  UpdatedAt?: string
  // 兼容旧字段
  TargetDensity?: number
  TargetViscosity?: number
  ProjectType?: string
  ProjectCode?: string
  StartDate?: string
  EndDate?: string
  ProjectLeader?: string
  Department?: string
  Status?: string
  Remark?: string
}

/**
 * 配方成分
 */
export interface FormulaComposition {
  CompositionID: number
  ProjectID: number
  MaterialID_FK?: number
  FillerID_FK?: number
  WeightPercent: number
  AdditionMethod?: string
  Remark?: string
  CreatedAt?: string
  UpdatedAt?: string
  // 关联信息
  material_name?: string
  filler_name?: string
}

/**
 * 项目查询参数
 */
export interface ProjectQueryParams extends ListQueryParams {
  ProjectName?: string
  ProjectType?: string
  Status?: string
  ProjectLeader?: string
}

/**
 * 配方成分查询参数
 */
export interface CompositionQueryParams extends ListQueryParams {
  ProjectID?: number
}

/**
 * 获取项目列表
 */
export function getProjectListApi(params?: ProjectQueryParams) {
  return request<PageResult<ProjectInfo>>({
    url: '/api/v1/projects/list',
    method: 'get',
    params,
  })
}

/**
 * 获取项目详情
 */
export function getProjectDetailApi(id: number) {
  return request<ProjectInfo>({
    url: `/api/v1/projects/${id}`,
    method: 'get',
  })
}

/**
 * 创建项目
 */
export function createProjectApi(data: Partial<ProjectInfo>) {
  return request<ProjectInfo>({
    url: '/api/v1/projects/create',
    method: 'post',
    data,
  })
}

/**
 * 更新项目
 */
export function updateProjectApi(id: number, data: Partial<ProjectInfo>) {
  return request<ProjectInfo>({
    url: `/api/v1/projects/${id}`,
    method: 'put',
    data,
  })
}

/**
 * 删除项目
 */
export function deleteProjectApi(id: number) {
  return request({
    url: `/api/v1/projects/${id}`,
    method: 'delete',
  })
}

/**
 * 获取项目的配方成分列表
 */
export function getCompositionListApi(projectId: number) {
  return request<FormulaComposition[]>({
    url: `/api/v1/projects/${projectId}/compositions`,
    method: 'get',
  })
}

/**
 * 创建配方成分
 */
export function createCompositionApi(data: any) {
  return request<FormulaComposition>({
    url: '/api/v1/projects/compositions/create',
    method: 'post',
    data,
  })
}

/**
 * 更新配方成分
 */
export function updateCompositionApi(id: number, data: Partial<FormulaComposition>) {
  return request<FormulaComposition>({
    url: `/api/v1/projects/compositions/${id}`,
    method: 'put',
    data,
  })
}

/**
 * 删除配方成分
 */
export function deleteCompositionApi(compositionId: number) {
  return request({
    url: `/api/v1/projects/compositions/${compositionId}`,
    method: 'delete',
  })
}

/**
 * 批量删除配方成分
 */
export function batchDeleteCompositionsApi(ids: number[]) {
  return request({
    url: '/api/v1/projects/compositions/batch-delete',
    method: 'delete',
    data: { composition_ids: ids },
  })
}

/**
 * 获取项目类型列表
 */
export function getProjectTypesApi() {
  return request({
    url: '/api/v1/projects/config/types',
    method: 'get',
  })
}

/**
 * 获取配方设计师列表
 */
export function getFormulatorsApi() {
  return request({
    url: '/api/v1/projects/config/formulators',
    method: 'get',
  })
}

/**
 * 导出项目图片报告
 */
export function exportProjectImageApi(projectId: number) {
  return request({
    url: `/api/v1/projects/export-image/${projectId}`,
    method: 'get',
    responseType: 'blob',
  })
}

