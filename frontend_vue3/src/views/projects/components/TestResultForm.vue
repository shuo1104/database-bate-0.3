<template>
  <div class="test-result-form">
    <!-- Inkjet Test Results Form -->
    <el-form
      v-if="isInkjetType"
      ref="inkFormRef"
      :model="inkForm"
      label-width="200px"
    >
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="Viscosity">
            <el-input v-model="inkForm.Ink_Viscosity" placeholder="Enter viscosity" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Reactivity/Cure Time">
            <el-input v-model="inkForm.Ink_Reactivity" placeholder="Enter reactivity/cure time" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="Particle Size (nm)">
            <el-input v-model="inkForm.Ink_ParticleSize" placeholder="Enter particle size" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Surface Tension (mN/m)">
            <el-input v-model="inkForm.Ink_SurfaceTension" placeholder="Enter surface tension" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="Colorimetry (Lab*)">
            <el-input v-model="inkForm.Ink_ColorValue" placeholder="Enter colorimetry" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Test Date">
            <el-date-picker
              v-model="inkForm.TestDate"
              type="date"
              placeholder="Select test date"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="Rheology Notes">
        <el-input
          v-model="inkForm.Ink_RheologyNote"
          type="textarea"
          :rows="2"
          placeholder="Enter rheology notes"
        />
      </el-form-item>
      <el-form-item label="Remarks">
        <el-input
          v-model="inkForm.Notes"
          type="textarea"
          :rows="2"
          placeholder="Enter remarks"
        />
      </el-form-item>
    </el-form>

    <!-- Coating Test Results Form -->
    <el-form
      v-else-if="isCoatingType"
      ref="coatingFormRef"
      :model="coatingForm"
      label-width="200px"
    >
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="Adhesion">
            <el-input v-model="coatingForm.Coating_Adhesion" placeholder="Enter adhesion" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Transparency">
            <el-input v-model="coatingForm.Coating_Transparency" placeholder="Enter transparency" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="Surface Hardness">
            <el-input v-model="coatingForm.Coating_SurfaceHardness" placeholder="Enter surface hardness" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Chemical Resistance">
            <el-input v-model="coatingForm.Coating_ChemicalResistance" placeholder="Enter chemical resistance" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="Cost Estimate (€/kg)">
            <el-input v-model="coatingForm.Coating_CostEstimate" placeholder="Enter cost estimate" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Test Date">
            <el-date-picker
              v-model="coatingForm.TestDate"
              type="date"
              placeholder="Select test date"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="Remarks">
        <el-input
          v-model="coatingForm.Notes"
          type="textarea"
          :rows="2"
          placeholder="Enter remarks"
        />
      </el-form-item>
    </el-form>

    <!-- 3D Printing Test Results Form -->
    <el-form
      v-else-if="is3DPrintType"
      ref="printFormRef"
      :model="printForm"
      label-width="200px"
    >
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="Shrinkage (%)">
            <el-input v-model="printForm.Print3D_Shrinkage" placeholder="Enter shrinkage" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Young's Modulus">
            <el-input v-model="printForm.Print3D_YoungsModulus" placeholder="Enter Young's modulus" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="Flexural Strength">
            <el-input v-model="printForm.Print3D_FlexuralStrength" placeholder="Enter flexural strength" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Shore Hardness">
            <el-input v-model="printForm.Print3D_ShoreHardness" placeholder="Enter shore hardness" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="Impact Resistance">
            <el-input v-model="printForm.Print3D_ImpactResistance" placeholder="Enter impact resistance" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Test Date">
            <el-date-picker
              v-model="printForm.TestDate"
              type="date"
              placeholder="Select test date"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="Remarks">
        <el-input
          v-model="printForm.Notes"
          type="textarea"
          :rows="2"
          placeholder="Enter remarks"
        />
      </el-form-item>
    </el-form>

    <!-- Composite Material Test Results Form -->
    <el-form
      v-else-if="isCompositeType"
      ref="compositeFormRef"
      :model="compositeForm"
      label-width="220px"
    >
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="Flexural Strength">
            <el-input v-model="compositeForm.Composite_FlexuralStrength" placeholder="Enter flexural strength" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Young's Modulus">
            <el-input v-model="compositeForm.Composite_YoungsModulus" placeholder="Enter Young's modulus" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="Impact Resistance">
            <el-input v-model="compositeForm.Composite_ImpactResistance" placeholder="Enter impact resistance" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Degree of Conversion (%)">
            <el-input v-model="compositeForm.Composite_ConversionRate" placeholder="Enter degree of conversion" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="Water Absorption/Solubility">
            <el-input v-model="compositeForm.Composite_WaterAbsorption" placeholder="Enter water absorption/solubility" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Test Date">
            <el-date-picker
              v-model="compositeForm.TestDate"
              type="date"
              placeholder="Select test date"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="Remarks">
        <el-input
          v-model="compositeForm.Notes"
          type="textarea"
          :rows="2"
          placeholder="Enter remarks"
        />
      </el-form-item>
    </el-form>

    <div v-else class="no-type-tip">
      <el-empty description="Please set a project type first" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage, type FormInstance } from 'element-plus'
import {
  getTestResultApi,
  saveInkResultApi,
  saveCoatingResultApi,
  save3DPrintResultApi,
  saveCompositeResultApi,
  type TestResultInk,
  type TestResultCoating,
  type TestResult3DPrint,
  type TestResultComposite
} from '@/api/test-results'

interface Props {
  projectId: number
  projectType: string
}

const props = defineProps<Props>()
const emit = defineEmits(['saved'])

// Computed properties to check project type (支持中英文)
const isInkjetType = computed(() => {
  return props.projectType === '喷墨' || props.projectType === 'Inkjet'
})

const isCoatingType = computed(() => {
  return props.projectType === '涂层' || props.projectType === 'Coating'
})

const is3DPrintType = computed(() => {
  return props.projectType === '3D打印' || props.projectType === '3D Printing'
})

const isCompositeType = computed(() => {
  return props.projectType === '复合材料' || props.projectType === 'Composite'
})

const inkFormRef = ref<FormInstance>()
const coatingFormRef = ref<FormInstance>()
const printFormRef = ref<FormInstance>()
const compositeFormRef = ref<FormInstance>()

const inkForm = reactive<Partial<TestResultInk>>({
  Ink_Viscosity: '',
  Ink_Reactivity: '',
  Ink_ParticleSize: '',
  Ink_SurfaceTension: '',
  Ink_ColorValue: '',
  Ink_RheologyNote: '',
  TestDate: '',
  Notes: '',
})

const coatingForm = reactive<Partial<TestResultCoating>>({
  Coating_Adhesion: '',
  Coating_Transparency: '',
  Coating_SurfaceHardness: '',
  Coating_ChemicalResistance: '',
  Coating_CostEstimate: '',
  TestDate: '',
  Notes: '',
})

const printForm = reactive<Partial<TestResult3DPrint>>({
  Print3D_Shrinkage: '',
  Print3D_YoungsModulus: '',
  Print3D_FlexuralStrength: '',
  Print3D_ShoreHardness: '',
  Print3D_ImpactResistance: '',
  TestDate: '',
  Notes: '',
})

const compositeForm = reactive<Partial<TestResultComposite>>({
  Composite_FlexuralStrength: '',
  Composite_YoungsModulus: '',
  Composite_ImpactResistance: '',
  Composite_ConversionRate: '',
  Composite_WaterAbsorption: '',
  TestDate: '',
  Notes: '',
})

// Load test results
async function loadTestResult() {
  try {
    const res = await getTestResultApi(props.projectId)
    if (res) {
      if (isInkjetType.value) {
        Object.assign(inkForm, res)
      } else if (isCoatingType.value) {
        Object.assign(coatingForm, res)
      } else if (is3DPrintType.value) {
        Object.assign(printForm, res)
      } else if (isCompositeType.value) {
        Object.assign(compositeForm, res)
      }
    }
  } catch (error) {
    console.error('Failed to load test results:', error)
  }
}

// Save test results
async function saveTestResult() {
  try {
    if (isInkjetType.value) {
      await saveInkResultApi(props.projectId, inkForm)
    } else if (isCoatingType.value) {
      await saveCoatingResultApi(props.projectId, coatingForm)
    } else if (is3DPrintType.value) {
      await save3DPrintResultApi(props.projectId, printForm)
    } else if (isCompositeType.value) {
      await saveCompositeResultApi(props.projectId, compositeForm)
    } else {
      ElMessage.warning('Unknown project type')
      return
    }
    
    ElMessage.success('Test results saved successfully')
    emit('saved')
  } catch (error) {
    ElMessage.error('Failed to save test results')
    console.error('Failed to save test results:', error)
  }
}

// Watch for project ID and type changes, reload data
watch(
  () => [props.projectId, props.projectType],
  () => {
    if (props.projectId && props.projectType) {
      loadTestResult()
    }
  },
  { immediate: true }
)

// Expose save method to parent component
defineExpose({
  saveTestResult
})
</script>

<style scoped lang="scss">
.test-result-form {
  padding: 10px 0;

  .no-type-tip {
    padding: 40px 0;
    text-align: center;
  }
}
</style>

