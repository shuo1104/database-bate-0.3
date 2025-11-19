<template>
  <div class="fillers-container">
    <el-card shadow="never">
      <!-- Search Bar -->
      <el-form :model="queryParams" inline>
        <el-form-item label="Keyword">
          <el-input
            v-model="queryParams.keyword"
            placeholder="Enter trade name"
            clearable
            @clear="handleQuery"
          />
        </el-form-item>
        <el-form-item label="Supplier">
          <el-input
            v-model="queryParams.supplier"
            placeholder="Enter supplier"
            clearable
            @clear="handleQuery"
          />
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
        <el-table-column prop="FillerID" label="ID" width="80" />
        <el-table-column prop="TradeName" label="Trade Name" min-width="150" />
        <el-table-column prop="FillerTypeName" label="Filler Type" width="120" />
        <el-table-column prop="Supplier" label="Supplier" min-width="150" />
            <el-table-column prop="ParticleSize" label="Particle Size" width="120" />
            <el-table-column label="Silanized" width="110">
              <template #default="{ row }">
                <el-tag v-if="row.IsSilanized === 1" type="success">Yes</el-tag>
                <el-tag v-else-if="row.IsSilanized === 0" type="info">No</el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="CouplingAgent" label="Coupling Agent" min-width="120" show-overflow-tooltip />
            <el-table-column prop="SurfaceArea" label="Surface Area" width="110" />
        <el-table-column label="Actions" width="180" fixed="right">
          <template #default="{ row }">
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
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="150px">
        <el-form-item label="Trade Name" prop="TradeName">
          <el-input v-model="formData.TradeName" placeholder="Enter trade name" />
        </el-form-item>
        <el-form-item label="Filler Type" prop="FillerType_FK">
          <el-select v-model="formData.FillerType_FK" placeholder="Select filler type" style="width: 100%">
            <el-option
              v-for="type in fillerTypes"
              :key="type.FillerTypeID"
              :label="type.FillerTypeName"
              :value="type.FillerTypeID"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Supplier">
          <el-input v-model="formData.Supplier" placeholder="Enter supplier" />
        </el-form-item>
        <el-form-item label="Particle Size (D50)">
          <el-input v-model="formData.ParticleSize" placeholder="e.g. 10-20nm" />
        </el-form-item>
        <el-form-item label="Silanized">
          <el-radio-group v-model="formData.IsSilanized">
            <el-radio :label="1">Yes</el-radio>
            <el-radio :label="0">No</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Coupling Agent">
          <el-input v-model="formData.CouplingAgent" placeholder="Enter coupling agent" />
        </el-form-item>
        <el-form-item label="Surface Area (m²/g)">
          <el-input-number 
            v-model.number="formData.SurfaceArea" 
            placeholder="Enter surface area" 
            :precision="4"
            :step="0.01"
            style="width: 100%"
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import {
  getFillerListApi,
  createFillerApi,
  updateFillerApi,
  deleteFillerApi,
  getFillerTypesApi,
  type FillerInfo,
  type FillerType
} from '@/api/fillers'
import Pagination from '@/components/Pagination.vue'
import request from '@/utils/request'

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref<FillerInfo[]>([])
const total = ref(0)
const selectedRows = ref<FillerInfo[]>([])
const fillerTypes = ref<FillerType[]>([])

const queryParams = reactive({
  page: 1,
  page_size: 20,
  keyword: '',
  supplier: '',
})

const dialogVisible = ref(false)
const dialogTitle = ref('Create Filler')
const formRef = ref<FormInstance>()
const formData = reactive<Partial<FillerInfo>>({
  TradeName: '',
  FillerType_FK: undefined,
  Supplier: '',
  ParticleSize: '',
  IsSilanized: 0,
  CouplingAgent: '',
  SurfaceArea: undefined,
})

const formRules = {
  TradeName: [{ required: true, message: 'Please enter trade name', trigger: 'blur' }],
  FillerType_FK: [{ required: true, message: 'Please select filler type', trigger: 'change' }],
}

// Get filler types list
async function getFillerTypes() {
  try {
    fillerTypes.value = await getFillerTypesApi()
  } catch (error) {
    console.error('Failed to get filler types:', error)
  }
}

// Get list
async function getList() {
  loading.value = true
  try {
    const res = await getFillerListApi(queryParams)
      tableData.value = res.items || []
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
  queryParams.supplier = ''
  getList()
}

// Create
function handleCreate() {
  dialogTitle.value = 'Create Filler'
  dialogVisible.value = true
}

// Edit
function handleEdit(row: FillerInfo) {
  dialogTitle.value = 'Edit Filler'
  // 转换数值类型字段，避免类型警告
  Object.assign(formData, {
    ...row,
    SurfaceArea: row.SurfaceArea ? Number(row.SurfaceArea) : undefined,
  })
  dialogVisible.value = true
}

// 删除
function handleDelete(row: FillerInfo) {
  ElMessageBox.confirm('Are you sure you want to delete this filler?', 'Confirm', {
    confirmButtonText: 'Confirm',
    cancelButtonText: 'Cancel',
    type: 'warning',
  }).then(async () => {
    try {
      await deleteFillerApi(row.FillerID)
      ElMessage.success('删除成功')
      getList()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
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
          trade_name: formData.TradeName,
          filler_type_fk: formData.FillerType_FK,
          supplier: formData.Supplier,
          particle_size: formData.ParticleSize,
          is_silanized: formData.IsSilanized,
          coupling_agent: formData.CouplingAgent,
          surface_area: formData.SurfaceArea ? Number(formData.SurfaceArea) : undefined,
        }

        if (formData.FillerID) {
          await updateFillerApi(formData.FillerID, requestData)
          ElMessage.success('Updated successfully')
        } else {
          await createFillerApi(requestData)
          ElMessage.success('Created successfully')
        }
        dialogVisible.value = false
        getList()
      } catch (error) {
        ElMessage.error(formData.FillerID ? 'Failed to update' : 'Failed to create')
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
    FillerID: undefined,  // 清除FillerID，确保下次创建时不会误用
    TradeName: '',
    FillerType_FK: undefined,
    Supplier: '',
    ParticleSize: '',
    IsSilanized: 0,
    CouplingAgent: '',
    SurfaceArea: undefined,
  })
}

// Handle selection change
function handleSelectionChange(selection: FillerInfo[]) {
  selectedRows.value = selection
}

// Export all data
async function handleExport(format: string) {
  try {
    const params = new URLSearchParams({
      format,
      ...(queryParams.TradeName && { keyword: queryParams.TradeName }),
      ...(queryParams.Supplier && { supplier: queryParams.Supplier })
    })
    
    const response = await request.get(`/api/v1/fillers/export?${params.toString()}`, {
      responseType: 'blob'
    })
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `fillers_all_${Date.now()}.${format}`)
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
  if (selectedRows.value.length === 0) {
    ElMessage.warning('Please select data to export first')
    return
  }

  try {
    // Prepare CSV/TXT content
    const columns = ['Filler ID', 'Trade Name', 'Filler Type', 'Supplier', 'Particle Size', 'Silanized', 'Coupling Agent', 'Surface Area']
    let content = ''
    const separator = format === 'csv' ? ',' : '\t'
    
    // Add header
    content = columns.join(separator) + '\n'
    
    // Add data rows
    selectedRows.value.forEach(row => {
      const values = [
        row.FillerID,
        row.TradeName,
        row.FillerTypeName || '',
        row.Supplier || '',
        row.ParticleSize || '',
        row.IsSilanized ? 'Yes' : 'No',
        row.CouplingAgent || '',
        row.SurfaceArea || ''
      ]
      content += values.join(separator) + '\n'
    })
    
    // Create Blob and download
    const blob = new Blob(['\ufeff' + content], { type: format === 'csv' ? 'text/csv;charset=utf-8' : 'text/plain;charset=utf-8' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `fillers_selected_${Date.now()}.${format}`)
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
  getFillerTypes()
  getList()
})
</script>

<style scoped lang="scss">
.fillers-container {
  height: 100%;
}
</style>

