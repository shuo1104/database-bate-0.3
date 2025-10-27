<template>
  <div class="fillers-container">
    <el-card shadow="never">
      <!-- 搜索栏 -->
      <el-form :model="queryParams" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="queryParams.keyword"
            placeholder="请输入商品名称"
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
        <el-table-column prop="FillerID" label="ID" width="80" />
        <el-table-column prop="TradeName" label="商品名称" min-width="150" />
        <el-table-column prop="FillerTypeName" label="填料类型" width="120" />
        <el-table-column prop="Supplier" label="供应商" min-width="150" />
            <el-table-column prop="ParticleSize" label="粒径" width="120" />
            <el-table-column label="是否硅烷化" width="110">
              <template #default="{ row }">
                <el-tag v-if="row.IsSilanized === 1" type="success">是</el-tag>
                <el-tag v-else-if="row.IsSilanized === 0" type="info">否</el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="CouplingAgent" label="偶联剂" min-width="120" show-overflow-tooltip />
            <el-table-column prop="SurfaceArea" label="比表面积" width="110" />
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
        <el-form-item label="商品名称" prop="TradeName">
          <el-input v-model="formData.TradeName" placeholder="请输入商品名称" />
        </el-form-item>
        <el-form-item label="填料类型" prop="FillerType_FK">
          <el-select v-model="formData.FillerType_FK" placeholder="请选择填料类型" style="width: 100%">
            <el-option
              v-for="type in fillerTypes"
              :key="type.FillerTypeID"
              :label="type.FillerTypeName"
              :value="type.FillerTypeID"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="供应商">
          <el-input v-model="formData.Supplier" placeholder="请输入供应商" />
        </el-form-item>
        <el-form-item label="粒径（含D50）">
          <el-input v-model="formData.ParticleSize" placeholder="例如: 10-20nm" />
        </el-form-item>
        <el-form-item label="是否硅烷化">
          <el-radio-group v-model="formData.IsSilanized">
            <el-radio :label="1">是</el-radio>
            <el-radio :label="0">否</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="所用偶联剂">
          <el-input v-model="formData.CouplingAgent" placeholder="请输入所用偶联剂" />
        </el-form-item>
        <el-form-item label="比表面积 (m²/g)">
          <el-input-number 
            v-model.number="formData.SurfaceArea" 
            placeholder="请输入比表面积" 
            :precision="4"
            :step="0.01"
            style="width: 100%"
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
const dialogTitle = ref('新增填料')
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
  TradeName: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  FillerType_FK: [{ required: true, message: '请选择填料类型', trigger: 'change' }],
}

// 获取填料类型列表
async function getFillerTypes() {
  try {
    fillerTypes.value = await getFillerTypesApi()
  } catch (error) {
    console.error('获取填料类型失败:', error)
  }
}

// 获取列表
async function getList() {
  loading.value = true
  try {
    const res = await getFillerListApi(queryParams)
    tableData.value = res.list || res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('获取列表错误:', error)
    ElMessage.error('获取列表失败')
  } finally {
    loading.value = false
  }
}

// 查询
function handleQuery() {
  queryParams.page = 1
  getList()
}

// 重置
function handleReset() {
  queryParams.page = 1
  queryParams.keyword = ''
  queryParams.supplier = ''
  getList()
}

// 新增
function handleCreate() {
  dialogTitle.value = '新增填料'
  dialogVisible.value = true
}

// 编辑
function handleEdit(row: FillerInfo) {
  dialogTitle.value = '编辑填料'
  Object.assign(formData, row)
  dialogVisible.value = true
}

// 删除
function handleDelete(row: FillerInfo) {
  ElMessageBox.confirm('确定要删除该填料吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
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

// 提交
async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        // 转换字段名为后端要求的格式
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
          ElMessage.success('更新成功')
        } else {
          await createFillerApi(requestData)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        getList()
      } catch (error) {
        ElMessage.error(formData.FillerID ? '更新失败' : '创建失败')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

// 关闭对话框
function handleDialogClose() {
  formRef.value?.resetFields()
  Object.assign(formData, {
    TradeName: '',
    FillerType_FK: undefined,
    Supplier: '',
    ParticleSize: '',
    IsSilanized: 0,
    CouplingAgent: '',
    SurfaceArea: undefined,
  })
}

// 处理选择变化
function handleSelectionChange(selection: FillerInfo[]) {
  selectedRows.value = selection
}

// 导出全部数据
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
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `fillers_all_${Date.now()}.${format}`)
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
    const columns = ['填料ID', '商品名称', '填料类型', '供应商', '粒径', '是否硅烷化', '偶联剂', '比表面积']
    let content = ''
    const separator = format === 'csv' ? ',' : '\t'
    
    // 添加表头
    content = columns.join(separator) + '\n'
    
    // 添加数据行
    selectedRows.value.forEach(row => {
      const values = [
        row.FillerID,
        row.TradeName,
        row.FillerTypeName || '',
        row.Supplier || '',
        row.ParticleSize || '',
        row.IsSilanized ? '是' : '否',
        row.CouplingAgent || '',
        row.SurfaceArea || ''
      ]
      content += values.join(separator) + '\n'
    })
    
    // 创建Blob并下载
    const blob = new Blob(['\ufeff' + content], { type: format === 'csv' ? 'text/csv;charset=utf-8' : 'text/plain;charset=utf-8' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `fillers_selected_${Date.now()}.${format}`)
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
  getFillerTypes()
  getList()
})
</script>

<style scoped lang="scss">
.fillers-container {
  height: 100%;
}
</style>

