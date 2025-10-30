/**
 * Form Validation Rules
 * 统一的表单验证规则 - 匹配数据库字段约束
 */
import type { FormItemRule } from 'element-plus'

// ==================== 数据库字段长度约束 ====================
export const DB_CONSTRAINTS = {
  // User fields
  username: { min: 3, max: 50 },
  password: { min: 6, max: 100 },
  realName: { min: 2, max: 100 },
  position: { min: 2, max: 100 },
  email: { max: 255 },
  
  // Project fields
  projectName: { min: 2, max: 255 },
  formulatorName: { min: 2, max: 255 },
  formulaCode: { max: 255 },
  
  // Material fields
  tradeName: { min: 2, max: 255 },
  supplier: { max: 255 },
  casNumber: { max: 255 },
  particleSize: { max: 255 },
  couplingAgent: { max: 255 },
  
  // Numeric fields
  weightPercentage: { min: 0, max: 100 },
  density: { min: 0, max: 99999.9999 },
  viscosity: { min: 0, max: 99999.9999 },
  surfaceArea: { min: 0, max: 999999.9999 },
} as const

// ==================== 正则表达式 ====================
export const REGEX_PATTERNS = {
  // 邮箱
  email: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
  
  // 用户名（字母、数字、下划线、中划线）
  username: /^[a-zA-Z0-9_-]+$/,
  
  // 密码（至少包含字母和数字）
  password: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]/,
  
  // 手机号（中国）
  phone: /^1[3-9]\d{9}$/,
  
  // 数字（支持小数）
  number: /^-?\d+(\.\d+)?$/,
  
  // 正整数
  positiveInteger: /^[1-9]\d*$/,
  
  // 非负整数
  nonNegativeInteger: /^(0|[1-9]\d*)$/,
  
  // URL
  url: /^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&/=]*)$/,
  
  // CAS号（化学文摘登记号）
  casNumber: /^\d{2,7}-\d{2}-\d$/,
} as const

// ==================== 自定义验证器 ====================

/**
 * 创建必填验证器
 */
export const createRequiredValidator = (
  fieldName: string,
  trigger: 'blur' | 'change' = 'blur'
): FormItemRule => ({
  required: true,
  message: `Please enter ${fieldName}`,
  trigger,
})

/**
 * 创建长度验证器
 */
export const createLengthValidator = (
  fieldName: string,
  min?: number,
  max?: number,
  trigger: 'blur' | 'change' = 'blur'
): FormItemRule => {
  if (min !== undefined && max !== undefined) {
    return {
      min,
      max,
      message: `${fieldName} should be between ${min} and ${max} characters`,
      trigger,
    }
  } else if (min !== undefined) {
    return {
      min,
      message: `${fieldName} should be at least ${min} characters`,
      trigger,
    }
  } else if (max !== undefined) {
    return {
      max,
      message: `${fieldName} should not exceed ${max} characters`,
      trigger,
    }
  }
  return {} as FormItemRule
}

/**
 * 创建正则验证器
 */
export const createPatternValidator = (
  pattern: RegExp,
  message: string,
  trigger: 'blur' | 'change' = 'blur'
): FormItemRule => ({
  pattern,
  message,
  trigger,
})

/**
 * 创建数字范围验证器
 */
export const createNumberRangeValidator = (
  fieldName: string,
  min?: number,
  max?: number,
  trigger: 'blur' | 'change' = 'blur'
): FormItemRule => ({
  type: 'number',
  min,
  max,
  message: min !== undefined && max !== undefined
    ? `${fieldName} should be between ${min} and ${max}`
    : min !== undefined
    ? `${fieldName} should be at least ${min}`
    : max !== undefined
    ? `${fieldName} should not exceed ${max}`
    : 'Invalid number',
  trigger,
  transform: (value: any) => {
    if (value === '' || value === null || value === undefined) return value
    return Number(value)
  },
})

/**
 * 自定义验证器：邮箱
 */
export const emailValidator = (_rule: any, value: string, callback: any) => {
  if (!value) {
    callback()
    return
  }
  if (!REGEX_PATTERNS.email.test(value)) {
    callback(new Error('Please enter a valid email address'))
  } else {
    callback()
  }
}

/**
 * 自定义验证器：用户名
 */
export const usernameValidator = (_rule: any, value: string, callback: any) => {
  if (!value) {
    callback()
    return
  }
  if (!REGEX_PATTERNS.username.test(value)) {
    callback(new Error('Username can only contain letters, numbers, underscores and hyphens'))
  } else {
    callback()
  }
}

/**
 * 自定义验证器：密码强度
 */
export const passwordStrengthValidator = (_rule: any, value: string, callback: any) => {
  if (!value) {
    callback()
    return
  }
  if (value.length < DB_CONSTRAINTS.password.min) {
    callback(new Error(`Password should be at least ${DB_CONSTRAINTS.password.min} characters`))
  } else if (!REGEX_PATTERNS.password.test(value)) {
    callback(new Error('Password must contain at least one letter and one number'))
  } else {
    callback()
  }
}

/**
 * 自定义验证器：确认密码
 */
export const createConfirmPasswordValidator = (passwordField: string) => {
  return (_rule: any, value: string, callback: any, formData: any) => {
    if (!value) {
      callback(new Error('Please confirm your password'))
      return
    }
    if (value !== formData[passwordField]) {
      callback(new Error('The two passwords do not match'))
    } else {
      callback()
    }
  }
}

/**
 * 自定义验证器：手机号
 */
export const phoneValidator = (_rule: any, value: string, callback: any) => {
  if (!value) {
    callback()
    return
  }
  if (!REGEX_PATTERNS.phone.test(value)) {
    callback(new Error('Please enter a valid phone number'))
  } else {
    callback()
  }
}

/**
 * 自定义验证器：CAS号
 */
export const casNumberValidator = (_rule: any, value: string, callback: any) => {
  if (!value) {
    callback()
    return
  }
  if (!REGEX_PATTERNS.casNumber.test(value)) {
    callback(new Error('Please enter a valid CAS number (e.g., 50-00-0)'))
  } else {
    callback()
  }
}

/**
 * 自定义验证器：URL
 */
export const urlValidator = (_rule: any, value: string, callback: any) => {
  if (!value) {
    callback()
    return
  }
  if (!REGEX_PATTERNS.url.test(value)) {
    callback(new Error('Please enter a valid URL'))
  } else {
    callback()
  }
}

/**
 * 自定义验证器：正数
 */
export const positiveNumberValidator = (fieldName: string) => {
  return (_rule: any, value: any, callback: any) => {
    if (value === '' || value === null || value === undefined) {
      callback()
      return
    }
    const num = Number(value)
    if (isNaN(num) || num < 0) {
      callback(new Error(`${fieldName} must be a positive number`))
    } else {
      callback()
    }
  }
}

// ==================== 预定义验证规则 ====================

/**
 * 用户名验证规则
 */
export const usernameRules: FormItemRule[] = [
  createRequiredValidator('username'),
  createLengthValidator('Username', DB_CONSTRAINTS.username.min, DB_CONSTRAINTS.username.max),
  { validator: usernameValidator, trigger: 'blur' },
]

/**
 * 密码验证规则
 */
export const passwordRules: FormItemRule[] = [
  createRequiredValidator('password'),
  { validator: passwordStrengthValidator, trigger: 'blur' },
]

/**
 * 邮箱验证规则
 */
export const emailRules: FormItemRule[] = [
  { validator: emailValidator, trigger: 'blur' },
  createLengthValidator('Email', undefined, DB_CONSTRAINTS.email.max),
]

/**
 * 真实姓名验证规则
 */
export const realNameRules: FormItemRule[] = [
  createRequiredValidator('real name'),
  createLengthValidator('Real name', DB_CONSTRAINTS.realName.min, DB_CONSTRAINTS.realName.max),
]

/**
 * 职位验证规则
 */
export const positionRules: FormItemRule[] = [
  createLengthValidator('Position', DB_CONSTRAINTS.position.min, DB_CONSTRAINTS.position.max),
]

/**
 * 项目名称验证规则
 */
export const projectNameRules: FormItemRule[] = [
  createRequiredValidator('project name'),
  createLengthValidator('Project name', DB_CONSTRAINTS.projectName.min, DB_CONSTRAINTS.projectName.max),
]

/**
 * 配方师名称验证规则
 */
export const formulatorNameRules: FormItemRule[] = [
  createRequiredValidator('formulator name'),
  createLengthValidator('Formulator name', DB_CONSTRAINTS.formulatorName.min, DB_CONSTRAINTS.formulatorName.max),
]

/**
 * 商品名称验证规则（原料/填料）
 */
export const tradeNameRules: FormItemRule[] = [
  createRequiredValidator('trade name'),
  createLengthValidator('Trade name', DB_CONSTRAINTS.tradeName.min, DB_CONSTRAINTS.tradeName.max),
]

/**
 * 供应商验证规则
 */
export const supplierRules: FormItemRule[] = [
  createLengthValidator('Supplier', undefined, DB_CONSTRAINTS.supplier.max),
]

/**
 * CAS号验证规则
 */
export const casNumberRules: FormItemRule[] = [
  { validator: casNumberValidator, trigger: 'blur' },
  createLengthValidator('CAS number', undefined, DB_CONSTRAINTS.casNumber.max),
]

/**
 * 重量百分比验证规则
 */
export const weightPercentageRules: FormItemRule[] = [
  createRequiredValidator('weight percentage'),
  createNumberRangeValidator(
    'Weight percentage',
    DB_CONSTRAINTS.weightPercentage.min,
    DB_CONSTRAINTS.weightPercentage.max
  ),
]

/**
 * 密度验证规则
 */
export const densityRules: FormItemRule[] = [
  { validator: positiveNumberValidator('Density'), trigger: 'blur' },
]

/**
 * 粘度验证规则
 */
export const viscosityRules: FormItemRule[] = [
  { validator: positiveNumberValidator('Viscosity'), trigger: 'blur' },
]

/**
 * 比表面积验证规则
 */
export const surfaceAreaRules: FormItemRule[] = [
  { validator: positiveNumberValidator('Surface area'), trigger: 'blur' },
]

// ==================== 工具函数 ====================

/**
 * 创建组合验证规则
 */
export const createCombinedRules = (...ruleArrays: FormItemRule[][]): FormItemRule[] => {
  return ruleArrays.flat()
}

/**
 * 创建选择器必填规则
 */
export const createSelectRequiredRule = (fieldName: string): FormItemRule => ({
  required: true,
  message: `Please select ${fieldName}`,
  trigger: 'change',
})

/**
 * 创建日期必填规则
 * Note: 不使用 type: 'date'，因为 el-date-picker 配合 value-format 会返回字符串
 */
export const createDateRequiredRule = (fieldName: string): FormItemRule => ({
  required: true,
  message: `Please select ${fieldName}`,
  trigger: 'change',
})

/**
 * 创建数组必填规则（多选）
 */
export const createArrayRequiredRule = (fieldName: string, minLength: number = 1): FormItemRule => ({
  required: true,
  type: 'array',
  min: minLength,
  message: `Please select at least ${minLength} ${fieldName}`,
  trigger: 'change',
})

// ==================== 导出默认对象 ====================
export default {
  // 约束常量
  DB_CONSTRAINTS,
  REGEX_PATTERNS,
  
  // 创建器函数
  createRequiredValidator,
  createLengthValidator,
  createPatternValidator,
  createNumberRangeValidator,
  createSelectRequiredRule,
  createDateRequiredRule,
  createArrayRequiredRule,
  createCombinedRules,
  createConfirmPasswordValidator,
  
  // 自定义验证器
  emailValidator,
  usernameValidator,
  passwordStrengthValidator,
  phoneValidator,
  casNumberValidator,
  urlValidator,
  positiveNumberValidator,
  
  // 预定义规则
  usernameRules,
  passwordRules,
  emailRules,
  realNameRules,
  positionRules,
  projectNameRules,
  formulatorNameRules,
  tradeNameRules,
  supplierRules,
  casNumberRules,
  weightPercentageRules,
  densityRules,
  viscosityRules,
  surfaceAreaRules,
}

