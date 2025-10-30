<template>
  <div class="materials-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>Materials Management</span>
        </div>
      </template>

      <!-- Search Bar -->
      <el-form :model="table.queryParams" inline class="search-form">
        <el-form-item label="Keyword">
          <el-input
            v-model="table.queryParams.keyword"
            placeholder="Enter trade name or CAS number"
            clearable
            @keyup.enter="table.handleQuery"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="Category">
          <el-select
            v-model="table.queryParams.category"
            placeholder="Select category"
            clearable
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
            v-model="table.queryParams.supplier"
            placeholder="Enter supplier"
            clearable
            style="width: 150px"
          />
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
          :show-image="false"
          @export="exportHelper.handleExport"
        />
        <ExportDropdown
          label="Export Selected"
          type="info"
          :disabled="!table.hasSelection"
          :show-image="false"
          @export="handleExportSelected"
        >
          <template v-if="table.hasSelection">
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
            <el-button type="primary" size="small" @click="crud.handleEdit(row)">Edit</el-button>
            <el-button type="danger" size="small" @click="crud.handleDelete(row, 'MaterialID')">Delete</el-button>
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
      <el-form :ref="(el: any) => crud.formRef.value = el" :model="crud.formData" :rules="formRules" label-width="150px">
        <el-form-item label="Trade Name" prop="TradeName">
          <el-input v-model="crud.formData.TradeName" placeholder="Enter trade name" />
        </el-form-item>
        <el-form-item label="Category">
          <el-select
            v-model="crud.formData.Category_FK"
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
          <el-input v-model="crud.formData.CAS_Number" placeholder="Enter CAS number" />
        </el-form-item>
        <el-form-item label="Supplier">
          <el-input v-model="crud.formData.Supplier" placeholder="Enter supplier" />
        </el-form-item>
        <el-form-item label="Density">
          <el-input v-model="crud.formData.Density" type="number" placeholder="Enter density" />
        </el-form-item>
        <el-form-item label="Viscosity">
          <el-input v-model="crud.formData.Viscosity" type="number" placeholder="Enter viscosity" />
        </el-form-item>
        <el-form-item label="Function Description">
          <el-input
            v-model="crud.formData.FunctionDescription"
            type="textarea"
            :rows="3"
            placeholder="Enter function description"
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
import { Plus } from '@element-plus/icons-vue'
import { 
  getMaterialListApi, 
  createMaterialApi, 
  updateMaterialApi, 
  deleteMaterialApi, 
  getMaterialCategoriesApi,
  type MaterialInfo,
  type MaterialCategory
} from '@/api/materials'
import Pagination from '@/components/Pagination.vue'
import ExportDropdown from '@/components/ExportDropdown/index.vue'
import { useTable } from '@/composables/useTable'
import { useCRUD } from '@/composables/useCRUD'
import { useExport } from '@/composables/useExport'
import request from '@/utils/request'
import {
  tradeNameRules,
} from '@/utils/validators'

// ==================== 表格管理 ====================
const table = useTable(getMaterialListApi, { 
  defaultPageSize: 20,
  dataTransform: (res: any) => ({
    list: res.list || res.items || [],
    total: res.total || 0
  })
})

// 扩展查询参数
Object.assign(table.queryParams, {
  category: '',
  supplier: ''
})

const hasSelection = computed(() => table.selectedRows.value.length > 0)

// ==================== CRUD 管理 ====================
const crud = useCRUD({
  createApi: createMaterialApi,
  updateApi: updateMaterialApi,
  deleteApi: deleteMaterialApi,
  idKey: 'MaterialID',
  resourceName: 'Material',
  onSuccess: () => table.fetchData(),
  transformRequestData: (formData: any) => ({
    trade_name: formData.TradeName,
    category_fk: formData.Category_FK,
    cas_number: formData.CAS_Number,
    supplier: formData.Supplier,
    density: formData.Density ? Number(formData.Density) : undefined,
    viscosity: formData.Viscosity ? Number(formData.Viscosity) : undefined,
    function_description: formData.FunctionDescription,
  }),
  transformResponseData: (data: any) => ({
    ...data,
    Density: data.Density ? Number(data.Density) : undefined,
    Viscosity: data.Viscosity ? Number(data.Viscosity) : undefined,
  }),
  defaultFormData: {
    TradeName: '',
    Category_FK: undefined,
    CAS_Number: '',
    Supplier: '',
    Density: undefined,
    Viscosity: undefined,
    FunctionDescription: '',
  }
})

const formRules = {
  TradeName: tradeNameRules,
  // Optional fields - no validation rules needed
  // They will be validated by backend if provided
}

// ==================== 导出管理 ====================
const exportHelper = useExport({
  exportApi: async (format: string, params: any) => {
    const queryString = new URLSearchParams({
      format,
      ...(table.queryParams.category && { category: table.queryParams.category }),
      ...(table.queryParams.supplier && { supplier: table.queryParams.supplier }),
      ...(table.queryParams.keyword && { keyword: table.queryParams.keyword })
    }).toString()
    
    return await request.get(`/api/v1/materials/export?${queryString}`, {
      responseType: 'blob'
    })
  },
  resourceName: 'Materials'
})

function handleExportSelected(format: string) {
  exportHelper.handleExportSelected(
    format,
    table.selectedRows.value,
    [
      { key: 'MaterialID', label: 'Material ID' },
      { key: 'TradeName', label: 'Trade Name' },
      { key: 'CategoryName', label: 'Category' },
      { key: 'CAS_Number', label: 'CAS Number' },
      { key: 'Supplier', label: 'Supplier' },
      { key: 'Density', label: 'Density' },
      { key: 'Viscosity', label: 'Viscosity' }
    ]
  )
}

// ==================== 业务逻辑 ====================
const categories = ref<MaterialCategory[]>([])

async function getCategories() {
  try {
    const res = await getMaterialCategoriesApi()
    categories.value = Array.isArray(res) ? res : (res.data || [])
  } catch (error) {
    console.error('Failed to get categories list:', error)
  }
}

// 自定义重置逻辑
function handleReset() {
  table.queryParams.keyword = ''
  table.queryParams.category = ''
  table.queryParams.supplier = ''
  table.handleReset()
}

// ==================== 初始化 ====================
onMounted(() => {
  table.fetchData()
  getCategories()
})
</script>

<style scoped lang="scss">
.materials-container {
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
