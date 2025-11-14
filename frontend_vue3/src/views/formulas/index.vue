<template>
  <div class="formula-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>Formula Components Management</span>
        </div>
      </template>

      <!-- Search Area -->
      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="Project">
          <el-select
            v-model="queryParams.project_id"
            placeholder="Type to search project name or code"
            clearable
            filterable
            remote
            :remote-method="searchProjects"
            :loading="projectsLoading"
            style="width: 400px"
            @change="handleProjectChange"
            @clear="handleReset"
          >
            <el-option
              v-for="project in projects"
              :key="project.ProjectID"
              :label="`${project.ProjectName} (${project.FormulaCode || 'No Code'})`"
              :value="project.ProjectID"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <!-- Action Buttons -->
      <div class="toolbar">
        <el-button
          type="primary"
          :icon="Plus"
          @click="handleAdd"
          :disabled="!queryParams.project_id"
        >
          Add Component
        </el-button>
        <el-button
          type="danger"
          :icon="Delete"
          @click="handleBatchDelete"
          :disabled="selectedRows.length === 0"
        >
          Batch Delete
        </el-button>
      </div>

      <!-- Project Info Display -->
      <el-alert
        v-if="currentProject"
        :title="`Current Project: ${currentProject.ProjectName} | Formula Code: ${currentProject.FormulaCode} | Project Type: ${currentProject.TypeName || '-'}`"
        type="info"
        :closable="false"
        style="margin-bottom: 16px"
      />

      <!-- Data Table -->
      <el-table
        :data="tableData"
        border
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
        v-loading="loading"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="CompositionID" label="ID" width="80" />
        <el-table-column label="Component Type" width="120">
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
        <el-table-column prop="WeightPercentage" label="Weight Percentage (%)" width="160" />
        <el-table-column prop="AdditionMethod" label="Addition Method" min-width="150" show-overflow-tooltip />
        <el-table-column prop="Remarks" label="Remarks" min-width="150" show-overflow-tooltip />
        <el-table-column label="Actions" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">Edit</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Formula Summary -->
      <div v-if="tableData.length > 0" class="composition-summary">
        <el-tag type="info" size="large">
          Total Weight Percentage: {{ totalWeightPercentage.toFixed(2) }}%
        </el-tag>
        <el-tag :type="totalWeightPercentage <= 100 ? 'success' : 'danger'" size="large">
          {{ totalWeightPercentage <= 100 ? '✓ Normal Ratio' : '⚠ Exceeds 100%' }}
        </el-tag>
      </div>
    </el-card>

    <!-- Add/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="150px">
        <el-form-item label="Component Type" prop="componentType">
          <el-radio-group v-model="formData.componentType">
            <el-radio label="material">Material</el-radio>
            <el-radio label="filler">Filler</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="formData.componentType === 'material'" label="Select Material" prop="MaterialID_FK">
          <el-select v-model="formData.MaterialID_FK" placeholder="Select material" style="width: 100%" filterable>
            <el-option
              v-for="material in materials"
              :key="material.MaterialID"
              :label="material.TradeName"
              :value="material.MaterialID"
            />
          </el-select>
        </el-form-item>
        <el-form-item v-if="formData.componentType === 'filler'" label="Select Filler" prop="FillerID_FK">
          <el-select v-model="formData.FillerID_FK" placeholder="Select filler" style="width: 100%" filterable>
            <el-option
              v-for="filler in fillers"
              :key="filler.FillerID"
              :label="filler.TradeName"
              :value="filler.FillerID"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Weight Percentage" prop="WeightPercent">
          <el-input v-model.number="formData.WeightPercent" placeholder="Enter weight percentage" type="number" step="0.01">
            <template #append>%</template>
          </el-input>
        </el-form-item>
        <el-form-item label="Addition Method">
          <el-input v-model="formData.AdditionMethod" placeholder="Enter addition method" />
        </el-form-item>
        <el-form-item label="Remarks">
          <el-input
            v-model="formData.Remark"
            type="textarea"
            :rows="3"
            placeholder="Enter remarks"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">Confirm</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import {
  getProjectListApi,
  getProjectDetailApi,
  getCompositionListApi,
  createCompositionApi,
  updateCompositionApi,
  deleteCompositionApi,
  type ProjectInfo,
  type FormulaComposition
} from '@/api/projects'
import { getMaterialListApi, type MaterialInfo } from '@/api/materials'
import { getFillerListApi, type FillerInfo } from '@/api/fillers'

// Query parameters
const queryParams = reactive({
  project_id: undefined as number | undefined,
})

// Data
const loading = ref(false)
const projectsLoading = ref(false)
const tableData = ref<FormulaComposition[]>([])
const selectedRows = ref<FormulaComposition[]>([])
const projects = ref<ProjectInfo[]>([])
const currentProject = ref<ProjectInfo | null>(null)
const materials = ref<MaterialInfo[]>([])
const fillers = ref<FillerInfo[]>([])

// Calculate total weight percentage
const totalWeightPercentage = computed(() => {
  return tableData.value.reduce((sum, item) => sum + (Number(item.WeightPercent) || 0), 0)
})

// Dialog
const dialogVisible = ref(false)
const dialogTitle = ref('Add Component')
const formRef = ref<FormInstance>()
const submitLoading = ref(false)

interface FormData {
  CompositionID?: number
  componentType: 'material' | 'filler'
  MaterialID_FK?: number
  FillerID_FK?: number
  WeightPercent?: number
  AdditionMethod?: string
  Remark?: string
}

const formData = reactive<FormData>({
  componentType: 'material',
  WeightPercent: undefined,
  AdditionMethod: '',
  Remark: '',
})

const formRules = {
  componentType: [{ required: true, message: 'Please select component type', trigger: 'change' }],
  MaterialID_FK: [{ required: true, message: 'Please select material', trigger: 'change' }],
  FillerID_FK: [{ required: true, message: 'Please select filler', trigger: 'change' }],
  WeightPercent: [
    { required: true, message: 'Please enter weight percentage', trigger: 'blur' },
    { type: 'number', min: 0, max: 100, message: 'Weight percentage should be between 0-100', trigger: 'blur' }
  ] as any,
}

// Search projects by keyword (remote search)
async function searchProjects(query: string) {
  if (!query || query.trim() === '') {
    // If empty, load first 50 projects as default
    await loadDefaultProjects()
    return
  }
  
  projectsLoading.value = true
  try {
    const res = await getProjectListApi({ 
      page: 1, 
      page_size: 50,
      keyword: query  // Search by keyword (project name or formula code)
    })
    projects.value = res.items || []
  } catch (error) {
    console.error('Failed to search projects:', error)
    ElMessage.error('Failed to search projects')
  } finally {
    projectsLoading.value = false
  }
}

// Load default projects (first 50)
async function loadDefaultProjects() {
  projectsLoading.value = true
  try {
    const res = await getProjectListApi({ 
      page: 1, 
      page_size: 50
    })
    projects.value = res.items || []
  } catch (error) {
    console.error('Failed to get project list:', error)
  } finally {
    projectsLoading.value = false
  }
}

// Get materials and fillers list
async function getMaterialsAndFillers() {
  try {
    const [materialsRes, fillersRes] = await Promise.all([
      getMaterialListApi({ page: 1, page_size: 100 }),
      getFillerListApi({ page: 1, page_size: 100 })
    ])
    materials.value = materialsRes.items || []
    fillers.value = fillersRes.items || []
  } catch (error) {
    console.error('Failed to get materials/fillers list:', error)
  }
}

// Project change
async function handleProjectChange() {
  if (queryParams.project_id) {
    await loadProjectInfo()
    await loadCompositions()
  } else {
    currentProject.value = null
    tableData.value = []
  }
}

// Load project info
async function loadProjectInfo() {
  if (!queryParams.project_id) return
  try {
    currentProject.value = await getProjectDetailApi(queryParams.project_id)
  } catch (error) {
    console.error('Failed to get project info:', error)
  }
}

// Load formula compositions
async function loadCompositions() {
  if (!queryParams.project_id) return
  loading.value = true
  try {
    const res = await getCompositionListApi(queryParams.project_id)
    tableData.value = Array.isArray(res) ? res : []
  } catch (error) {
    ElMessage.error('Failed to get formula compositions')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// Reset
function handleReset() {
  queryParams.project_id = undefined
  currentProject.value = null
  tableData.value = []
}

// Selection change
function handleSelectionChange(selection: FormulaComposition[]) {
  selectedRows.value = selection
}

// Add
function handleAdd() {
  if (!queryParams.project_id) {
    ElMessage.warning('Please select a project first')
    return
  }
  dialogTitle.value = 'Add Component'
  dialogVisible.value = true
}

// Edit
function handleEdit(row: FormulaComposition) {
  dialogTitle.value = 'Edit Component'
  Object.assign(formData, {
    CompositionID: row.CompositionID,
    componentType: row.MaterialID_FK ? 'material' : 'filler',
    MaterialID_FK: row.MaterialID_FK,
    FillerID_FK: row.FillerID_FK,
    WeightPercent: row.WeightPercent,
    AdditionMethod: row.AdditionMethod,
    Remark: row.Remark,
  })
  dialogVisible.value = true
}

// Delete
function handleDelete(row: FormulaComposition) {
  ElMessageBox.confirm('Are you sure you want to delete this component?', 'Confirm', {
    confirmButtonText: 'Confirm',
    cancelButtonText: 'Cancel',
    type: 'warning',
  }).then(async () => {
    try {
      await deleteCompositionApi(row.CompositionID)
      ElMessage.success('Deleted successfully')
      loadCompositions()
    } catch (error) {
      ElMessage.error('Failed to delete')
    }
  })
}

// Batch delete
function handleBatchDelete() {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('Please select data to delete')
    return
  }
  ElMessageBox.confirm(`Are you sure you want to delete ${selectedRows.value.length} selected items?`, 'Confirm', {
    confirmButtonText: 'Confirm',
    cancelButtonText: 'Cancel',
    type: 'warning',
  }).then(async () => {
    try {
      await Promise.all(selectedRows.value.map(row => deleteCompositionApi(row.CompositionID)))
      ElMessage.success('Deleted successfully')
      loadCompositions()
    } catch (error) {
      ElMessage.error('Failed to delete')
    }
  })
}

// Submit form
async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        const data: any = {
          project_id: queryParams.project_id,
          weight_percentage: formData.WeightPercent,
          addition_method: formData.AdditionMethod,
          remarks: formData.Remark,
        }

        if (formData.componentType === 'material') {
          data.material_id = formData.MaterialID_FK
        } else {
          data.filler_id = formData.FillerID_FK
        }

        if (formData.CompositionID) {
          await updateCompositionApi(formData.CompositionID, data)
          ElMessage.success('Updated successfully')
        } else {
          await createCompositionApi(data)
          ElMessage.success('Added successfully')
        }
        dialogVisible.value = false
        loadCompositions()
      } catch (error) {
        ElMessage.error(formData.CompositionID ? 'Failed to update' : 'Failed to add')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

// Close dialog
function handleDialogClose() {
  formRef.value?.resetFields()
  Object.assign(formData, {
    componentType: 'material',
    WeightPercent: undefined,
    AdditionMethod: '',
    Remark: '',
  })
}

onMounted(() => {
  loadDefaultProjects()  // Load first 50 projects by default
  getMaterialsAndFillers()
})
</script>

<style scoped lang="scss">
.formula-container {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .search-form {
    margin-bottom: 16px;
  }

  .toolbar {
    margin-bottom: 16px;
  }

  .composition-summary {
    margin-top: 16px;
    padding: 12px;
    background-color: #f5f7fa;
    border-radius: 4px;
    display: flex;
    gap: 12px;
  }
}
</style>
