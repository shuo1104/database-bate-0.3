<template>
  <div class="test-result-form">
    <!-- 喷墨测试结果表单 -->
    <el-form
      v-if="projectType === '喷墨'"
      ref="inkFormRef"
      :model="inkForm"
      label-width="140px"
    >
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="粘度">
            <el-input v-model="inkForm.Ink_Viscosity" placeholder="请输入粘度" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="反应活性/固化时间">
            <el-input v-model="inkForm.Ink_Reactivity" placeholder="请输入反应活性/固化时间" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="粒径(nm)">
            <el-input v-model="inkForm.Ink_ParticleSize" placeholder="请输入粒径" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="表面张力(mN/m)">
            <el-input v-model="inkForm.Ink_SurfaceTension" placeholder="请输入表面张力" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="色度(Lab*色值)">
            <el-input v-model="inkForm.Ink_ColorValue" placeholder="请输入色度" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="测试日期">
            <el-date-picker
              v-model="inkForm.TestDate"
              type="date"
              placeholder="选择测试日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="流变学说明">
        <el-input
          v-model="inkForm.Ink_RheologyNote"
          type="textarea"
          :rows="2"
          placeholder="请输入流变学说明"
        />
      </el-form-item>
      <el-form-item label="备注">
        <el-input
          v-model="inkForm.Notes"
          type="textarea"
          :rows="2"
          placeholder="请输入备注"
        />
      </el-form-item>
    </el-form>

    <!-- 涂层测试结果表单 -->
    <el-form
      v-else-if="projectType === '涂层'"
      ref="coatingFormRef"
      :model="coatingForm"
      label-width="140px"
    >
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="附着力">
            <el-input v-model="coatingForm.Coating_Adhesion" placeholder="请输入附着力" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="透明度">
            <el-input v-model="coatingForm.Coating_Transparency" placeholder="请输入透明度" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="表面硬度">
            <el-input v-model="coatingForm.Coating_SurfaceHardness" placeholder="请输入表面硬度" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="耐化学性">
            <el-input v-model="coatingForm.Coating_ChemicalResistance" placeholder="请输入耐化学性" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="成本估算(€/kg)">
            <el-input v-model="coatingForm.Coating_CostEstimate" placeholder="请输入成本估算" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="测试日期">
            <el-date-picker
              v-model="coatingForm.TestDate"
              type="date"
              placeholder="选择测试日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="备注">
        <el-input
          v-model="coatingForm.Notes"
          type="textarea"
          :rows="2"
          placeholder="请输入备注"
        />
      </el-form-item>
    </el-form>

    <!-- 3D打印测试结果表单 -->
    <el-form
      v-else-if="projectType === '3D打印'"
      ref="printFormRef"
      :model="printForm"
      label-width="140px"
    >
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="收缩率(%)">
            <el-input v-model="printForm.Print3D_Shrinkage" placeholder="请输入收缩率" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="杨氏模量">
            <el-input v-model="printForm.Print3D_YoungsModulus" placeholder="请输入杨氏模量" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="弯曲强度">
            <el-input v-model="printForm.Print3D_FlexuralStrength" placeholder="请输入弯曲强度" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="邵氏硬度">
            <el-input v-model="printForm.Print3D_ShoreHardness" placeholder="请输入邵氏硬度" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="抗冲击性">
            <el-input v-model="printForm.Print3D_ImpactResistance" placeholder="请输入抗冲击性" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="测试日期">
            <el-date-picker
              v-model="printForm.TestDate"
              type="date"
              placeholder="选择测试日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="备注">
        <el-input
          v-model="printForm.Notes"
          type="textarea"
          :rows="2"
          placeholder="请输入备注"
        />
      </el-form-item>
    </el-form>

    <!-- 复合材料测试结果表单 -->
    <el-form
      v-else-if="projectType === '复合材料'"
      ref="compositeFormRef"
      :model="compositeForm"
      label-width="160px"
    >
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="弯曲强度">
            <el-input v-model="compositeForm.Composite_FlexuralStrength" placeholder="请输入弯曲强度" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="杨氏模量">
            <el-input v-model="compositeForm.Composite_YoungsModulus" placeholder="请输入杨氏模量" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="抗冲击性">
            <el-input v-model="compositeForm.Composite_ImpactResistance" placeholder="请输入抗冲击性" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="转化率(可选)">
            <el-input v-model="compositeForm.Composite_ConversionRate" placeholder="请输入转化率" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="吸水率/溶解度(可选)">
            <el-input v-model="compositeForm.Composite_WaterAbsorption" placeholder="请输入吸水率/溶解度" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="测试日期">
            <el-date-picker
              v-model="compositeForm.TestDate"
              type="date"
              placeholder="选择测试日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="备注">
        <el-input
          v-model="compositeForm.Notes"
          type="textarea"
          :rows="2"
          placeholder="请输入备注"
        />
      </el-form-item>
    </el-form>

    <div v-else class="no-type-tip">
      <el-empty description="请先为项目设置项目类型" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
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

// 加载测试结果
async function loadTestResult() {
  try {
    const res = await getTestResultApi(props.projectId)
    if (res) {
      if (props.projectType === '喷墨') {
        Object.assign(inkForm, res)
      } else if (props.projectType === '涂层') {
        Object.assign(coatingForm, res)
      } else if (props.projectType === '3D打印') {
        Object.assign(printForm, res)
      } else if (props.projectType === '复合材料') {
        Object.assign(compositeForm, res)
      }
    }
  } catch (error) {
    console.error('加载测试结果失败:', error)
  }
}

// 保存测试结果
async function saveTestResult() {
  try {
    if (props.projectType === '喷墨') {
      await saveInkResultApi(props.projectId, inkForm)
    } else if (props.projectType === '涂层') {
      await saveCoatingResultApi(props.projectId, coatingForm)
    } else if (props.projectType === '3D打印') {
      await save3DPrintResultApi(props.projectId, printForm)
    } else if (props.projectType === '复合材料') {
      await saveCompositeResultApi(props.projectId, compositeForm)
    } else {
      ElMessage.warning('未知的项目类型')
      return
    }
    
    ElMessage.success('测试结果保存成功')
    emit('saved')
  } catch (error) {
    ElMessage.error('测试结果保存失败')
    console.error('保存测试结果失败:', error)
  }
}

// 监听项目ID和类型变化，重新加载数据
watch(
  () => [props.projectId, props.projectType],
  () => {
    if (props.projectId && props.projectType) {
      loadTestResult()
    }
  },
  { immediate: true }
)

// 暴露保存方法给父组件
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

