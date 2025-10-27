<template>
  <div class="materials-container">
    <el-card shadow="never">
      <!-- 搜索栏 -->
      <el-form :model="queryParams" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="queryParams.keyword"
            placeholder="请输入原料名称或CAS号"
            clearable
            @clear="handleQuery"
          />
        </el-form-item>
        <el-form-item label="供应商">
          <el-input
            v-model="queryParams.supplier"
            placeholder="请输入供应商"
            clearable
            @clear="handleQuery"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button type="success" @click="handleCreate">新增</el-button>
          <el-dropdown @command="handleExport" style="margin-left: 10px">
            <el-button type="warning">
              导出全部<el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="csv">导出为 CSV</el-dropdown-item>
                <el-dropdown-item command="txt">导出为 TXT</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-dropdown @command="handleExportSelected" style="margin-left: 10px" :disabled="selectedRows.length === 0">
            <el-button type="info" :disabled="selectedRows.length === 0">
              导出选中({{ selectedRows.length }})<el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="csv">导出为 CSV</el-dropdown-item>
                <el-dropdown-item command="txt">导出为 TXT</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
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
        <el-table-column prop="TradeName" label="商品名" min-width="150" />
        <el-table-column prop="CategoryName" label="类别" width="120" />
        <el-table-column prop="CAS_Number" label="CAS号" width="120" />
        <el-table-column prop="Supplier" label="供应商" width="120" />
        <el-table-column prop="Density" label="密度" width="100">
          <template #default="{ row }">
            {{ row.Density ? Number(row.Density).toFixed(4) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="Viscosity" label="粘度" width="100">
          <template #default="{ row }">
            {{ row.Viscosity ? Number(row.Viscosity).toFixed(2) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="FunctionDescription" label="功能描述" min-width="150" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <Pagination
        v-show="total > 0"
        :total="total"
        v-model:page="queryParams.page"
        v-model:limit="queryParams.page_size"
        @pagination="getList"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px">
        <el-form-item label="原料名称" prop="MaterialName">
          <el-input v-model="formData.MaterialName" placeholder="请输入原料名称" />
        </el-form-item>
        <el-form-item label="英文名称">
          <el-input v-model="formData.EnglishName" placeholder="请输入英文名称" />
        </el-form-item>
        <el-form-item label="CAS号">
          <el-input v-model="formData.CAS" placeholder="请输入CAS号" />
        </el-form-item>
        <el-form-item label="类别">
          <el-input v-model="formData.Category" placeholder="请输入类别" />
        </el-form-item>
        <el-form-item label="供应商">
          <el-input v-model="formData.Supplier" placeholder="请输入供应商" />
        </el-form-item>
        <el-form-item label="单位">
          <el-input v-model="formData.Unit" placeholder="请输入单位（如：kg）" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="formData.Remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import { getMaterialListApi, createMaterialApi, updateMaterialApi, deleteMaterialApi, type MaterialInfo } from '@/api/materials'
import { formatDateTime } from '@/utils/common'
import Pagination from '@/components/Pagination.vue'
import request from '@/utils/request'

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref<MaterialInfo[]>([])
const total = ref(0)
const selectedRows = ref<MaterialInfo[]>([])

const queryParams = reactive({
  page: 1,
  page_size: 20,
  keyword: '',
  supplier: '',
})

const dialogVisible = ref(false)
const dialogTitle = ref('新增原料')
const formRef = ref<FormInstance>()
const formData = reactive<Partial<MaterialInfo>>({
  MaterialName: '',
  EnglishName: '',
  CAS: '',
  Category: '',
  Supplier: '',
  Unit: 'kg',
  Remark: '',
})

const formRules = {
  MaterialName: [{ required: true, message: '请输入原料名称', trigger: 'blur' }],
}

async function getList() {
  loading.value = true
  try {
    const res = await getMaterialListApi(queryParams)
    // 后端返回的是 list 而不是 items
    tableData.value = res.list || res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('获取列表错误:', error)
    ElMessage.error('获取列表失败')
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
  queryParams.supplier = ''
  getList()
}

function handleCreate() {
  dialogTitle.value = '新增原料'
  dialogVisible.value = true
}

function handleEdit(row: MaterialInfo) {
  dialogTitle.value = '编辑原料'
  Object.assign(formData, row)
  dialogVisible.value = true
}

function handleDelete(row: MaterialInfo) {
  ElMessageBox.confirm('确定要删除该原料吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await deleteMaterialApi(row.MaterialID)
      ElMessage.success('删除成功')
      getList()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        // 转换字段名为后端要求的格式
        const requestData: any = {
          trade_name: formData.MaterialName,
          cas_number: formData.CAS,
          supplier: formData.Supplier,
          density: formData.Density ? Number(formData.Density) : undefined,
          viscosity: formData.Viscosity ? Number(formData.Viscosity) : undefined,
          function_description: formData.Remark,
        }

        if (formData.MaterialID) {
          await updateMaterialApi(formData.MaterialID, requestData)
          ElMessage.success('更新成功')
        } else {
          await createMaterialApi(requestData)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        getList()
      } catch (error) {
        ElMessage.error(formData.MaterialID ? '更新失败' : '创建失败')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

function handleDialogClose() {
  formRef.value?.resetFields()
  Object.assign(formData, {
    MaterialName: '',
    EnglishName: '',
    CAS: '',
    Category: '',
    Supplier: '',
    Unit: 'kg',
    Remark: '',
  })
}

// 处理选择变化
function handleSelectionChange(selection: MaterialInfo[]) {
  selectedRows.value = selection
}

// 导出全部数据
async function handleExport(format: string) {
  try {
    const params = new URLSearchParams({
      format,
      ...(queryParams.MaterialName && { keyword: queryParams.MaterialName }),
      ...(queryParams.Category && { category: queryParams.Category })
    })
    
    const response = await request.get(`/api/v1/materials/export?${params.toString()}`, {
      responseType: 'blob'
    })
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `materials_all_${Date.now()}.${format}`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
    console.error('导出失败:', error)
  }
}

// 导出选中数据
async function handleExportSelected(format: string) {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择要导出的数据')
    return
  }

  try {
    // 准备CSV/TXT内容
    const columns = ['原料ID', '商品名称', '类别', '供应商', 'CAS号', '密度', '粘度', '功能说明']
    let content = ''
    const separator = format === 'csv' ? ',' : '\t'
    
    // 添加表头
    content = columns.join(separator) + '\n'
    
    // 添加数据行
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
    
    // 创建Blob并下载
    const blob = new Blob(['\ufeff' + content], { type: format === 'csv' ? 'text/csv;charset=utf-8' : 'text/plain;charset=utf-8' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `materials_selected_${Date.now()}.${format}`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success(`已导出 ${selectedRows.value.length} 条数据`)
  } catch (error) {
    ElMessage.error('导出失败')
    console.error('导出失败:', error)
  }
}

onMounted(() => {
  getList()
})
</script>

<style scoped lang="scss">
.materials-container {
  height: 100%;
}
</style>

