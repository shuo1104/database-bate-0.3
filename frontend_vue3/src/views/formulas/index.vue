<template>
  <div class="formula-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>配方成分管理</span>
        </div>
      </template>

      <!-- 搜索区域 -->
      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="项目筛选">
          <el-select
            v-model="queryParams.project_id"
            placeholder="请选择项目"
            clearable
            filterable
            style="width: 300px"
            @change="handleProjectChange"
          >
            <el-option
              v-for="project in projects"
              :key="project.ProjectID"
              :label="`${project.ProjectName} (${project.FormulaCode})`"
              :value="project.ProjectID"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 操作按钮 -->
      <div class="toolbar">
        <el-button
          type="primary"
          :icon="Plus"
          @click="handleAdd"
          :disabled="!queryParams.project_id"
        >
          添加成分
        </el-button>
        <el-button
          type="danger"
          :icon="Delete"
          @click="handleBatchDelete"
          :disabled="selectedRows.length === 0"
        >
          批量删除
        </el-button>
      </div>

      <!-- 项目信息展示 -->
      <el-alert
        v-if="currentProject"
        :title="`当前项目: ${currentProject.ProjectName} | 配方编号: ${currentProject.FormulaCode} | 项目类型: ${currentProject.TypeName || '-'}`"
        type="info"
        :closable="false"
        style="margin-bottom: 16px"
      />

      <!-- 数据表格 -->
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
        <el-table-column label="成分类型" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.MaterialID_FK" type="success">原料</el-tag>
            <el-tag v-else-if="row.FillerID_FK" type="warning">填料</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="成分名称" min-width="150">
          <template #default="{ row }">
            {{ row.MaterialName || row.FillerName || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="WeightPercentage" label="重量百分比 (%)" width="140" />
        <el-table-column prop="AdditionMethod" label="掺入方法" min-width="150" show-overflow-tooltip />
        <el-table-column prop="Remarks" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 配方汇总 -->
      <div v-if="tableData.length > 0" class="composition-summary">
        <el-tag type="info" size="large">
          总重量百分比: {{ totalWeightPercentage.toFixed(2) }}%
        </el-tag>
        <el-tag :type="totalWeightPercentage <= 100 ? 'success' : 'danger'" size="large">
          {{ totalWeightPercentage <= 100 ? '✓ 配比正常' : '⚠ 超过100%' }}
        </el-tag>
      </div>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px">
        <el-form-item label="成分类型" prop="componentType">
          <el-radio-group v-model="formData.componentType">
            <el-radio label="material">原料</el-radio>
            <el-radio label="filler">填料</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="formData.componentType === 'material'" label="选择原料" prop="MaterialID_FK">
          <el-select v-model="formData.MaterialID_FK" placeholder="请选择原料" style="width: 100%" filterable>
            <el-option
              v-for="material in materials"
              :key="material.MaterialID"
              :label="material.TradeName"
              :value="material.MaterialID"
            />
          </el-select>
        </el-form-item>
        <el-form-item v-if="formData.componentType === 'filler'" label="选择填料" prop="FillerID_FK">
          <el-select v-model="formData.FillerID_FK" placeholder="请选择填料" style="width: 100%" filterable>
            <el-option
              v-for="filler in fillers"
              :key="filler.FillerID"
              :label="filler.TradeName"
              :value="filler.FillerID"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="重量百分比" prop="WeightPercentage">
          <el-input v-model.number="formData.WeightPercentage" placeholder="请输入重量百分比" type="number" step="0.01">
            <template #append>%</template>
          </el-input>
        </el-form-item>
        <el-form-item label="掺入方法">
          <el-input v-model="formData.AdditionMethod" placeholder="请输入掺入方法" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="formData.Remarks"
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
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Search, Refresh, Plus, Delete } from '@element-plus/icons-vue'
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

// 查询参数
const queryParams = reactive({
  project_id: undefined as number | undefined,
})

// 数据
const loading = ref(false)
const tableData = ref<FormulaComposition[]>([])
const selectedRows = ref<FormulaComposition[]>([])
const projects = ref<ProjectInfo[]>([])
const currentProject = ref<ProjectInfo | null>(null)
const materials = ref<MaterialInfo[]>([])
const fillers = ref<FillerInfo[]>([])

// 计算总重量百分比
const totalWeightPercentage = computed(() => {
  return tableData.value.reduce((sum, item) => sum + (Number(item.WeightPercentage) || 0), 0)
})

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('添加成分')
const formRef = ref<FormInstance>()
const submitLoading = ref(false)

interface FormData {
  CompositionID?: number
  componentType: 'material' | 'filler'
  MaterialID_FK?: number
  FillerID_FK?: number
  WeightPercentage?: number
  AdditionMethod?: string
  Remarks?: string
}

const formData = reactive<FormData>({
  componentType: 'material',
  WeightPercentage: undefined,
  AdditionMethod: '',
  Remarks: '',
})

const formRules = {
  componentType: [{ required: true, message: '请选择成分类型', trigger: 'change' }],
  MaterialID_FK: [{ required: true, message: '请选择原料', trigger: 'change' }],
  FillerID_FK: [{ required: true, message: '请选择填料', trigger: 'change' }],
  WeightPercentage: [
    { required: true, message: '请输入重量百分比', trigger: 'blur' },
    { type: 'number', min: 0, max: 100, message: '重量百分比应在0-100之间', trigger: 'blur' }
  ],
}

// 获取项目列表（只显示有配方成分的项目）
async function getProjects() {
  try {
    // 使用分页获取所有项目，每次100条
    let allProjects = []
    let currentPage = 1
    let hasMore = true
    
    while (hasMore && currentPage <= 20) { // 最多20页，避免无限循环
      const res = await getProjectListApi({ 
        page: currentPage, 
        page_size: 100,
        has_compositions: true  // 只显示有配方成分的项目
      })
      const list = res.list || res.items || []
      allProjects = allProjects.concat(list)
      
      // 如果返回的数量少于100，说明没有更多了
      if (list.length < 100) {
        hasMore = false
      } else {
        currentPage++
      }
    }
    
    projects.value = allProjects
  } catch (error) {
    console.error('获取项目列表失败:', error)
  }
}

// 获取原料和填料列表
async function getMaterialsAndFillers() {
  try {
    const [materialsRes, fillersRes] = await Promise.all([
      getMaterialListApi({ page: 1, page_size: 100 }),
      getFillerListApi({ page: 1, page_size: 100 })
    ])
    materials.value = materialsRes.list || materialsRes.items || []
    fillers.value = fillersRes.list || fillersRes.items || []
  } catch (error) {
    console.error('获取原料/填料列表失败:', error)
  }
}

// 项目切换
async function handleProjectChange() {
  if (queryParams.project_id) {
    await loadProjectInfo()
    await loadCompositions()
  } else {
    currentProject.value = null
    tableData.value = []
  }
}

// 加载项目信息
async function loadProjectInfo() {
  if (!queryParams.project_id) return
  try {
    currentProject.value = await getProjectDetailApi(queryParams.project_id)
  } catch (error) {
    console.error('获取项目信息失败:', error)
  }
}

// 加载配方成分
async function loadCompositions() {
  if (!queryParams.project_id) return
  loading.value = true
  try {
    const res = await getCompositionListApi(queryParams.project_id)
    tableData.value = Array.isArray(res) ? res : []
  } catch (error) {
    ElMessage.error('获取配方成分失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 查询
function handleSearch() {
  loadCompositions()
}

// 重置
function handleReset() {
  queryParams.project_id = undefined
  currentProject.value = null
  tableData.value = []
}

// 选择变化
function handleSelectionChange(selection: FormulaComposition[]) {
  selectedRows.value = selection
}

// 添加
function handleAdd() {
  if (!queryParams.project_id) {
    ElMessage.warning('请先选择项目')
    return
  }
  dialogTitle.value = '添加成分'
  dialogVisible.value = true
}

// 编辑
function handleEdit(row: FormulaComposition) {
  dialogTitle.value = '编辑成分'
  Object.assign(formData, {
    CompositionID: row.CompositionID,
    componentType: row.MaterialID_FK ? 'material' : 'filler',
    MaterialID_FK: row.MaterialID_FK,
    FillerID_FK: row.FillerID_FK,
    WeightPercentage: row.WeightPercentage,
    AdditionMethod: row.AdditionMethod,
    Remarks: row.Remarks,
  })
  dialogVisible.value = true
}

// 删除
function handleDelete(row: FormulaComposition) {
  ElMessageBox.confirm('确定要删除该成分吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await deleteCompositionApi(row.CompositionID)
      ElMessage.success('删除成功')
      loadCompositions()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

// 批量删除
function handleBatchDelete() {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请选择要删除的数据')
    return
  }
  ElMessageBox.confirm(`确定要删除选中的 ${selectedRows.value.length} 条数据吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await Promise.all(selectedRows.value.map(row => deleteCompositionApi(row.CompositionID)))
      ElMessage.success('删除成功')
      loadCompositions()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

// 提交表单
async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        const data: any = {
          project_id: queryParams.project_id,
          weight_percentage: formData.WeightPercentage,
          addition_method: formData.AdditionMethod,
          remarks: formData.Remarks,
        }

        if (formData.componentType === 'material') {
          data.material_id = formData.MaterialID_FK
        } else {
          data.filler_id = formData.FillerID_FK
        }

        if (formData.CompositionID) {
          await updateCompositionApi(formData.CompositionID, data)
          ElMessage.success('更新成功')
        } else {
          await createCompositionApi(data)
          ElMessage.success('添加成功')
        }
        dialogVisible.value = false
        loadCompositions()
      } catch (error) {
        ElMessage.error(formData.CompositionID ? '更新失败' : '添加失败')
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
    componentType: 'material',
    WeightPercentage: undefined,
    AdditionMethod: '',
    Remarks: '',
  })
}

onMounted(() => {
  getProjects()
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

