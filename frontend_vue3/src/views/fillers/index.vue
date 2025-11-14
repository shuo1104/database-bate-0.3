<template>
  <div class="fillers-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>Fillers Management</span>
        </div>
      </template>

      <!-- Search Bar -->
      <el-form :model="table.queryParams" inline class="search-form">
        <el-form-item label="Keyword">
          <el-input
            v-model="table.queryParams.keyword"
            placeholder="Enter trade name"
            clearable
            @keyup.enter="table.handleQuery"
            style="width: 200px"
          />
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
          :disabled="!hasSelection"
          :show-image="false"
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
            <el-button type="primary" size="small" @click="crud.handleEdit(row)">Edit</el-button>
            <el-button type="danger" size="small" @click="crud.handleDelete(row, 'FillerID' as any)">Delete</el-button>
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
        <el-form-item label="Filler Type" prop="FillerType_FK">
          <el-select v-model="crud.formData.FillerType_FK" placeholder="Select filler type" style="width: 100%">
            <el-option
              v-for="type in fillerTypes"
              :key="type.FillerTypeID"
              :label="type.FillerTypeName"
              :value="type.FillerTypeID"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Supplier">
          <el-input v-model="crud.formData.Supplier" placeholder="Enter supplier" />
        </el-form-item>
        <el-form-item label="Particle Size (D50)">
          <el-input v-model="crud.formData.ParticleSize" placeholder="e.g. 10-20nm" />
        </el-form-item>
        <el-form-item label="Silanized">
          <el-radio-group v-model="crud.formData.IsSilanized">
            <el-radio :label="1">Yes</el-radio>
            <el-radio :label="0">No</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Coupling Agent">
          <el-input v-model="crud.formData.CouplingAgent" placeholder="Enter coupling agent" />
        </el-form-item>
        <el-form-item label="Surface Area (m²/g)">
          <el-input-number 
            v-model.number="crud.formData.SurfaceArea" 
            placeholder="Enter surface area" 
            :precision="4"
            :step="0.01"
            style="width: 100%"
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
  getFillerListApi, 
  createFillerApi, 
  updateFillerApi, 
  deleteFillerApi,
  getFillerTypesApi,
  // type FillerInfo,
  type FillerType
} from '@/api/fillers'
import Pagination from '@/components/Pagination.vue'
import ExportDropdown from '@/components/ExportDropdown/index.vue'
import { useTable } from '@/composables/useTable'
import { useCRUD } from '@/composables/useCRUD'
import { useExport } from '@/composables/useExport'
import request from '@/utils/request'
import {
  tradeNameRules,
  createSelectRequiredRule,
} from '@/utils/validators'

// ==================== 表格管理 ====================
const table = useTable(getFillerListApi, { 
  defaultPageSize: 20
})

// 扩展查询参数
Object.assign(table.queryParams, {
  supplier: ''
})

const hasSelection = computed(() => table.selectedRows.value.length > 0)

// ==================== CRUD 管理 ====================
const crud = useCRUD({
  createApi: createFillerApi,
  updateApi: updateFillerApi as any,
  deleteApi: deleteFillerApi as any,
  idKey: 'FillerID',
  resourceName: 'Filler',
  onSuccess: () => table.fetchData(),
  transformRequestData: (formData: any) => ({
    trade_name: formData.TradeName,
    filler_type_fk: formData.FillerType_FK,
    supplier: formData.Supplier,
    particle_size: formData.ParticleSize,
    is_silanized: formData.IsSilanized,
    coupling_agent: formData.CouplingAgent,
    surface_area: formData.SurfaceArea ? Number(formData.SurfaceArea) : undefined,
  }),
  transformResponseData: (data: any) => ({
    ...data,
    SurfaceArea: data.SurfaceArea ? Number(data.SurfaceArea) : undefined,
  }),
  defaultFormData: {
    TradeName: '',
    FillerType_FK: undefined,
    Supplier: '',
    ParticleSize: '',
    IsSilanized: 0,
    CouplingAgent: '',
    SurfaceArea: undefined,
  }
})

const formRules = {
  TradeName: tradeNameRules,
  FillerType_FK: [createSelectRequiredRule('filler type')],
  // Optional fields - no validation rules needed
  // They will be validated by backend if provided
}

// ==================== 导出管理 ====================
const exportHelper = useExport({
  exportApi: async (format: string, _params: any) => {
    const queryString = new URLSearchParams({
      format,
      ...(table.queryParams.supplier && { supplier: table.queryParams.supplier }),
      ...(table.queryParams.keyword && { keyword: table.queryParams.keyword })
    }).toString()
    
    return await request.get(`/api/v1/fillers/export?${queryString}`, {
      responseType: 'blob'
    })
  },
  resourceName: 'Fillers'
})

function handleExportSelected(format: string) {
  exportHelper.handleExportSelected(
    format,
    table.selectedRows.value,
    [
      { key: 'FillerID', label: 'Filler ID' },
      { key: 'TradeName', label: 'Trade Name' },
      { key: 'FillerTypeName', label: 'Filler Type' },
      { key: 'Supplier', label: 'Supplier' },
      { key: 'ParticleSize', label: 'Particle Size' },
      { key: 'IsSilanized', label: 'Silanized' },
      { key: 'CouplingAgent', label: 'Coupling Agent' },
      { key: 'SurfaceArea', label: 'Surface Area' }
    ]
  )
}

// ==================== 业务逻辑 ====================
const fillerTypes = ref<FillerType[]>([])

async function getFillerTypes() {
  try {
    const res = await getFillerTypesApi()
    fillerTypes.value = Array.isArray(res) ? res : ((res as any).data || [])
  } catch (error) {
    console.error('Failed to get filler types:', error)
  }
}

// 自定义重置逻辑
function handleReset() {
  table.queryParams.keyword = ''
  table.queryParams.supplier = ''
  table.handleReset()
}

// ==================== 初始化 ====================
onMounted(() => {
  table.fetchData()
  getFillerTypes()
})
</script>

<style scoped lang="scss">
.fillers-container {
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

