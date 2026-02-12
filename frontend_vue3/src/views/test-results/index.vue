<template>
  <div class="test-results-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>Results</span>
        </div>
      </template>

      <!-- Search Area -->
      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="Project">
          <el-select
            v-model="queryParams.project_id"
            placeholder="Select or search project"
            clearable
            filterable
            :loading="projectsLoading"
            style="width: 400px"
            @change="handleProjectChange"
            @clear="handleReset"
          >
            <el-option
              v-for="project in projects"
              :key="project.ProjectID"
              :label="`${project.ProjectName} (${project.FormulaCode || 'No Code'})`"
              :value="project.ProjectID"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <!-- Project Info Display -->
      <el-alert
        v-if="currentProject"
        :title="`Current Project: ${currentProject.ProjectName} | Formula Code: ${currentProject.FormulaCode} | Project Type: ${currentProject.TypeName || '-'}`"
        type="info"
        :closable="false"
        style="margin-bottom: 16px"
      />

      <!-- Action Buttons -->
      <div class="toolbar">
        <el-button
          type="primary"
          :icon="Edit"
          @click="handleEdit"
          :disabled="!queryParams.project_id || !currentProject"
        >
          Edit Results
        </el-button>
      </div>

      <!-- Test Results Display -->
      <div v-if="testResult" class="test-result-content">
        <el-descriptions :column="2" border>
          <template v-for="(value, key) in filteredTestResult" :key="key">
            <el-descriptions-item :label="formatFieldLabel(String(key))">
              {{ value || '-' }}
            </el-descriptions-item>
          </template>
        </el-descriptions>
      </div>
      <el-empty v-else-if="queryParams.project_id" description="No results yet, click the button above to add" />
      <el-empty v-else description="Please select a project to view results" />
    </el-card>

    <!-- Test Results Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      title="Edit Results"
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
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSaveTestResult">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Edit } from '@element-plus/icons-vue'
import {
  getProjectListApi,
  getProjectDetailApi,
  type ProjectInfo
} from '@/api/projects'
import { getTestResultApi } from '@/api/test-results'
import TestResultForm from '@/views/projects/components/TestResultForm.vue'

// Query parameters
const queryParams = reactive({
  project_id: undefined as number | undefined,
})

// Data
const projectsLoading = ref(false)
const projects = ref<ProjectInfo[]>([])
const currentProject = ref<ProjectInfo | null>(null)
const testResult = ref<any>(null)

// Dialog
const dialogVisible = ref(false)
const submitLoading = ref(false)
const testResultFormRef = ref<InstanceType<typeof TestResultForm>>()

// Filtered test results (exclude fields not to display)
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

// Format field label
function formatFieldLabel(field: string): string {
  const labelMap: Record<string, string> = {
    // Inkjet
    'Ink_Viscosity': 'Viscosity',
    'Ink_Reactivity': 'Reactivity/Curing Time',
    'Ink_ParticleSize': 'Particle Size (nm)',
    'Ink_SurfaceTension': 'Surface Tension (mN/m)',
    'Ink_ColorValue': 'Colorimetry (Lab*)',
    'Ink_RheologyNote': 'Rheology Notes',
    // Coating
    'Coating_Adhesion': 'Adhesion',
    'Coating_Transparency': 'Transparency',
    'Coating_SurfaceHardness': 'Surface Hardness',
    'Coating_ChemicalResistance': 'Chemical Resistance',
    'Coating_CostEstimate': 'Cost Estimate',
    // 3D Printing
    'Print3D_Shrinkage': 'Shrinkage',
    'Print3D_YoungsModulus': "Young's Modulus (GPa)",
    'Print3D_FlexuralStrength': 'Flexural Strength (MPa)',
    'Print3D_ShoreHardness': 'Shore Hardness',
    'Print3D_ImpactResistance': 'Impact Resistance',
    // Composite
    'Composite_FlexuralStrength': 'Flexural Strength (MPa)',
    'Composite_YoungsModulus': "Young's Modulus (GPa)",
    'Composite_ImpactResistance': 'Impact Resistance (kJ/m²)',
    'Composite_ConversionRate': 'Degree of Conversion (%)',
    'Composite_WaterAbsorption': 'Water Absorption (%)',
    // General
    'TestDate': 'Test Date',
    'Notes': 'Notes',
  }
  return labelMap[field] || field
}

// Search projects by keyword (remote search)
async function searchProjects(query: string) {
  if (!query || query.trim() === '') {
    // If empty, load first 50 projects as default
    await loadDefaultProjects()
    return
  }

  projectsLoading.value = true
  try {
    const res = await getProjectListApi({
      page: 1,
      page_size: 50,
      keyword: query
    })
    projects.value = res.list || res.items || []
  } catch (error) {
    console.error('Failed to search projects:', error)
    ElMessage.error('Failed to search projects')
  } finally {
    projectsLoading.value = false
  }
}

// Load default projects (first 50)
async function loadDefaultProjects() {
  projectsLoading.value = true
  try {
    const res = await getProjectListApi({
      page: 1,
      page_size: 50
    })
    projects.value = res.list || res.items || []
  } catch (error) {
    console.error('Failed to get project list:', error)
  } finally {
    projectsLoading.value = false
  }
}

// Project change
async function handleProjectChange() {
  if (queryParams.project_id) {
    await loadProjectInfo()
    await loadTestResults()
  } else {
    currentProject.value = null
    testResult.value = null
  }
}

// Load project info
async function loadProjectInfo() {
  if (!queryParams.project_id) return
  try {
    currentProject.value = await getProjectDetailApi(queryParams.project_id)
  } catch (error) {
    console.error('Failed to get project info:', error)
  }
}

// Load test results
async function loadTestResults() {
  if (!queryParams.project_id) return
  try {
    const res = await getTestResultApi(queryParams.project_id)
    testResult.value = res || null
  } catch (error) {
    console.error('Failed to load test results:', error)
    testResult.value = null
  }
}

// Reset
function handleReset() {
  queryParams.project_id = undefined
  currentProject.value = null
  testResult.value = null
}

// Edit
function handleEdit() {
  if (!queryParams.project_id || !currentProject.value) {
    ElMessage.warning('Please select a project first')
    return
  }
  dialogVisible.value = true
}

// Save test results
async function handleSaveTestResult() {
  if (!testResultFormRef.value) return

  submitLoading.value = true
  try {
    await testResultFormRef.value.saveTestResult()
  } catch (error) {
    // Error handling completed in child component
  } finally {
    submitLoading.value = false
  }
}

// Test result saved callback
async function handleTestResultSaved() {
  dialogVisible.value = false
  await loadTestResults()
  ElMessage.success('Saved successfully')
}

// Close dialog
function handleDialogClose() {
  // Cleanup logic
}

onMounted(() => {
  loadDefaultProjects()  // Load first 50 projects by default
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
