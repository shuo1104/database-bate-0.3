<template>
  <div class="agent-review">
    <div class="review-summary">
      <div class="summary-item">
        <span class="label">Current Page Records</span>
        <span class="value">{{ currentPageTotal }}</span>
      </div>
      <div class="summary-item">
        <span class="label">Pending Review</span>
        <span class="value warning">{{ pendingCount }}</span>
      </div>
      <div class="summary-item">
        <span class="label">Manually Reviewed</span>
        <span class="value success">{{ manualReviewedCount }}</span>
      </div>
    </div>

    <el-form :inline="true" :model="table.queryParams" class="search-form">
      <el-form-item label="Review Status">
        <el-select v-model="table.queryParams.review_status" style="width: 150px">
          <el-option label="All" value="" />
          <el-option label="Pending Review" value="pending_review" />
          <el-option label="Approved" value="approved" />
          <el-option label="Rejected" value="rejected" />
          <el-option label="Modified" value="modified" />
        </el-select>
      </el-form-item>

      <el-form-item label="Task ID">
        <el-input
          v-model="table.queryParams.task_id"
          clearable
          placeholder="e.g. 1001"
          style="width: 130px"
        />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="table.handleQuery">Search</el-button>
        <el-button @click="handleReset">Reset</el-button>
      </el-form-item>
    </el-form>

    <el-table
      v-loading="table.loading.value"
      :data="table.tableData.value"
      border
      stripe
      class="review-table"
    >
      <el-table-column prop="record_id" label="Review Record ID" width="120" />

      <el-table-column prop="source_file_name" label="File Name" min-width="160">
        <template #default="{ row }">
          {{ row.source_file_name || '-' }}
        </template>
      </el-table-column>

      <el-table-column prop="task_id" label="Ingestion Task ID" width="130">
        <template #default="{ row }">
          {{ row.task_id ? `#${row.task_id}` : '-' }}
        </template>
      </el-table-column>

      <el-table-column prop="overall_confidence" label="Confidence" width="100">
        <template #default="{ row }">
          <span v-if="typeof row.overall_confidence === 'number'">
            {{ Math.round(row.overall_confidence * 100) }}%
          </span>
          <span v-else>-</span>
        </template>
      </el-table-column>

      <el-table-column prop="review_status" label="Status" width="160">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row)">
            {{ statusLabel(row) }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="extracted_data" label="Extracted Data" min-width="260">
        <template #default="{ row }">
          <el-popover
            placement="top-start"
            trigger="hover"
            :width="560"
            popper-class="extracted-data-popover"
          >
            <template #reference>
              <span class="extracted-data-preview">{{ formatDataPreview(row.extracted_data) }}</span>
            </template>
            <pre class="extracted-data-detail">{{ formatDataDetail(row.extracted_data) }}</pre>
          </el-popover>
        </template>
      </el-table-column>

      <el-table-column prop="created_at" label="Created At" width="170">
        <template #default="{ row }">
          {{ formatDateTime(row.created_at) }}
        </template>
      </el-table-column>

      <el-table-column label="Actions" width="320" fixed="right">
        <template #default="{ row }">
          <el-button link class="action-btn" type="success" :disabled="isManuallyReviewed(row)" @click="handleApprove(row)">Approve</el-button>
          <el-button link class="action-btn" type="danger" :disabled="isManuallyReviewed(row)" @click="handleReject(row)">Reject</el-button>
          <el-button link class="action-btn" type="primary" :disabled="isManuallyReviewed(row)" @click="openModifyDialog(row)">Modify</el-button>
          <el-button link class="action-btn" type="danger" @click="handleDelete(row)">Delete</el-button>
          <el-tag v-if="isManuallyReviewed(row)" size="small" type="info">Manually Reviewed</el-tag>
        </template>
      </el-table-column>
    </el-table>

    <Pagination
      v-show="table.total.value > 0"
      :total="table.total.value"
      v-model:page="table.queryParams.page"
      v-model:limit="table.queryParams.page_size"
      @pagination="table.fetchData"
    />

    <el-dialog
      v-model="modifyDialogVisible"
      title="Modify Extracted Result"
      width="680px"
      :close-on-click-modal="false"
    >
      <el-form label-width="90px">
        <el-form-item label="JSON Data">
          <el-input
            v-model="modifyJsonText"
            type="textarea"
            :rows="12"
            resize="none"
            placeholder="Please enter valid JSON"
          />
        </el-form-item>

        <el-form-item label="Comment">
          <el-input
            v-model="modifyComment"
            type="textarea"
            :rows="3"
            resize="none"
            placeholder="Optional comment"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="modifyDialogVisible = false">Cancel</el-button>
        <el-button type="primary" :loading="submitLoading" @click="submitModify">
          Submit Changes
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  deleteReviewRecordApi,
  getReviewListApi,
  reviewRecordApi,
  type AgentReviewListParams,
  type AgentReviewRecord,
  type AgentReviewStatus,
  type AgentReviewAction,
} from '@/api/agent'
import { useTable } from '@/composables/useTable'

function fetchReviewList(params: any) {
  const normalized: AgentReviewListParams = {
    page: params.page,
    page_size: params.page_size,
  }

  if (params.review_status) {
    normalized.review_status = params.review_status as AgentReviewStatus
  }

  if (params.task_id !== '' && params.task_id !== null && params.task_id !== undefined) {
    const taskId = Number(params.task_id)
    if (!Number.isNaN(taskId)) {
      normalized.task_id = taskId
    }
  }

  return getReviewListApi(normalized)
}

const table = useTable<AgentReviewRecord>(fetchReviewList as any, {
  defaultPageSize: 10,
})

Object.assign(table.queryParams, {
  review_status: '',
  task_id: '',
})

const modifyDialogVisible = ref(false)
const submitLoading = ref(false)
const currentRecordId = ref<number | null>(null)
const modifyJsonText = ref('')
const modifyComment = ref('')

const currentPageTotal = computed(() => table.tableData.value.length)

const pendingCount = computed(() => {
  return table.tableData.value.filter((item) => item.review_status === 'pending_review').length
})

const manualReviewedCount = computed(() => {
  return table.tableData.value.filter((item) => isManuallyReviewed(item)).length
})

function statusLabel(record: AgentReviewRecord) {
  if (record.review_status === 'approved' && !isManuallyReviewed(record)) {
    return 'Auto Approved (Needs Review)'
  }
  if (record.review_status === 'pending_review') {
    return 'Pending Review'
  }
  if (record.review_status === 'approved') {
    return 'Approved'
  }
  if (record.review_status === 'rejected') {
    return 'Rejected'
  }
  return 'Modified'
}

function statusTagType(record: AgentReviewRecord) {
  if (record.review_status === 'approved' && !isManuallyReviewed(record)) {
    return 'warning'
  }
  if (record.review_status === 'pending_review') {
    return 'warning'
  }
  if (record.review_status === 'approved') {
    return 'success'
  }
  if (record.review_status === 'rejected') {
    return 'danger'
  }
  return 'info'
}

function formatDateTime(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return '-'
  }

  return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`
}

function stringifyExtractedData(data: unknown, pretty = false) {
  if (!data || typeof data !== 'object') {
    return '-'
  }

  try {
    const plain = JSON.stringify(data, null, pretty ? 2 : 0)
    return plain || '-'
  } catch {
    return '-'
  }
}

function formatDataPreview(data: unknown) {
  const plain = stringifyExtractedData(data)
  if (!plain) {
    return '-'
  }

  return plain.length > 120 ? `${plain.slice(0, 120)}...` : plain
}

function formatDataDetail(data: unknown) {
  return stringifyExtractedData(data, true)
}

function isManuallyReviewed(record: Pick<AgentReviewRecord, 'reviewed_by_user_id'>) {
  return typeof record.reviewed_by_user_id === 'number' && record.reviewed_by_user_id > 0
}

function handleReset() {
  table.queryParams.review_status = ''
  table.queryParams.task_id = ''
  table.handleQuery()
}

async function submitReviewAction(record: AgentReviewRecord, action: AgentReviewAction) {
  submitLoading.value = true
  try {
    await reviewRecordApi(record.record_id, {
      action,
    })
    ElMessage.success('Action completed')
    await table.fetchData()
  } catch (error) {
    console.error('Failed to review record:', error)
  } finally {
    submitLoading.value = false
  }
}

function handleApprove(record: AgentReviewRecord) {
  ElMessageBox.confirm('Confirm approving this record?', 'Review Confirmation', {
    type: 'warning',
  }).then(async () => {
    await submitReviewAction(record, 'approved')
  }).catch(() => {})
}

function handleReject(record: AgentReviewRecord) {
  ElMessageBox.confirm('Confirm rejecting this record?', 'Review Confirmation', {
    type: 'warning',
  }).then(async () => {
    await submitReviewAction(record, 'rejected')
  }).catch(() => {})
}

function handleDelete(record: AgentReviewRecord) {
  ElMessageBox.confirm(
    `Confirm deleting review record #${record.record_id}?`,
    'Delete Confirmation',
    {
      type: 'warning',
      confirmButtonText: 'Delete',
    }
  ).then(async () => {
    submitLoading.value = true
    try {
      await deleteReviewRecordApi(record.record_id)
      ElMessage.success('Record deleted')
      await table.fetchData()
    } catch (error) {
      console.error('Failed to delete review record:', error)
    } finally {
      submitLoading.value = false
    }
  }).catch(() => {})
}

function openModifyDialog(record: AgentReviewRecord) {
  currentRecordId.value = record.record_id
  modifyJsonText.value = JSON.stringify(record.extracted_data, null, 2)
  modifyComment.value = ''
  modifyDialogVisible.value = true
}

async function submitModify() {
  if (!currentRecordId.value) {
    return
  }

  let parsedJson: Record<string, any>
  try {
    parsedJson = JSON.parse(modifyJsonText.value)
  } catch {
    ElMessage.error('Invalid JSON format. Please check and try again.')
    return
  }

  submitLoading.value = true
  try {
    await reviewRecordApi(currentRecordId.value, {
      action: 'modified',
      modified_data: parsedJson,
      comment: modifyComment.value || undefined,
    })

    ElMessage.success('Changes submitted')
    modifyDialogVisible.value = false
    await table.fetchData()
  } catch (error) {
    console.error('Failed to submit modified data:', error)
  } finally {
    submitLoading.value = false
  }
}

table.fetchData()
</script>

<style scoped lang="scss">
.agent-review {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.review-summary {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  padding: 8px 10px;
  border: 1px solid #d7e4ee;
  border-radius: 10px;
  background: linear-gradient(180deg, #fdfefe 0%, #f4f9fd 100%);

  .summary-item {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: #567082;
    font-size: 12px;

    .value {
      font-size: 14px;
      font-weight: 700;
      color: #345469;
    }

    .warning {
      color: #b6781b;
    }

    .success {
      color: #2f7d49;
    }
  }
}

.search-form {
  margin-bottom: 10px;
  padding: 8px 10px 0;
  border: 1px solid #d8e5ef;
  border-radius: 10px;
  background: #ffffff;
}

.review-table {
  flex: 1;

  :deep(.el-table__cell) {
    padding: 8px 0;
  }

  :deep(.el-table__row:hover > td) {
    background: #f4f9fd !important;
  }
}

.action-btn {
  margin-right: 2px;
}

.extracted-data-preview {
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: pointer;
  color: #35556a;
}

.extracted-data-detail {
  margin: 0;
  max-height: 320px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 12px;
  line-height: 1.45;
  color: #223643;
}

:deep(.extracted-data-popover) {
  max-width: min(90vw, 640px);
}

@media (max-width: 768px) {
  .review-summary {
    flex-wrap: wrap;
    gap: 8px 12px;
  }
}
</style>
