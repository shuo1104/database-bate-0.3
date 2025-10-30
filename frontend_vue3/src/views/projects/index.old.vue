<template>
  <div class="projects-container">
    <el-card shadow="never">
      <!-- Search Bar -->
      <el-form :model="queryParams" inline>
        <el-form-item label="Keyword">
          <el-input
            v-model="queryParams.keyword"
            placeholder="Enter project name or formula code"
            clearable
            style="width: 200px"
            @clear="handleQuery"
          />
        </el-form-item>
        <el-form-item label="Project Type">
          <el-select
            v-model="queryParams.project_type"
            placeholder="Select project type"
            clearable
            style="width: 150px"
            @change="handleQuery"
            @clear="handleQuery"
          >
            <el-option
              v-for="item in projectTypes"
              :key="item.TypeID"
              :label="item.TypeName"
              :value="item.TypeName"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Formulator">
          <el-select
            v-model="queryParams.formulator"
            placeholder="Select formulator"
            clearable
            filterable
            style="width: 150px"
            @change="handleQuery"
            @clear="handleQuery"
          >
            <el-option
              v-for="item in formulators"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">Search</el-button>
          <el-button @click="handleReset">Reset</el-button>
          <el-button type="success" @click="handleCreate">Create</el-button>
          <el-dropdown @command="handleExport" style="margin-left: 10px">
            <el-button type="warning">
              Export All<el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="csv">Export as CSV</el-dropdown-item>
                <el-dropdown-item command="txt">Export as TXT</el-dropdown-item>
                <el-dropdown-item command="image" divided>Export Image Report</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-dropdown @command="handleExportSelected" style="margin-left: 10px" :disabled="selectedRows.length === 0">
            <el-button type="info" :disabled="selectedRows.length === 0">
              Export Selected ({{ selectedRows.length }})<el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="csv">Export as CSV</el-dropdown-item>
                <el-dropdown-item command="txt">Export as TXT</el-dropdown-item>
                <el-dropdown-item command="image" divided>Export Image Report</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-form-item>
      </el-form>

      <!-- Table -->
      <el-table 
        v-loading="loading" 
        :data="tableData" 
        border 
        stripe 
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="ProjectID" label="ID" width="80" />
        <el-table-column prop="ProjectName" label="Project Name" min-width="150" />
        <el-table-column prop="FormulaCode" label="Formula Code" min-width="180" />
        <el-table-column prop="TypeName" label="Project Type" width="120" />
        <el-table-column prop="FormulatorName" label="Formulator" width="120" />
        <el-table-column prop="SubstrateApplication" label="Substrate Application" min-width="150" />
        <el-table-column prop="FormulationDate" label="Formulation Date" width="120" />
        <el-table-column label="Actions" width="260" fixed="right">
          <template #default="{ row }">
            <el-button type="info" size="small" @click="handleViewDetail(row)">Detail</el-button>
            <el-button type="primary" size="small" @click="handleEdit(row)">Edit</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <Pagination
        v-show="total > 0"
        :total="total"
        v-model:page="queryParams.page"
        v-model:limit="queryParams.page_size"
        @pagination="getList"
      />
    </el-card>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="160px">
        <el-form-item label="Project Name" prop="ProjectName">
          <el-input v-model="formData.ProjectName" placeholder="Enter project name" />
        </el-form-item>
        <el-form-item label="Project Type" prop="ProjectType_FK">
          <el-select v-model="formData.ProjectType_FK" placeholder="Select project type" style="width: 100%">
            <el-option
              v-for="type in projectTypes"
              :key="type.TypeID"
              :label="type.TypeName"
              :value="type.TypeID"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Formulator" prop="FormulatorName">
          <el-input v-model="formData.FormulatorName" placeholder="Enter formulator name" />
        </el-form-item>
        <el-form-item label="Formulation Date" prop="FormulationDate">
          <el-date-picker
            v-model="formData.FormulationDate"
            type="date"
            placeholder="Select formulation date"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="Substrate/Application" prop="SubstrateApplication">
          <el-input v-model="formData.SubstrateApplication" placeholder="Enter substrate or application" />
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
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import { getProjectListApi, createProjectApi, updateProjectApi, deleteProjectApi, getProjectTypesApi, getFormulatorsApi, exportProjectImageApi, type ProjectInfo } from '@/api/projects'
import { formatDateTime } from '@/utils/common'
import Pagination from '@/components/Pagination.vue'
import request from '@/utils/request'

const router = useRouter()

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref<ProjectInfo[]>([])
const total = ref(0)
const selectedRows = ref<ProjectInfo[]>([])

const queryParams = reactive({
  page: 1,
  page_size: 20,
  keyword: '',
  project_type: '',
  formulator: '',
})

const dialogVisible = ref(false)
const dialogTitle = ref('Create Project')
const formRef = ref<FormInstance>()
const formData = reactive<Partial<ProjectInfo>>({
  ProjectName: '',
  ProjectType_FK: undefined,
  FormulatorName: '',
  FormulationDate: '',
  SubstrateApplication: '',
})

const formRules = {
  ProjectName: [{ required: true, message: 'Please enter project name', trigger: 'blur' }],
  ProjectType_FK: [{ required: true, message: 'Please select project type', trigger: 'change' }],
  FormulatorName: [{ required: true, message: 'Please enter formulator name', trigger: 'blur' }],
  FormulationDate: [{ required: true, message: 'Please select formulation date', trigger: 'change' }],
}

// Project types and formulators lists
const projectTypes = ref<any[]>([])
const formulators = ref<string[]>([])

// Get list
async function getList() {
  loading.value = true
  try {
    const res = await getProjectListApi(queryParams)
    // Backend returns 'list' instead of 'items'
    tableData.value = res.list || res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('Get list error:', error)
    ElMessage.error('Failed to get list')
  } finally {
    loading.value = false
  }
}

// Query
function handleQuery() {
  queryParams.page = 1
  getList()
}

// Reset
function handleReset() {
  queryParams.page = 1
  queryParams.keyword = ''
  queryParams.project_type = ''
  queryParams.formulator = ''
  getList()
}

// View detail
function handleViewDetail(row: ProjectInfo) {
  router.push(`/projects/${row.ProjectID}`)
}

// Create
function handleCreate() {
  dialogTitle.value = 'Create Project'
  dialogVisible.value = true
}

// Edit
function handleEdit(row: ProjectInfo) {
  dialogTitle.value = 'Edit Project'
  Object.assign(formData, row)
  dialogVisible.value = true
}

// Delete
function handleDelete(row: ProjectInfo) {
  ElMessageBox.confirm('Are you sure you want to delete this project?', 'Confirm', {
    confirmButtonText: 'Confirm',
    cancelButtonText: 'Cancel',
    type: 'warning',
  }).then(async () => {
    try {
      await deleteProjectApi(row.ProjectID)
      ElMessage.success('Deleted successfully')
      getList()
    } catch (error) {
      ElMessage.error('Failed to delete')
    }
  })
}

// Export image report
async function handleExportImage(row: any) {
  row.exportLoading = true
  try {
    const blob = await exportProjectImageApi(row.ProjectID)
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([blob]))
    const link = document.createElement('a')
    link.href = url
    const timestamp = new Date().getTime()
    link.setAttribute('download', `project_${row.ProjectID}_report_${timestamp}.png`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success(`Image report for project ${row.ProjectName} exported successfully`)
  } catch (error: any) {
    console.error('Export image report failed:', error)
    ElMessage.error(`Failed to export image report for project ${row.ProjectName}`)
  } finally {
    row.exportLoading = false
  }
}

// Submit
async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        // Convert field names to backend format
        const requestData: any = {
          project_name: formData.ProjectName,
          project_type_fk: formData.ProjectType_FK,
          formulator_name: formData.FormulatorName,
          formulation_date: formData.FormulationDate,
          substrate_application: formData.SubstrateApplication,
        }

        if (formData.ProjectID) {
          await updateProjectApi(formData.ProjectID, requestData)
          ElMessage.success('Updated successfully')
        } else {
          await createProjectApi(requestData)
          ElMessage.success('Created successfully')
        }
        dialogVisible.value = false
        getList()
      } catch (error) {
        ElMessage.error(formData.ProjectID ? 'Failed to update' : 'Failed to create')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

// Get project types list
async function getProjectTypes() {
  try {
    const types = await getProjectTypesApi()
    projectTypes.value = types || []
  } catch (error) {
    console.error('Failed to get project types:', error)
  }
}

// Get formulators list
async function getFormulators() {
  try {
    const res = await getFormulatorsApi()
    formulators.value = res || []
  } catch (error) {
    console.error('Failed to get formulators list:', error)
  }
}

// Close dialog
function handleDialogClose() {
  formRef.value?.resetFields()
  Object.assign(formData, {
    ProjectID: undefined,  // 清除ProjectID，确保下次创建时不会误用
    ProjectName: '',
    ProjectType_FK: undefined,
    FormulatorName: '',
    FormulationDate: '',
    SubstrateApplication: '',
  })
}

// Handle selection change
function handleSelectionChange(selection: ProjectInfo[]) {
  selectedRows.value = selection
}

// Export all data
async function handleExport(format: string) {
  if (format === 'image') {
    ElMessage.warning('Image reports only support single project export, please export from detail page or actions column')
    return
  }
  try {
    const params = new URLSearchParams({
      format,
      ...(queryParams.keyword && { keyword: queryParams.keyword }),
      ...(queryParams.project_type && { project_type: queryParams.project_type }),
      ...(queryParams.formulator && { formulator: queryParams.formulator })
    })
    
    const response = await request.get(`/api/v1/projects/export?${params.toString()}`, {
      responseType: 'blob'
    })
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `projects_all_${Date.now()}.${format}`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('Exported successfully')
  } catch (error) {
    ElMessage.error('Failed to export')
    console.error('Export failed:', error)
  }
}

// Export selected data
async function handleExportSelected(format: string) {
  if (selectedRows.value.length === 0 && format !== 'image') {
    ElMessage.warning('Please select data to export first')
    return
  }

  if (format === 'image') {
    if (selectedRows.value.length === 0) {
      ElMessage.warning('Please select projects to export image reports')
      return
    }
    if (selectedRows.value.length > 5) {
      ElMessage.warning('Maximum 5 projects can be exported at once')
      return
    }
    
    // Export images one by one
    for (const row of selectedRows.value) {
      await handleExportImage(row)
    }
    return
  }

  try {
    // Prepare CSV/TXT content
    const columns = ['Project ID', 'Project Name', 'Project Type', 'Formula Code', 'Formulator', 'Formulation Date', 'Substrate', 'Created Time']
    let content = ''
    const separator = format === 'csv' ? ',' : '\t'
    
    // Add header
    content = columns.join(separator) + '\n'
    
    // Add data rows
    selectedRows.value.forEach(row => {
      const values = [
        row.ProjectID,
        row.ProjectName,
        row.TypeName || '',
        row.FormulaCode || '',
        row.FormulatorName || '',
        row.FormulationDate || '',
        row.SubstrateApplication || '',
        formatDateTime(row.CreatedAt) || ''
      ]
      content += values.join(separator) + '\n'
    })
    
    // Create Blob and download
    const blob = new Blob(['\ufeff' + content], { type: format === 'csv' ? 'text/csv;charset=utf-8' : 'text/plain;charset=utf-8' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `projects_selected_${Date.now()}.${format}`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success(`Exported ${selectedRows.value.length} records`)
  } catch (error) {
    ElMessage.error('Failed to export')
    console.error('Export failed:', error)
  }
}

onMounted(() => {
  getList()
  getProjectTypes()
  getFormulators()
})
</script>

<style scoped lang="scss">
.projects-container {
  height: 100%;
}
</style>

