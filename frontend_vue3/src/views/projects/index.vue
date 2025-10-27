<template>
  <div class="projects-container">
    <el-card shadow="never">
      <!-- 搜索栏 -->
      <el-form :model="queryParams" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="queryParams.keyword"
            placeholder="请输入项目名称或配方编号"
            clearable
            style="width: 200px"
            @clear="handleQuery"
          />
        </el-form-item>
        <el-form-item label="项目类型">
          <el-select
            v-model="queryParams.project_type"
            placeholder="请选择项目类型"
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
        <el-form-item label="配方师">
          <el-select
            v-model="queryParams.formulator"
            placeholder="请选择配方师"
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
                <el-dropdown-item command="image" divided>导出图片报告</el-dropdown-item>
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
                <el-dropdown-item command="image" divided>导出图片报告</el-dropdown-item>
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
        <el-table-column prop="ProjectID" label="ID" width="80" />
        <el-table-column prop="ProjectName" label="项目名称" min-width="150" />
        <el-table-column prop="FormulaCode" label="配方编号" min-width="180" />
        <el-table-column prop="TypeName" label="项目类型" width="120" />
        <el-table-column prop="FormulatorName" label="配方师" width="120" />
        <el-table-column prop="SubstrateApplication" label="基材应用" min-width="150" />
        <el-table-column prop="FormulationDate" label="配方日期" width="120" />
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button type="info" size="small" @click="handleViewDetail(row)">详情</el-button>
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
        <el-form-item label="项目名称" prop="ProjectName">
          <el-input v-model="formData.ProjectName" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目类型" prop="ProjectType_FK">
          <el-select v-model="formData.ProjectType_FK" placeholder="请选择项目类型" style="width: 100%">
            <el-option
              v-for="type in projectTypes"
              :key="type.TypeID"
              :label="type.TypeName"
              :value="type.TypeID"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="配方设计师" prop="FormulatorName">
          <el-input v-model="formData.FormulatorName" placeholder="请输入配方设计师姓名" />
        </el-form-item>
        <el-form-item label="配方日期" prop="FormulationDate">
          <el-date-picker
            v-model="formData.FormulationDate"
            type="date"
            placeholder="选择配方设计日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="目标基材">
          <el-input v-model="formData.SubstrateApplication" placeholder="请输入目标基材或应用领域" />
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
const dialogTitle = ref('新增项目')
const formRef = ref<FormInstance>()
const formData = reactive<Partial<ProjectInfo>>({
  ProjectName: '',
  ProjectType_FK: undefined,
  FormulatorName: '',
  FormulationDate: '',
  SubstrateApplication: '',
})

const formRules = {
  ProjectName: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  ProjectType_FK: [{ required: true, message: '请选择项目类型', trigger: 'change' }],
  FormulatorName: [{ required: true, message: '请输入配方设计师', trigger: 'blur' }],
  FormulationDate: [{ required: true, message: '请选择配方日期', trigger: 'change' }],
}

// 项目类型列表和配方师列表
const projectTypes = ref<any[]>([])
const formulators = ref<string[]>([])

// 获取列表
async function getList() {
  loading.value = true
  try {
    const res = await getProjectListApi(queryParams)
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

// 查询
function handleQuery() {
  console.log('查询被调用，参数:', queryParams)
  queryParams.page = 1
  getList()
}

// 重置
function handleReset() {
  queryParams.page = 1
  queryParams.keyword = ''
  queryParams.project_type = ''
  queryParams.formulator = ''
  getList()
}

// 查看详情
function handleViewDetail(row: ProjectInfo) {
  router.push(`/projects/${row.ProjectID}`)
}

// 新增
function handleCreate() {
  dialogTitle.value = '新增项目'
  dialogVisible.value = true
}

// 编辑
function handleEdit(row: ProjectInfo) {
  dialogTitle.value = '编辑项目'
  Object.assign(formData, row)
  dialogVisible.value = true
}

// 删除
function handleDelete(row: ProjectInfo) {
  ElMessageBox.confirm('确定要删除该项目吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await deleteProjectApi(row.ProjectID)
      ElMessage.success('删除成功')
      getList()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

// 导出图片报告
async function handleExportImage(row: any) {
  row.exportLoading = true
  try {
    const blob = await exportProjectImageApi(row.ProjectID)
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([blob]))
    const link = document.createElement('a')
    link.href = url
    const timestamp = new Date().getTime()
    link.setAttribute('download', `project_${row.ProjectID}_report_${timestamp}.png`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success(`项目 ${row.ProjectName} 的图片报告导出成功`)
  } catch (error: any) {
    console.error('导出图片报告失败:', error)
    ElMessage.error(`项目 ${row.ProjectName} 的图片报告导出失败`)
  } finally {
    row.exportLoading = false
  }
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
          project_name: formData.ProjectName,
          project_type_fk: formData.ProjectType_FK,
          formulator_name: formData.FormulatorName,
          formulation_date: formData.FormulationDate,
          substrate_application: formData.SubstrateApplication,
        }

        if (formData.ProjectID) {
          await updateProjectApi(formData.ProjectID, requestData)
          ElMessage.success('更新成功')
        } else {
          await createProjectApi(requestData)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        getList()
      } catch (error) {
        ElMessage.error(formData.ProjectID ? '更新失败' : '创建失败')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

// 获取项目类型列表
async function getProjectTypes() {
  try {
    const types = await getProjectTypesApi()
    projectTypes.value = types || []
  } catch (error) {
    console.error('获取项目类型失败:', error)
  }
}

// 获取配方师列表
async function getFormulators() {
  try {
    const res = await getFormulatorsApi()
    formulators.value = res || []
  } catch (error) {
    console.error('获取配方师列表失败:', error)
  }
}

// 关闭对话框
function handleDialogClose() {
  formRef.value?.resetFields()
  Object.assign(formData, {
    ProjectName: '',
    ProjectType_FK: undefined,
    FormulatorName: '',
    FormulationDate: '',
    SubstrateApplication: '',
  })
}

// 处理选择变化
function handleSelectionChange(selection: ProjectInfo[]) {
  selectedRows.value = selection
}

// 导出全部数据
async function handleExport(format: string) {
  if (format === 'image') {
    ElMessage.warning('图片报告仅支持单个项目导出，请在详情页或操作列中导出')
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
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `projects_all_${Date.now()}.${format}`)
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
  if (selectedRows.value.length === 0 && format !== 'image') {
    ElMessage.warning('请先选择要导出的数据')
    return
  }

  if (format === 'image') {
    if (selectedRows.value.length === 0) {
      ElMessage.warning('请选择要导出图片报告的项目')
      return
    }
    if (selectedRows.value.length > 5) {
      ElMessage.warning('一次最多只能导出5个项目的图片报告')
      return
    }
    
    // 挨个导出图片
    for (const row of selectedRows.value) {
      await handleExportImage(row)
    }
    return
  }

  try {
    // 准备CSV/TXT内容
    const columns = ['项目ID', '项目名称', '项目类型', '配方编号', '配方设计师', '配方日期', '目标基材', '创建时间']
    let content = ''
    const separator = format === 'csv' ? ',' : '\t'
    
    // 添加表头
    content = columns.join(separator) + '\n'
    
    // 添加数据行
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
    
    // 创建Blob并下载
    const blob = new Blob(['\ufeff' + content], { type: format === 'csv' ? 'text/csv;charset=utf-8' : 'text/plain;charset=utf-8' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `projects_selected_${Date.now()}.${format}`)
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
  getProjectTypes()
  getFormulators()
})
</script>

<style scoped lang="scss">
.projects-container {
  height: 100%;
}
</style>

