<template>
  <div class="project-detail-container">
    <el-card shadow="never" class="header-card">
      <div class="header-actions">
        <el-button @click="handleBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <div>
          <el-button type="success" @click="handleExportImage" :loading="exportLoading">
            <el-icon><Picture /></el-icon>
            导出图片报告
          </el-button>
          <el-button type="primary" @click="handleEdit">编辑项目</el-button>
          <el-button type="danger" @click="handleDelete">删除项目</el-button>
        </div>
      </div>
    </el-card>

    <!-- 项目基本信息 -->
    <el-card shadow="never" class="info-card">
      <template #header>
        <div class="card-header">
          <span>项目基本信息</span>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="项目名称">{{ projectInfo.ProjectName }}</el-descriptions-item>
        <el-descriptions-item label="配方编号">{{ projectInfo.FormulaCode }}</el-descriptions-item>
        <el-descriptions-item label="项目类型">{{ projectInfo.TypeName }}</el-descriptions-item>
        <el-descriptions-item label="配方设计师">{{ projectInfo.FormulatorName }}</el-descriptions-item>
        <el-descriptions-item label="配方日期">{{ projectInfo.FormulationDate }}</el-descriptions-item>
        <el-descriptions-item label="目标基材">{{ projectInfo.SubstrateApplication || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间" :span="2">{{ formatDateTime(projectInfo.CreatedAt) }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 配方成分 -->
    <el-card shadow="never" class="composition-card">
      <template #header>
        <div class="card-header">
          <span>配方成分</span>
          <el-button type="primary" size="small" @click="handleAddComposition">添加成分</el-button>
        </div>
      </template>
      
      <el-table :data="compositions" border stripe style="width: 100%">
        <el-table-column prop="CompositionID" label="ID" width="80" />
        <el-table-column label="成分类型" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.MaterialID_FK" type="success">原料</el-tag>
            <el-tag v-else-if="row.FillerID_FK" type="warning">填料</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="成分名称" min-width="150">
          <template #default="{ row }">
            {{ row.MaterialName || row.FillerName || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="WeightPercentage" label="重量百分比 (%)" width="140" />
        <el-table-column prop="AdditionMethod" label="掺入方法" min-width="150" show-overflow-tooltip />
        <el-table-column prop="Remarks" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEditComposition(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDeleteComposition(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="composition-summary">
        <el-tag type="info" size="large">
          总重量百分比: {{ totalWeightPercentage.toFixed(2) }}%
        </el-tag>
        <el-tag :type="totalWeightPercentage <= 100 ? 'success' : 'danger'" size="large">
          {{ totalWeightPercentage <= 100 ? '✓ 配比正常' : '⚠ 超过100%' }}
        </el-tag>
      </div>
    </el-card>

    <!-- 测试结果 -->
    <el-card shadow="never" class="test-result-card">
      <template #header>
        <div class="card-header">
          <span>测试结果</span>
          <el-button type="primary" size="small" @click="handleEditTestResult">编辑测试结果</el-button>
        </div>
      </template>
      
      <div v-if="testResult" class="test-result-content">
        <el-descriptions :column="2" border>
          <template v-for="(value, key) in testResult" :key="key">
            <el-descriptions-item v-if="!['ResultID', 'ProjectID_FK'].includes(String(key))" :label="String(key)">
              {{ value || '-' }}
            </el-descriptions-item>
          </template>
        </el-descriptions>
      </div>
      <el-empty v-else description="暂无测试结果，点击上方按钮添加" />
    </el-card>

    <!-- 添加/编辑配方成分对话框 -->
    <el-dialog
      v-model="compositionDialogVisible"
      :title="compositionDialogTitle"
      width="600px"
      @close="handleCompositionDialogClose"
    >
      <el-form ref="compositionFormRef" :model="compositionFormData" :rules="compositionFormRules" label-width="120px">
        <el-form-item label="成分类型" prop="componentType">
          <el-radio-group v-model="compositionFormData.componentType">
            <el-radio label="material">原料</el-radio>
            <el-radio label="filler">填料</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="compositionFormData.componentType === 'material'" label="选择原料" prop="MaterialID_FK">
          <el-select v-model="compositionFormData.MaterialID_FK" placeholder="请选择原料" style="width: 100%" filterable>
            <el-option
              v-for="material in materials"
              :key="material.MaterialID"
              :label="material.TradeName"
              :value="material.MaterialID"
            />
          </el-select>
        </el-form-item>
        <el-form-item v-if="compositionFormData.componentType === 'filler'" label="选择填料" prop="FillerID_FK">
          <el-select v-model="compositionFormData.FillerID_FK" placeholder="请选择填料" style="width: 100%" filterable>
            <el-option
              v-for="filler in fillers"
              :key="filler.FillerID"
              :label="filler.TradeName"
              :value="filler.FillerID"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="重量百分比" prop="WeightPercentage">
          <el-input v-model.number="compositionFormData.WeightPercentage" placeholder="请输入重量百分比" type="number" step="0.01">
            <template #append>%</template>
          </el-input>
        </el-form-item>
        <el-form-item label="掺入方法">
          <el-input v-model="compositionFormData.AdditionMethod" placeholder="请输入掺入方法" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="compositionFormData.Remarks"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="compositionDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="compositionSubmitLoading" @click="handleSubmitComposition">确定</el-button>
      </template>
    </el-dialog>

    <!-- 测试结果编辑对话框 -->
    <el-dialog
      v-model="testResultDialogVisible"
      title="编辑测试结果"
      width="800px"
      @close="handleTestResultDialogClose"
    >
      <TestResultForm
        ref="testResultFormRef"
        :project-id="projectId"
        :project-type="projectInfo.TypeName || ''"
        @saved="handleTestResultSaved"
      />
      <template #footer>
        <el-button @click="testResultDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="testResultSubmitLoading" @click="handleSaveTestResult">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { ArrowLeft, Picture } from '@element-plus/icons-vue'
import {
  getProjectDetailApi,
  deleteProjectApi,
  exportProjectImageApi,
  type ProjectInfo
} from '@/api/projects'
import {
  getCompositionListApi,
  createCompositionApi,
  updateCompositionApi,
  deleteCompositionApi,
  type FormulaComposition
} from '@/api/projects'
import { getMaterialListApi, type MaterialInfo } from '@/api/materials'
import { getFillerListApi, type FillerInfo } from '@/api/fillers'
import { getTestResultApi } from '@/api/test-results'
import { formatDateTime } from '@/utils/common'
import TestResultForm from './components/TestResultForm.vue'

const route = useRoute()
const router = useRouter()

const projectId = computed(() => Number(route.params.id))
const projectInfo = ref<Partial<ProjectInfo>>({})
const compositions = ref<FormulaComposition[]>([])
const testResult = ref<any>(null)
const materials = ref<MaterialInfo[]>([])
const fillers = ref<FillerInfo[]>([])
const exportLoading = ref(false)

// 计算总重量百分比
const totalWeightPercentage = computed(() => {
  return compositions.value.reduce((sum, item) => {
    const weight = Number(item.WeightPercentage) || 0
    return sum + weight
  }, 0)
})

// 配方成分对话框
const compositionDialogVisible = ref(false)
const compositionDialogTitle = ref('添加成分')
const compositionFormRef = ref<FormInstance>()
const compositionSubmitLoading = ref(false)

interface CompositionFormData {
  CompositionID?: number
  componentType: 'material' | 'filler'
  MaterialID_FK?: number
  FillerID_FK?: number
  WeightPercentage?: number
  AdditionMethod?: string
  Remarks?: string
}

const compositionFormData = reactive<CompositionFormData>({
  componentType: 'material',
  WeightPercentage: undefined,
  AdditionMethod: '',
  Remarks: '',
})

const compositionFormRules = {
  componentType: [{ required: true, message: '请选择成分类型', trigger: 'change' }],
  MaterialID_FK: [{ required: true, message: '请选择原料', trigger: 'change' }],
  FillerID_FK: [{ required: true, message: '请选择填料', trigger: 'change' }],
  WeightPercentage: [
    { required: true, message: '请输入重量百分比', trigger: 'blur' },
    { type: 'number', min: 0, max: 100, message: '重量百分比应在0-100之间', trigger: 'blur' }
  ],
}

// 测试结果相关
const testResultDialogVisible = ref(false)
const testResultSubmitLoading = ref(false)
const testResultFormRef = ref<InstanceType<typeof TestResultForm>>()

// 获取项目详情
async function getProjectDetail() {
  try {
    projectInfo.value = await getProjectDetailApi(projectId.value)
  } catch (error) {
    ElMessage.error('获取项目详情失败')
    console.error(error)
  }
}

// 获取配方成分列表
async function getCompositions() {
  try {
    const res = await getCompositionListApi(projectId.value)
    compositions.value = Array.isArray(res) ? res : []
  } catch (error) {
    ElMessage.error('获取配方成分失败')
    console.error(error)
  }
}

// 获取原料和填料列表
async function getMaterialsAndFillers() {
  try {
    const [materialsRes, fillersRes] = await Promise.all([
      getMaterialListApi({ page: 1, page_size: 100 }),
      getFillerListApi({ page: 1, page_size: 100 })
    ])
    materials.value = materialsRes.list || materialsRes.items || []
    fillers.value = fillersRes.list || fillersRes.items || []
  } catch (error) {
    console.error('获取原料/填料列表失败:', error)
  }
}

// 返回
function handleBack() {
  router.push('/projects')
}

// 编辑项目
function handleEdit() {
  ElMessage.info('编辑功能开发中...')
}

// 删除项目
function handleDelete() {
  ElMessageBox.confirm('确定要删除该项目吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await deleteProjectApi(projectId.value)
      ElMessage.success('删除成功')
      router.push('/projects')
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

// 添加成分
function handleAddComposition() {
  compositionDialogTitle.value = '添加成分'
  compositionDialogVisible.value = true
}

// 编辑成分
function handleEditComposition(row: FormulaComposition) {
  compositionDialogTitle.value = '编辑成分'
  Object.assign(compositionFormData, {
    CompositionID: row.CompositionID,
    componentType: row.MaterialID_FK ? 'material' : 'filler',
    MaterialID_FK: row.MaterialID_FK,
    FillerID_FK: row.FillerID_FK,
    WeightPercentage: row.WeightPercentage,
    AdditionMethod: row.AdditionMethod,
    Remarks: row.Remarks,
  })
  compositionDialogVisible.value = true
}

// 删除成分
function handleDeleteComposition(row: FormulaComposition) {
  ElMessageBox.confirm('确定要删除该成分吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await deleteCompositionApi(row.CompositionID)
      ElMessage.success('删除成功')
      getCompositions()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

// 提交配方成分
async function handleSubmitComposition() {
  if (!compositionFormRef.value) return

  await compositionFormRef.value.validate(async (valid) => {
    if (valid) {
      compositionSubmitLoading.value = true
      try {
        const data: any = {
          project_id: projectId.value,
          weight_percentage: compositionFormData.WeightPercentage,
          addition_method: compositionFormData.AdditionMethod,
          remarks: compositionFormData.Remarks,
        }

        if (compositionFormData.componentType === 'material') {
          data.material_id = compositionFormData.MaterialID_FK
        } else {
          data.filler_id = compositionFormData.FillerID_FK
        }

        if (compositionFormData.CompositionID) {
          await updateCompositionApi(compositionFormData.CompositionID, data)
          ElMessage.success('更新成功')
        } else {
          await createCompositionApi(data)
          ElMessage.success('添加成功')
        }
        compositionDialogVisible.value = false
        getCompositions()
      } catch (error) {
        ElMessage.error(compositionFormData.CompositionID ? '更新失败' : '添加失败')
      } finally {
        compositionSubmitLoading.value = false
      }
    }
  })
}

// 关闭配方成分对话框
function handleCompositionDialogClose() {
  compositionFormRef.value?.resetFields()
  Object.assign(compositionFormData, {
    componentType: 'material',
    WeightPercentage: undefined,
    AdditionMethod: '',
    Remarks: '',
  })
}

// 导出图片报告
async function handleExportImage() {
  exportLoading.value = true
  try {
    const blob = await exportProjectImageApi(projectId.value)
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([blob]))
    const link = document.createElement('a')
    link.href = url
    const timestamp = new Date().getTime()
    link.setAttribute('download', `project_${projectId.value}_report_${timestamp}.png`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('图片报告导出成功')
  } catch (error: any) {
    console.error('导出图片报告失败:', error)
    ElMessage.error('导出图片报告失败: ' + (error.response?.data?.detail || error.message || '未知错误'))
  } finally {
    exportLoading.value = false
  }
}

// 编辑测试结果
function handleEditTestResult() {
  testResultDialogVisible.value = true
}

// 保存测试结果
async function handleSaveTestResult() {
  if (!testResultFormRef.value) return

  testResultSubmitLoading.value = true
  try {
    await testResultFormRef.value.saveTestResult()
  } catch (error) {
    // 错误处理已在子组件中完成
  } finally {
    testResultSubmitLoading.value = false
  }
}

// 测试结果保存成功回调
async function handleTestResultSaved() {
  testResultDialogVisible.value = false
  await loadTestResults()
}

// 关闭测试结果对话框
function handleTestResultDialogClose() {
  // 清理逻辑
}

// 加载测试结果
async function loadTestResults() {
  try {
    const res = await getTestResultApi(projectId.value)
    testResult.value = res || null
  } catch (error) {
    console.error('加载测试结果失败:', error)
    testResult.value = null
  }
}

// 获取测试结果组件（根据项目类型）
function getTestResultComponent() {
  // 这里可以根据项目类型返回不同的测试结果展示组件
  // 暂时返回一个简单的显示
  return () => h('div', { class: 'simple-test-result' }, '测试结果组件开发中...')
}

onMounted(() => {
  getProjectDetail()
  getCompositions()
  getMaterialsAndFillers()
  loadTestResults()
})
</script>

<style scoped lang="scss">
.project-detail-container {
  .header-card {
    margin-bottom: 20px;

    .header-actions {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }

  .info-card,
  .composition-card,
  .test-result-card {
    margin-bottom: 20px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }

  .composition-summary {
    margin-top: 16px;
    padding: 12px;
    background-color: #f5f7fa;
    border-radius: 4px;
    display: flex;
    gap: 12px;
  }

  .test-result-content {
    padding: 16px;
  }
}
</style>

