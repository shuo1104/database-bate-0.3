<template>
  <div class="test-results-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>测试结果管理</span>
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

      <!-- 项目信息展示 -->
      <el-alert
        v-if="currentProject"
        :title="`当前项目: ${currentProject.ProjectName} | 配方编号: ${currentProject.FormulaCode} | 项目类型: ${currentProject.TypeName || '-'}`"
        type="info"
        :closable="false"
        style="margin-bottom: 16px"
      />

      <!-- 操作按钮 -->
      <div class="toolbar">
        <el-button
          type="primary"
          :icon="Edit"
          @click="handleEdit"
          :disabled="!queryParams.project_id || !currentProject"
        >
          编辑测试结果
        </el-button>
      </div>

      <!-- 测试结果显示 -->
      <div v-if="testResult" class="test-result-content">
        <el-descriptions :column="2" border>
          <template v-for="(value, key) in filteredTestResult" :key="key">
            <el-descriptions-item :label="formatFieldLabel(String(key))">
              {{ value || '-' }}
            </el-descriptions-item>
          </template>
        </el-descriptions>
      </div>
      <el-empty v-else-if="queryParams.project_id" description="暂无测试结果，点击上方按钮添加" />
      <el-empty v-else description="请选择项目查看测试结果" />
    </el-card>

    <!-- 测试结果编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="编辑测试结果"
      width="800px"
      @close="handleDialogClose"
    >
      <TestResultForm
        ref="testResultFormRef"
        :project-id="queryParams.project_id || 0"
        :project-type="currentProject?.TypeName || ''"
        @saved="handleTestResultSaved"
      />
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSaveTestResult">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Edit } from '@element-plus/icons-vue'
import {
  getProjectListApi,
  getProjectDetailApi,
  type ProjectInfo
} from '@/api/projects'
import { getTestResultApi } from '@/api/test-results'
import TestResultForm from '@/views/projects/components/TestResultForm.vue'

// 查询参数
const queryParams = reactive({
  project_id: undefined as number | undefined,
})

// 数据
const projects = ref<ProjectInfo[]>([])
const currentProject = ref<ProjectInfo | null>(null)
const testResult = ref<any>(null)

// 对话框
const dialogVisible = ref(false)
const submitLoading = ref(false)
const testResultFormRef = ref<InstanceType<typeof TestResultForm>>()

// 过滤后的测试结果（排除不需要显示的字段）
const filteredTestResult = computed(() => {
  if (!testResult.value) return {}
  const excluded = ['ResultID', 'ProjectID_FK']
  return Object.keys(testResult.value)
    .filter(key => !excluded.includes(key))
    .reduce((obj: any, key) => {
      obj[key] = testResult.value[key]
      return obj
    }, {})
})

// 格式化字段标签
function formatFieldLabel(field: string): string {
  const labelMap: Record<string, string> = {
    // 喷墨
    'Ink_Viscosity': '粘度',
    'Ink_Reactivity': '反应活性/固化时间',
    'Ink_ParticleSize': '粒径(nm)',
    'Ink_SurfaceTension': '表面张力(mN/m)',
    'Ink_ColorValue': '色度(Lab*色值)',
    'Ink_RheologyNote': '流变学说明',
    // 涂层
    'Coating_Adhesion': '附着力',
    'Coating_Transparency': '透明度',
    'Coating_SurfaceHardness': '表面硬度',
    'Coating_ChemicalResistance': '耐化学性',
    'Coating_CostEstimate': '成本估算',
    // 3D打印
    'Print3D_Shrinkage': '收缩率',
    'Print3D_YoungsModulus': '杨氏模量(GPa)',
    'Print3D_FlexuralStrength': '弯曲强度(MPa)',
    'Print3D_ShoreHardness': '邵氏硬度',
    'Print3D_ImpactResistance': '冲击强度',
    // 复合材料
    'Composite_FlexuralStrength': '弯曲强度(MPa)',
    'Composite_YoungsModulus': '杨氏模量(GPa)',
    'Composite_ImpactResistance': '冲击强度(kJ/m²)',
    'Composite_ConversionRate': '转化率(%)',
    'Composite_WaterAbsorption': '吸水率(%)',
    // 通用
    'TestDate': '测试日期',
    'Notes': '备注',
  }
  return labelMap[field] || field
}

// 获取项目列表（只显示有测试结果的项目）
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
        has_test_results: true  // 只显示有测试结果的项目
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

// 项目切换
async function handleProjectChange() {
  if (queryParams.project_id) {
    await loadProjectInfo()
    await loadTestResults()
  } else {
    currentProject.value = null
    testResult.value = null
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

// 加载测试结果
async function loadTestResults() {
  if (!queryParams.project_id) return
  try {
    const res = await getTestResultApi(queryParams.project_id)
    testResult.value = res || null
  } catch (error) {
    console.error('加载测试结果失败:', error)
    testResult.value = null
  }
}

// 查询
function handleSearch() {
  loadTestResults()
}

// 重置
function handleReset() {
  queryParams.project_id = undefined
  currentProject.value = null
  testResult.value = null
}

// 编辑
function handleEdit() {
  if (!queryParams.project_id || !currentProject.value) {
    ElMessage.warning('请先选择项目')
    return
  }
  dialogVisible.value = true
}

// 保存测试结果
async function handleSaveTestResult() {
  if (!testResultFormRef.value) return

  submitLoading.value = true
  try {
    await testResultFormRef.value.saveTestResult()
  } catch (error) {
    // 错误处理已在子组件中完成
  } finally {
    submitLoading.value = false
  }
}

// 测试结果保存成功回调
async function handleTestResultSaved() {
  dialogVisible.value = false
  await loadTestResults()
  ElMessage.success('保存成功')
}

// 关闭对话框
function handleDialogClose() {
  // 清理逻辑
}

onMounted(() => {
  getProjects()
})
</script>

<style scoped lang="scss">
.test-results-container {
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

  .test-result-content {
    padding: 16px;
    background-color: #f5f7fa;
    border-radius: 4px;
  }
}
</style>

