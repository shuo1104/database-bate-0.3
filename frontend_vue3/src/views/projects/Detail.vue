<template>
  <div class="project-detail-container">
    <el-card shadow="never" class="header-card">
      <div class="header-actions">
        <el-button @click="handleBack">
          <el-icon><ArrowLeft /></el-icon>
          Back
        </el-button>
        <div>
          <el-button type="success" @click="handleExportImage" :loading="exportLoading">
            <el-icon><Picture /></el-icon>
            Export Image Report
          </el-button>
          <el-button type="primary" @click="handleEdit">Edit Project</el-button>
          <el-button type="danger" @click="handleDelete">Delete Project</el-button>
        </div>
      </div>
    </el-card>

    <!-- Project Basic Information -->
    <el-card shadow="never" class="info-card">
      <template #header>
        <div class="card-header">
          <span>Project Basic Information</span>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Project Name">{{ projectInfo.ProjectName }}</el-descriptions-item>
        <el-descriptions-item label="Formula Code">{{ projectInfo.FormulaCode }}</el-descriptions-item>
        <el-descriptions-item label="Project Type">{{ projectInfo.TypeName }}</el-descriptions-item>
        <el-descriptions-item label="Formulator">{{ projectInfo.FormulatorName }}</el-descriptions-item>
        <el-descriptions-item label="Formulation Date">{{ projectInfo.FormulationDate }}</el-descriptions-item>
        <el-descriptions-item label="Substrate/Application">{{ projectInfo.SubstrateApplication || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- Formula Composition -->
    <el-card shadow="never" class="composition-card">
      <template #header>
        <div class="card-header">
          <span>Formula Composition</span>
          <el-button type="primary" size="small" @click="handleAddComposition">Add Component</el-button>
        </div>
      </template>
      
      <el-table :data="compositions" border stripe style="width: 100%">
        <el-table-column prop="CompositionID" label="ID" width="80" />
        <el-table-column label="Component Type" width="140">
          <template #default="{ row }">
            <el-tag v-if="row.MaterialID_FK" type="success">Material</el-tag>
            <el-tag v-else-if="row.FillerID_FK" type="warning">Filler</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Component Name" min-width="150">
          <template #default="{ row }">
            {{ row.MaterialName || row.FillerName || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="WeightPercent" label="Weight (%)" width="120" />
        <el-table-column prop="AdditionMethod" label="Addition Method" min-width="150" show-overflow-tooltip />
        <el-table-column prop="Remark" label="Remarks" min-width="150" show-overflow-tooltip />
        <el-table-column label="Actions" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEditComposition(row)">Edit</el-button>
            <el-button type="danger" size="small" @click="handleDeleteComposition(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="composition-summary">
        <el-tag type="info" size="large">
          Total Weight Percentage: {{ totalWeightPercentage.toFixed(2) }}%
        </el-tag>
        <el-tag :type="totalWeightPercentage <= 100 ? 'success' : 'danger'" size="large">
          {{ totalWeightPercentage <= 100 ? '✓ Normal' : '⚠ Exceeds 100%' }}
        </el-tag>
      </div>
    </el-card>

    <!-- Test Results -->
    <el-card shadow="never" class="test-result-card">
      <template #header>
        <div class="card-header">
          <span>Test Results</span>
          <el-button type="primary" size="small" @click="handleEditTestResult">Edit Test Results</el-button>
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
      <el-empty v-else description="No test results yet. Click the button above to add." />
    </el-card>

    <!-- Add/Edit Composition Dialog -->
    <el-dialog
      v-model="compositionDialogVisible"
      :title="compositionDialogTitle"
      width="600px"
      @close="handleCompositionDialogClose"
    >
      <el-form ref="compositionFormRef" :model="compositionFormData" :rules="compositionFormRules" label-width="150px">
        <el-form-item label="Component Type" prop="componentType">
          <el-radio-group v-model="compositionFormData.componentType">
            <el-radio label="material">Material</el-radio>
            <el-radio label="filler">Filler</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="compositionFormData.componentType === 'material'" label="Select Material" prop="MaterialID_FK">
          <el-select
            v-model="compositionFormData.MaterialID_FK"
            placeholder="Select or search material"
            style="width: 100%"
            filterable
            :loading="materialsLoading"
          >
            <el-option
              v-for="material in materials"
              :key="material.MaterialID"
              :label="material.TradeName"
              :value="material.MaterialID"
            />
          </el-select>
        </el-form-item>
        <el-form-item v-if="compositionFormData.componentType === 'filler'" label="Select Filler" prop="FillerID_FK">
          <el-select
            v-model="compositionFormData.FillerID_FK"
            placeholder="Select or search filler"
            style="width: 100%"
            filterable
            :loading="fillersLoading"
          >
            <el-option
              v-for="filler in fillers"
              :key="filler.FillerID"
              :label="filler.TradeName"
              :value="filler.FillerID"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Weight Percentage" prop="WeightPercent">
          <el-input v-model.number="compositionFormData.WeightPercent" placeholder="Enter weight percentage" type="number" step="0.01">
            <template #append>%</template>
          </el-input>
        </el-form-item>
        <el-form-item label="Addition Method">
          <el-input v-model="compositionFormData.AdditionMethod" placeholder="Enter addition method" />
        </el-form-item>
        <el-form-item label="Remarks">
          <el-input
            v-model="compositionFormData.Remark"
            type="textarea"
            :rows="3"
            placeholder="Enter remarks"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="compositionDialogVisible = false">Cancel</el-button>
        <el-button type="primary" :loading="compositionSubmitLoading" @click="handleSubmitComposition">Confirm</el-button>
      </template>
    </el-dialog>

    <!-- Test Results Edit Dialog -->
    <el-dialog
      v-model="testResultDialogVisible"
      title="Edit Test Results"
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
        <el-button @click="testResultDialogVisible = false">Cancel</el-button>
        <el-button type="primary" :loading="testResultSubmitLoading" @click="handleSaveTestResult">Save</el-button>
      </template>
    </el-dialog>

    <!-- Edit Project Dialog -->
    <el-dialog
      v-model="projectDialogVisible"
      title="Edit Project Information"
      width="600px"
      @close="handleProjectDialogClose"
    >
      <el-form ref="projectFormRef" :model="projectFormData" :rules="projectFormRules" label-width="160px">
        <el-form-item label="Project Name" prop="project_name">
          <el-input v-model="projectFormData.project_name" placeholder="Enter project name" />
        </el-form-item>
        <el-form-item label="Project Type" prop="project_type_fk">
          <el-select v-model="projectFormData.project_type_fk" placeholder="Select project type" style="width: 100%">
            <el-option
              v-for="type in projectTypes"
              :key="type.TypeID"
              :label="type.TypeName"
              :value="type.TypeID"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Formulator" prop="formulator_name">
          <el-input v-model="projectFormData.formulator_name" placeholder="Enter formulator name" />
        </el-form-item>
        <el-form-item label="Formulation Date" prop="formulation_date">
          <el-date-picker
            v-model="projectFormData.formulation_date"
            type="date"
            placeholder="Select formulation date"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="Substrate/Application">
          <el-input
            v-model="projectFormData.substrate_application"
            type="textarea"
            :rows="3"
            placeholder="Enter substrate or application"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="projectDialogVisible = false">Cancel</el-button>
        <el-button type="primary" :loading="projectSubmitLoading" @click="handleSubmitProject">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { ArrowLeft, Picture } from '@element-plus/icons-vue'
import {
  getProjectDetailApi,
  deleteProjectApi,
  updateProjectApi,
  exportProjectImageApi,
  getProjectTypesApi,
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
// import { formatDateTime } from '@/utils/common'
import TestResultForm from './components/TestResultForm.vue'
import {
  projectNameRules,
  formulatorNameRules,
  weightPercentageRules,
  createSelectRequiredRule,
  createDateRequiredRule,
} from '@/utils/validators'

const route = useRoute()
const router = useRouter()

const projectId = computed(() => Number(route.params.id))
const projectInfo = ref<Partial<ProjectInfo>>({})
const compositions = ref<FormulaComposition[]>([])
const testResult = ref<any>(null)
const materials = ref<MaterialInfo[]>([])
const fillers = ref<FillerInfo[]>([])
const exportLoading = ref(false)
const materialsLoading = ref(false)
const fillersLoading = ref(false)

// 计算总重量百分比
const totalWeightPercentage = computed(() => {
  return compositions.value.reduce((sum, item) => {
    const weight = Number(item.WeightPercent) || 0
    return sum + weight
  }, 0)
})

// Composition dialog
const compositionDialogVisible = ref(false)
const compositionDialogTitle = ref('Add Component')
const compositionFormRef = ref<FormInstance>()
const compositionSubmitLoading = ref(false)

interface CompositionFormData {
  CompositionID?: number
  componentType: 'material' | 'filler'
  MaterialID_FK?: number
  FillerID_FK?: number
  WeightPercent?: number
  AdditionMethod?: string
  Remark?: string
}

const compositionFormData = reactive<CompositionFormData>({
  componentType: 'material',
  WeightPercent: undefined,
  AdditionMethod: '',
  Remark: '',
})

const compositionFormRules = {
  componentType: [createSelectRequiredRule('component type')],
  MaterialID_FK: [createSelectRequiredRule('material')],
  FillerID_FK: [createSelectRequiredRule('filler')],
  WeightPercent: weightPercentageRules,
}

// 测试结果相关
const testResultDialogVisible = ref(false)
const testResultSubmitLoading = ref(false)
const testResultFormRef = ref<InstanceType<typeof TestResultForm>>()

// 项目编辑相关
const projectDialogVisible = ref(false)
const projectFormRef = ref<FormInstance>()
const projectSubmitLoading = ref(false)
const projectTypes = ref<any[]>([])

const projectFormData = reactive({
  project_name: '',
  project_type_fk: undefined as number | undefined,
  formulator_name: '',
  formulation_date: '',
  substrate_application: '',
})

const projectFormRules = {
  project_name: projectNameRules,
  project_type_fk: [createSelectRequiredRule('project type')],
  formulator_name: formulatorNameRules,
  formulation_date: [createDateRequiredRule('formulation date')],
}

// Get project details
async function getProjectDetail() {
  try {
    projectInfo.value = await getProjectDetailApi(projectId.value)
  } catch (error) {
    ElMessage.error('Failed to get project details')
    console.error(error)
  }
}

// Get composition list
async function getCompositions() {
  try {
    console.log('Loading compositions for project:', projectId.value)
    const res = await getCompositionListApi(projectId.value)
    console.log('Composition response:', res)
    compositions.value = Array.isArray(res) ? res : []
    console.log('Compositions set to:', compositions.value)
  } catch (error) {
    ElMessage.error('Failed to get composition list')
    console.error('Failed to load compositions:', error)
  }
}

// Get materials and fillers list (initial load)
async function getMaterialsAndFillers() {
  try {
    const [materialsRes, fillersRes] = await Promise.all([
      getMaterialListApi({ page: 1, page_size: 100 }),
      getFillerListApi({ page: 1, page_size: 100 })
    ])
    materials.value = materialsRes.list || materialsRes.items || []
    fillers.value = fillersRes.list || fillersRes.items || []
  } catch (error) {
    console.error('Failed to get materials/fillers list:', error)
  }
}

// Search materials by keyword (remote search)
async function searchMaterials(query: string) {
  if (!query || query.trim() === '') {
    // If empty, load first 100 as default
    materialsLoading.value = true
    try {
      const res = await getMaterialListApi({ page: 1, page_size: 100 })
      materials.value = res.list || res.items || []
    } catch (error) {
      console.error('Failed to load materials:', error)
    } finally {
      materialsLoading.value = false
    }
    return
  }

  materialsLoading.value = true
  try {
    const res = await getMaterialListApi({
      page: 1,
      page_size: 50,
      keyword: query
    })
    materials.value = res.list || res.items || []
  } catch (error) {
    console.error('Failed to search materials:', error)
  } finally {
    materialsLoading.value = false
  }
}

// Search fillers by keyword (remote search)
async function searchFillers(query: string) {
  if (!query || query.trim() === '') {
    // If empty, load first 100 as default
    fillersLoading.value = true
    try {
      const res = await getFillerListApi({ page: 1, page_size: 100 })
      fillers.value = res.list || res.items || []
    } catch (error) {
      console.error('Failed to load fillers:', error)
    } finally {
      fillersLoading.value = false
    }
    return
  }

  fillersLoading.value = true
  try {
    const res = await getFillerListApi({
      page: 1,
      page_size: 50,
      keyword: query
    })
    fillers.value = res.list || res.items || []
  } catch (error) {
    console.error('Failed to search fillers:', error)
  } finally {
    fillersLoading.value = false
  }
}

// 返回
function handleBack() {
  router.push('/projects')
}

// 编辑项目
function handleEdit() {
  // 填充表单数据
  projectFormData.project_name = projectInfo.value.ProjectName || ''
  projectFormData.project_type_fk = projectInfo.value.ProjectType_FK
  projectFormData.formulator_name = projectInfo.value.FormulatorName || ''
  projectFormData.formulation_date = projectInfo.value.FormulationDate || ''
  projectFormData.substrate_application = projectInfo.value.SubstrateApplication || ''
  
  projectDialogVisible.value = true
}

// Delete project
function handleDelete() {
  ElMessageBox.confirm('Are you sure you want to delete this project?', 'Confirmation', {
    confirmButtonText: 'Confirm',
    cancelButtonText: 'Cancel',
    type: 'warning',
  }).then(async () => {
    try {
      await deleteProjectApi(projectId.value)
      ElMessage.success('Deleted successfully')
      router.push('/projects')
    } catch (error) {
      ElMessage.error('Delete failed')
    }
  })
}

// Add component
function handleAddComposition() {
  compositionDialogTitle.value = 'Add Component'
  compositionDialogVisible.value = true
}

// Edit component
function handleEditComposition(row: FormulaComposition) {
  compositionDialogTitle.value = 'Edit Component'
  Object.assign(compositionFormData, {
    CompositionID: row.CompositionID,
    componentType: row.MaterialID_FK ? 'material' : 'filler',
    MaterialID_FK: row.MaterialID_FK,
    FillerID_FK: row.FillerID_FK,
    WeightPercent: row.WeightPercent ? Number(row.WeightPercent) : undefined,
    AdditionMethod: row.AdditionMethod,
    Remark: row.Remark,
  })
  compositionDialogVisible.value = true
}

// Delete component
function handleDeleteComposition(row: FormulaComposition) {
  ElMessageBox.confirm('Are you sure you want to delete this component?', 'Confirmation', {
    confirmButtonText: 'Confirm',
    cancelButtonText: 'Cancel',
    type: 'warning',
  }).then(async () => {
    try {
      await deleteCompositionApi(row.CompositionID)
      ElMessage.success('Deleted successfully')
      getCompositions()
    } catch (error) {
      ElMessage.error('Delete failed')
    }
  })
}

// Submit composition
async function handleSubmitComposition() {
  if (!compositionFormRef.value) return

  await compositionFormRef.value.validate(async (valid) => {
    if (valid) {
      compositionSubmitLoading.value = true
      try {
        const data: any = {
          project_id: projectId.value,
          weight_percentage: compositionFormData.WeightPercent,
          addition_method: compositionFormData.AdditionMethod,
          remarks: compositionFormData.Remark,
        }

        if (compositionFormData.componentType === 'material') {
          data.material_id = compositionFormData.MaterialID_FK
        } else {
          data.filler_id = compositionFormData.FillerID_FK
        }

        if (compositionFormData.CompositionID) {
          await updateCompositionApi(compositionFormData.CompositionID, data)
          ElMessage.success('Updated successfully')
        } else {
          await createCompositionApi(data)
          ElMessage.success('Added successfully')
        }
        compositionDialogVisible.value = false
        getCompositions()
      } catch (error) {
        ElMessage.error(compositionFormData.CompositionID ? 'Update failed' : 'Add failed')
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
    WeightPercent: undefined,
    AdditionMethod: '',
    Remark: '',
  })
}

// Export image report
async function handleExportImage() {
  exportLoading.value = true
  try {
    const blob = await exportProjectImageApi(projectId.value)
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([blob]))
    const link = document.createElement('a')
    link.href = url
    const timestamp = new Date().getTime()
    link.setAttribute('download', `project_${projectId.value}_report_${timestamp}.png`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('Image report exported successfully')
  } catch (error: any) {
    console.error('Export image report failed:', error)
    ElMessage.error('Export image report failed: ' + (error.response?.data?.detail || error.message || 'Unknown error'))
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
  console.log('Test result saved callback triggered')
  testResultDialogVisible.value = false
  await loadTestResults()
  console.log('Test results reloaded after save')
}

// 关闭测试结果对话框
function handleTestResultDialogClose() {
  // 清理逻辑
}

// Load test results
async function loadTestResults() {
  try {
    console.log('Loading test results for project:', projectId.value)
    const res = await getTestResultApi(projectId.value)
    console.log('Test result response:', res)
    testResult.value = res || null
    console.log('Test result set to:', testResult.value)
  } catch (error) {
    console.error('Load test results failed:', error)
    testResult.value = null
  }
}

// Get test result component (based on project type)
// function getTestResultComponent() {
//   // Can return different test result display components based on project type
//   // Temporarily returns a simple display
//   return () => h('div', { class: 'simple-test-result' }, 'Test result component under development...')
// }

// Get project types list
async function getProjectTypes() {
  try {
    const types = await getProjectTypesApi()
    projectTypes.value = types || []
  } catch (error) {
    console.error('Failed to get project types:', error)
  }
}

// Submit project edit
async function handleSubmitProject() {
  if (!projectFormRef.value) return

  await projectFormRef.value.validate(async (valid) => {
    if (valid) {
      projectSubmitLoading.value = true
      try {
        await updateProjectApi(projectId.value, projectFormData as any)
        ElMessage.success('Project updated successfully')
        projectDialogVisible.value = false
        // Reload project details
        await getProjectDetail()
      } catch (error) {
        console.error('Update project failed:', error)
        ElMessage.error('Project update failed')
      } finally {
        projectSubmitLoading.value = false
      }
    }
  })
}

// Project dialog close
function handleProjectDialogClose() {
  projectFormRef.value?.resetFields()
  Object.assign(projectFormData, {
    project_name: '',
    project_type_fk: undefined,
    formulator_name: '',
    formulation_date: '',
    substrate_application: '',
  })
}

onMounted(() => {
  getProjectDetail()
  getCompositions()
  getMaterialsAndFillers()
  loadTestResults()
  getProjectTypes()
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

