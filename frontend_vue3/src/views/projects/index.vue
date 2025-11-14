<template>
  <div class="projects-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>Projects Management</span>
        </div>
      </template>

      <!-- Search Bar -->
      <el-form :model="table.queryParams" inline class="search-form">
        <el-form-item label="Keyword">
          <el-input
            v-model="table.queryParams.keyword"
            placeholder="Enter project name or formula code"
            clearable
            style="width: 200px"
            @keyup.enter="table.handleQuery"
          />
        </el-form-item>
        <el-form-item label="Project Type">
          <el-select
            v-model="table.queryParams.project_type"
            placeholder="Select project type"
            clearable
            style="width: 150px"
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
            v-model="table.queryParams.formulator"
            placeholder="Select formulator"
            clearable
            filterable
            style="width: 150px"
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
          <el-button type="primary" @click="table.handleQuery">Search</el-button>
          <el-button @click="handleReset">Reset</el-button>
        </el-form-item>
      </el-form>

      <!-- Toolbar -->
      <div class="toolbar">
        <el-button type="success" :icon="Plus" @click="crud.handleAdd()">Create</el-button>
        
        <!-- Export Buttons -->
        <ExportDropdown
          label="Export All"
          type="warning"
          :loading="exportHelper.exportLoading.value"
          @export="exportHelper.handleExport"
        />
        <ExportDropdown
          label="Export Selected"
          type="info"
          :disabled="!hasSelection"
          @export="handleExportSelected"
        >
          <template v-if="hasSelection">
            ({{ table.selectedRows.value.length }})
          </template>
        </ExportDropdown>
      </div>

      <!-- Table -->
      <el-table 
        v-loading="table.loading.value" 
        :data="table.tableData.value" 
        border 
        stripe 
        style="width: 100%"
        @selection-change="table.handleSelectionChange"
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
            <el-button type="primary" size="small" @click="crud.handleEdit(row)">Edit</el-button>
            <el-button type="danger" size="small" @click="crud.handleDelete(row, 'ProjectID' as any)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <Pagination
        v-show="table.total.value > 0"
        :total="table.total.value"
        v-model:page="table.queryParams.page"
        v-model:limit="table.queryParams.page_size"
        @pagination="table.fetchData"
      />
    </el-card>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="crud.dialogVisible.value"
      :title="crud.dialogTitle.value"
      width="600px"
      @close="crud.handleDialogClose"
    >
      <el-form :ref="(el: any) => crud.formRef.value = el" :model="crud.formData" :rules="formRules" label-width="180px">
        <el-form-item label="Project Name" prop="ProjectName">
          <el-input v-model="crud.formData.ProjectName" placeholder="Enter project name" />
        </el-form-item>
        <el-form-item label="Project Type" prop="ProjectType_FK">
          <el-select v-model="crud.formData.ProjectType_FK" placeholder="Select project type" style="width: 100%">
            <el-option
              v-for="type in projectTypes"
              :key="type.TypeID"
              :label="type.TypeName"
              :value="type.TypeID"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Formulator Name" prop="FormulatorName">
          <el-input v-model="crud.formData.FormulatorName" placeholder="Enter formulator name" />
        </el-form-item>
        <el-form-item label="Formulation Date" prop="FormulationDate">
          <el-date-picker
            v-model="crud.formData.FormulationDate"
            type="date"
            placeholder="Select date"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="Substrate Application">
          <el-input
            v-model="crud.formData.SubstrateApplication"
            type="textarea"
            :rows="3"
            placeholder="Enter substrate application"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="crud.dialogVisible.value = false">Cancel</el-button>
        <el-button type="primary" :loading="crud.submitLoading.value" @click="crud.handleSubmit()">Confirm</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Plus } from '@element-plus/icons-vue'
import { 
  getProjectListApi, 
  createProjectApi, 
  updateProjectApi, 
  deleteProjectApi, 
  getProjectTypesApi,
  getFormulatorsApi,
  type ProjectInfo
  // type ProjectType
} from '@/api/projects'
import Pagination from '@/components/Pagination.vue'
import ExportDropdown from '@/components/ExportDropdown/index.vue'
import { useTable } from '@/composables/useTable'
import { useCRUD } from '@/composables/useCRUD'
import { useExport } from '@/composables/useExport'
import request from '@/utils/request'
import {
  projectNameRules,
  formulatorNameRules,
  createSelectRequiredRule,
  createDateRequiredRule,
} from '@/utils/validators'

const router = useRouter()

// ==================== 表格管理 ====================
const table = useTable(getProjectListApi, { 
  defaultPageSize: 20
})

// 扩展查询参数
Object.assign(table.queryParams, {
  project_type: '',
  formulator: ''
})

const hasSelection = computed(() => table.selectedRows.value.length > 0)

// ==================== CRUD 管理 ====================
const crud = useCRUD({
  createApi: createProjectApi,
  updateApi: updateProjectApi as any,
  deleteApi: deleteProjectApi as any,
  idKey: 'ProjectID',
  resourceName: 'Project',
  onSuccess: () => table.fetchData(),
  transformRequestData: (formData: any) => ({
    project_name: formData.ProjectName,
    project_type_fk: formData.ProjectType_FK,
    formulator_name: formData.FormulatorName,
    formulation_date: formData.FormulationDate,
    substrate_application: formData.SubstrateApplication,
  }),
  defaultFormData: {
    ProjectName: '',
    ProjectType_FK: undefined,
    FormulatorName: '',
    FormulationDate: '',
    SubstrateApplication: '',
  }
})

const formRules = {
  ProjectName: projectNameRules,
  ProjectType_FK: [createSelectRequiredRule('project type')],
  FormulatorName: formulatorNameRules,
  FormulationDate: [createDateRequiredRule('formulation date')],
}

// ==================== 导出管理 ====================
const exportHelper = useExport({
  exportApi: async (format: string, _params: any) => {
    const queryString = new URLSearchParams({
      format,
      ...(table.queryParams.project_type && { project_type: table.queryParams.project_type }),
      ...(table.queryParams.formulator && { formulator: table.queryParams.formulator }),
      ...(table.queryParams.keyword && { keyword: table.queryParams.keyword })
    }).toString()
    
    return await request.get(`/api/v1/projects/export?${queryString}`, {
      responseType: 'blob'
    })
  },
  resourceName: 'Projects'
})

function handleExportSelected(format: string) {
  if (format === 'image') {
    exportHelper.handleBatchExportImages(
      table.selectedRows.value as any
    )
  } else {
    exportHelper.handleExportSelected(
      format,
      table.selectedRows.value,
      [
        { key: 'ProjectID', label: 'Project ID' },
        { key: 'ProjectName', label: 'Project Name' },
        { key: 'FormulaCode', label: 'Formula Code' },
        { key: 'TypeName', label: 'Project Type' },
        { key: 'FormulatorName', label: 'Formulator' },
        { key: 'SubstrateApplication', label: 'Substrate Application' },
        { key: 'FormulationDate', label: 'Formulation Date' }
      ]
    )
  }
}

// ==================== 业务逻辑 ====================
const projectTypes = ref<any[]>([])
const formulators = ref<string[]>([])

async function getProjectTypes() {
  try {
    const res = await getProjectTypesApi()
    projectTypes.value = Array.isArray(res) ? res : (res.data || [])
  } catch (error) {
    console.error('Failed to get project types:', error)
  }
}

async function getFormulators() {
  try {
    const res = await getFormulatorsApi()
    formulators.value = Array.isArray(res) ? res : (res.data || [])
  } catch (error) {
    console.error('Failed to get formulators list:', error)
  }
}

function handleViewDetail(row: ProjectInfo) {
  router.push({
    name: 'ProjectDetail',
    params: { id: row.ProjectID }
  })
}

// 自定义重置逻辑
function handleReset() {
  table.queryParams.keyword = ''
  table.queryParams.project_type = ''
  table.queryParams.formulator = ''
  table.handleReset()
}

// ==================== 初始化 ====================
onMounted(() => {
  table.fetchData()
  getProjectTypes()
  getFormulators()
})
</script>

<style scoped lang="scss">
.projects-container {
  height: 100%;
}

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
  display: flex;
  gap: 8px;
}
</style>

