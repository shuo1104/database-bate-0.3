<template>
  <div class="materials-container">
    <el-card shadow="never">
      <!-- Search Bar -->
      <el-form :model="queryParams" inline>
        <el-form-item label="Keyword">
          <el-input
            v-model="queryParams.keyword"
            placeholder="Enter trade name or CAS number"
            clearable
            @clear="handleQuery"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="Category">
          <el-select
            v-model="queryParams.category"
            placeholder="Select category"
            clearable
            @change="handleQuery"
            @clear="handleQuery"
            style="width: 150px"
          >
            <el-option
              v-for="item in categories"
              :key="item.CategoryID"
              :label="item.CategoryName"
              :value="item.CategoryName"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Supplier">
          <el-input
            v-model="queryParams.supplier"
            placeholder="Enter supplier"
            clearable
            @clear="handleQuery"
            style="width: 150px"
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
        <el-table-column prop="MaterialID" label="ID" width="80" />
        <el-table-column prop="TradeName" label="Trade Name" min-width="150" />
        <el-table-column prop="CategoryName" label="Category" width="120" />
        <el-table-column prop="CAS_Number" label="CAS Number" width="120" />
        <el-table-column prop="Supplier" label="Supplier" width="120" />
        <el-table-column prop="Density" label="Density" width="100">
          <template #default="{ row }">
            {{ row.Density ? Number(row.Density).toFixed(4) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="Viscosity" label="Viscosity" width="100">
          <template #default="{ row }">
            {{ row.Viscosity ? Number(row.Viscosity).toFixed(2) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="FunctionDescription" label="Function Description" min-width="150" />
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
        <el-form-item label="Category">
          <el-select
            v-model="formData.Category_FK"
            placeholder="Select category"
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="item in categories"
              :key="item.CategoryID"
              :label="item.CategoryName"
              :value="item.CategoryID"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="CAS Number">
          <el-input v-model="formData.CAS_Number" placeholder="Enter CAS number" />
        </el-form-item>
        <el-form-item label="Supplier">
          <el-input v-model="formData.Supplier" placeholder="Enter supplier" />
        </el-form-item>
        <el-form-item label="Density">
          <el-input v-model="formData.Density" type="number" placeholder="Enter density" />
        </el-form-item>
        <el-form-item label="Viscosity">
          <el-input v-model="formData.Viscosity" type="number" placeholder="Enter viscosity" />
        </el-form-item>
        <el-form-item label="Function Description">
          <el-input
            v-model="formData.FunctionDescription"
            type="textarea"
            :rows="3"
            placeholder="Enter function description"
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
  getMaterialListApi, 
  createMaterialApi, 
  updateMaterialApi, 
  deleteMaterialApi, 
  getMaterialCategoriesApi,
  type MaterialInfo,
  type MaterialCategory
} from '@/api/materials'
import { formatDateTime } from '@/utils/common'
import Pagination from '@/components/Pagination.vue'
import request from '@/utils/request'

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref<MaterialInfo[]>([])
const total = ref(0)
const selectedRows = ref<MaterialInfo[]>([])
const categories = ref<MaterialCategory[]>([])

const queryParams = reactive({
  page: 1,
  page_size: 20,
  keyword: '',
  category: '',
  supplier: '',
})

const dialogVisible = ref(false)
const dialogTitle = ref('Create Material')
const formRef = ref<FormInstance>()
const formData = reactive<Partial<MaterialInfo>>({
  TradeName: '',
  Category_FK: undefined,
  CAS_Number: '',
  Supplier: '',
  Density: undefined,
  Viscosity: undefined,
  FunctionDescription: '',
})

const formRules = {
  TradeName: [{ required: true, message: 'Please enter trade name', trigger: 'blur' }],
}

async function getList() {
  loading.value = true
  try {
    const res = await getMaterialListApi(queryParams)
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

function handleQuery() {
  queryParams.page = 1
  getList()
}

function handleReset() {
  queryParams.page = 1
  queryParams.keyword = ''
  queryParams.category = ''
  queryParams.supplier = ''
  getList()
}

function handleCreate() {
  dialogTitle.value = 'Create Material'
  dialogVisible.value = true
}

function handleEdit(row: MaterialInfo) {
  dialogTitle.value = 'Edit Material'
  // 转换数值类型字段，避免类型警告
  Object.assign(formData, {
    ...row,
    Density: row.Density ? Number(row.Density) : undefined,
    Viscosity: row.Viscosity ? Number(row.Viscosity) : undefined,
  })
  dialogVisible.value = true
}

function handleDelete(row: MaterialInfo) {
  ElMessageBox.confirm('Are you sure you want to delete this material?', 'Confirm', {
    confirmButtonText: 'Confirm',
    cancelButtonText: 'Cancel',
    type: 'warning',
  }).then(async () => {
    try {
      await deleteMaterialApi(row.MaterialID)
      ElMessage.success('Deleted successfully')
      getList()
    } catch (error) {
      ElMessage.error('Failed to delete')
    }
  })
}

async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        // Convert field names to backend format
        const requestData: any = {
          trade_name: formData.TradeName,
          category_fk: formData.Category_FK,
          cas_number: formData.CAS_Number,
          supplier: formData.Supplier,
          density: formData.Density ? Number(formData.Density) : undefined,
          viscosity: formData.Viscosity ? Number(formData.Viscosity) : undefined,
          function_description: formData.FunctionDescription,
        }

        if (formData.MaterialID) {
          await updateMaterialApi(formData.MaterialID, requestData)
          ElMessage.success('Updated successfully')
        } else {
          await createMaterialApi(requestData)
          ElMessage.success('Created successfully')
        }
        dialogVisible.value = false
        getList()
      } catch (error) {
        ElMessage.error(formData.MaterialID ? 'Failed to update' : 'Failed to create')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

function handleDialogClose() {
  formRef.value?.resetFields()
  Object.assign(formData, {
    MaterialID: undefined,  // 清除MaterialID，确保下次创建时不会误用
    TradeName: '',
    Category_FK: undefined,
    CAS_Number: '',
    Supplier: '',
    Density: undefined,
    Viscosity: undefined,
    FunctionDescription: '',
  })
}

// Get categories list
async function getCategories() {
  try {
    const res = await getMaterialCategoriesApi()
    // Ensure res is an array, if it's an object, get the data field
    categories.value = Array.isArray(res) ? res : (res.data || [])
  } catch (error) {
    console.error('Failed to get categories list:', error)
  }
}

// Handle selection change
function handleSelectionChange(selection: MaterialInfo[]) {
  selectedRows.value = selection
}

// Export all data
async function handleExport(format: string) {
  try {
    const params = new URLSearchParams({
      format,
      ...(queryParams.keyword && { keyword: queryParams.keyword }),
      ...(queryParams.category && { category: queryParams.category }),
      ...(queryParams.supplier && { supplier: queryParams.supplier })
    })
    
    const response = await request.get(`/api/v1/materials/export?${params.toString()}`, {
      responseType: 'blob'
    })
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `materials_all_${Date.now()}.${format}`)
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
    const columns = ['Material ID', 'Trade Name', 'Category', 'Supplier', 'CAS Number', 'Density', 'Viscosity', 'Function Description']
    let content = ''
    const separator = format === 'csv' ? ',' : '\t'
    
    // Add header
    content = columns.join(separator) + '\n'
    
    // Add data rows
    selectedRows.value.forEach(row => {
      const values = [
        row.MaterialID,
        row.TradeName,
        row.CategoryName || '',
        row.Supplier || '',
        row.CAS_Number || '',
        row.Density || '',
        row.Viscosity || '',
        row.FunctionDescription || ''
      ]
      content += values.join(separator) + '\n'
    })
    
    // Create Blob and download
    const blob = new Blob(['\ufeff' + content], { type: format === 'csv' ? 'text/csv;charset=utf-8' : 'text/plain;charset=utf-8' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `materials_selected_${Date.now()}.${format}`)
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
  getCategories()
})
</script>

<style scoped lang="scss">
.materials-container {
  height: 100%;
}
</style>
