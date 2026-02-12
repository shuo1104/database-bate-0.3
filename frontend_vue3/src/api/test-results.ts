import { request } from '@/utils/request'

// ==================== 测试结果接口类型定义 ====================

export interface TestResultInk {
  ResultID?: number
  ProjectID_FK: number
  Ink_Viscosity?: string
  Ink_Reactivity?: string
  Ink_ParticleSize?: string
  Ink_SurfaceTension?: string
  Ink_ColorValue?: string
  Ink_RheologyNote?: string
  TestDate?: string
  Notes?: string
}

export interface TestResultCoating {
  ResultID?: number
  ProjectID_FK: number
  Coating_Adhesion?: string
  Coating_Transparency?: string
  Coating_SurfaceHardness?: string
  Coating_ChemicalResistance?: string
  Coating_CostEstimate?: string
  TestDate?: string
  Notes?: string
}

export interface TestResult3DPrint {
  ResultID?: number
  ProjectID_FK: number
  Print3D_Shrinkage?: string
  Print3D_YoungsModulus?: string
  Print3D_FlexuralStrength?: string
  Print3D_ShoreHardness?: string
  Print3D_ImpactResistance?: string
  TestDate?: string
  Notes?: string
}

export interface TestResultComposite {
  ResultID?: number
  ProjectID_FK: number
  Composite_FlexuralStrength?: string
  Composite_YoungsModulus?: string
  Composite_ImpactResistance?: string
  Composite_ConversionRate?: string
  Composite_WaterAbsorption?: string
  TestDate?: string
  Notes?: string
}

export type TestResult = TestResultInk | TestResultCoating | TestResult3DPrint | TestResultComposite

// ==================== API 函数 ====================

/**
 * 获取项目测试结果
 * @param projectId 项目ID
 */
export function getTestResultApi(projectId: number) {
  return request<TestResult>({
    url: `/api/v1/test-results/project/${projectId}`,
    method: 'get',
  })
}

/**
 * 创建或更新喷墨测试结果
 * @param projectId 项目ID
 * @param data 测试数据
 */
export function saveInkResultApi(projectId: number, data: Partial<TestResultInk>) {
  return request<TestResultInk>({
    url: `/api/v1/test-results/ink/${projectId}`,
    method: 'post',
    data,
  })
}

/**
 * 创建或更新涂层测试结果
 * @param projectId 项目ID
 * @param data 测试数据
 */
export function saveCoatingResultApi(projectId: number, data: Partial<TestResultCoating>) {
  return request<TestResultCoating>({
    url: `/api/v1/test-results/coating/${projectId}`,
    method: 'post',
    data,
  })
}

/**
 * 创建或更新3D打印测试结果
 * @param projectId 项目ID
 * @param data 测试数据
 */
export function save3DPrintResultApi(projectId: number, data: Partial<TestResult3DPrint>) {
  return request<TestResult3DPrint>({
    url: `/api/v1/test-results/3dprint/${projectId}`,
    method: 'post',
    data,
  })
}

/**
 * 创建或更新复合材料测试结果
 * @param projectId 项目ID
 * @param data 测试数据
 */
export function saveCompositeResultApi(projectId: number, data: Partial<TestResultComposite>) {
  return request<TestResultComposite>({
    url: `/api/v1/test-results/composite/${projectId}`,
    method: 'post',
    data,
  })
}

