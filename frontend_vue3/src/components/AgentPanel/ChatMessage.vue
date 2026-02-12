<template>
  <div class="chat-message" :class="[`role-${message.role}`, { failed: message.failed }]">
    <div v-if="message.role !== 'system'" class="avatar">
      {{ message.role === 'user' ? 'U' : 'A' }}
    </div>

    <div class="bubble-wrapper">
      <div class="meta">
        <span class="role-label">{{ roleLabel }}</span>
        <span class="time">{{ formattedTime }}</span>
        <el-tag v-if="message.pending" size="small" type="info">Sending</el-tag>
        <el-tag v-if="message.failed" size="small" type="danger">Failed</el-tag>
      </div>

      <div class="bubble" :class="{ 'is-failed': message.failed }">
        <div v-if="message.file_name" class="file-name">Attachment: {{ message.file_name }}</div>

        <div
          v-if="message.role === 'agent'"
          class="markdown-body"
          v-html="renderedContent"
        />
        <div v-else class="plain-text">{{ message.content }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { AgentChatMessage } from '@/store/modules/agent'

interface Props {
  message: AgentChatMessage
}

const props = defineProps<Props>()

const roleLabel = computed(() => {
  if (props.message.role === 'user') {
    return 'Me'
  }

  if (props.message.role === 'agent') {
    return 'Agent'
  }

  return 'System'
})

const formattedTime = computed(() => {
  const date = new Date(props.message.created_at)
  if (Number.isNaN(date.getTime())) {
    return '--:--'
  }

  const hour = `${date.getHours()}`.padStart(2, '0')
  const minute = `${date.getMinutes()}`.padStart(2, '0')
  return `${hour}:${minute}`
})

function escapeHtml(input: string) {
  return input
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function formatInlineMarkdown(input: string) {
  let output = input
  output = output.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  output = output.replace(/\*(.+?)\*/g, '<em>$1</em>')
  output = output.replace(/`([^`]+)`/g, '<code>$1</code>')
  output = output.replace(
    /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
    '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
  )
  return output
}

function splitPipeRow(line: string) {
  return line
    .trim()
    .replace(/^\|/, '')
    .replace(/\|$/, '')
    .split('|')
    .map((cell) => formatInlineMarkdown(cell.trim()))
}

function isTableSeparator(line: string) {
  const normalized = line.trim().replace(/^\|/, '').replace(/\|$/, '')
  const segments = normalized.split('|').map((segment) => segment.trim())
  return segments.length > 0 && segments.every((segment) => /^:?-{3,}:?$/.test(segment))
}

function getTableAlignments(separatorLine: string) {
  return separatorLine
    .trim()
    .replace(/^\|/, '')
    .replace(/\|$/, '')
    .split('|')
    .map((segment) => {
      const trimmed = segment.trim()
      if (trimmed.startsWith(':') && trimmed.endsWith(':')) {
        return 'center'
      }
      if (trimmed.endsWith(':')) {
        return 'right'
      }
      return 'left'
    })
}

function buildTableBlock(lines: string[], startIndex: number) {
  const headers = splitPipeRow(lines[startIndex])
  if (!headers.length) {
    return {
      html: `<p>${formatInlineMarkdown(lines[startIndex].trim())}</p>`,
      nextIndex: startIndex + 1,
    }
  }

  const alignments = getTableAlignments(lines[startIndex + 1])
  const rows: string[][] = []

  let cursor = startIndex + 2
  while (cursor < lines.length) {
    const line = lines[cursor]
    if (!line.trim() || !line.includes('|')) {
      break
    }

    const cells = splitPipeRow(line)
    if (cells.length < headers.length) {
      cells.push(...Array.from({ length: headers.length - cells.length }, () => ''))
    }

    if (cells.length > headers.length) {
      const head = cells.slice(0, headers.length - 1)
      const tail = cells.slice(headers.length - 1).join(' | ')
      rows.push([...head, tail])
      cursor += 1
      continue
    }

    rows.push(cells)
    cursor += 1
  }

  const headHtml = headers
    .map((cell, index) => `<th class="align-${alignments[index] || 'left'}">${cell}</th>`)
    .join('')

  const bodyHtml = rows
    .map((cells) => {
      const rowCells = headers.map((_, index) => cells[index] || '')
      return `<tr>${rowCells
        .map((cell, index) => `<td class="align-${alignments[index] || 'left'}">${cell}</td>`)
        .join('')}</tr>`
    })
    .join('')

  return {
    html: `<div class="table-wrap"><table><thead><tr>${headHtml}</tr></thead><tbody>${bodyHtml}</tbody></table></div>`,
    nextIndex: cursor,
  }
}

function buildListBlock(lines: string[], startIndex: number) {
  const items: string[] = []
  let cursor = startIndex

  while (cursor < lines.length) {
    const trimmed = lines[cursor].trim()
    const match = trimmed.match(/^[-*]\s+(.+)$/)
    if (!match) {
      break
    }

    items.push(`<li>${formatInlineMarkdown(match[1])}</li>`)
    cursor += 1
  }

  return {
    html: `<ul>${items.join('')}</ul>`,
    nextIndex: cursor,
  }
}

function renderMarkdown(input: string) {
  if (!input.trim()) {
    return ''
  }

  const codeBlocks: string[] = []

  const escaped = escapeHtml(input).replace(/```([\s\S]*?)```/g, (_, code: string) => {
    const index = codeBlocks.push(`<pre><code>${code}</code></pre>`) - 1
    return `@@CODE_BLOCK_${index}@@`
  })

  const lines = escaped.split('\n')
  const blocks: string[] = []

  for (let index = 0; index < lines.length;) {
    const currentLine = lines[index]
    const currentTrimmed = currentLine.trim()

    if (!currentTrimmed) {
      index += 1
      continue
    }

    if (currentLine.includes('|') && index + 1 < lines.length && isTableSeparator(lines[index + 1])) {
      const tableBlock = buildTableBlock(lines, index)
      blocks.push(tableBlock.html)
      index = tableBlock.nextIndex
      continue
    }

    if (/^[-*]\s+/.test(currentTrimmed)) {
      const listBlock = buildListBlock(lines, index)
      blocks.push(listBlock.html)
      index = listBlock.nextIndex
      continue
    }

    if (/^###\s+/.test(currentTrimmed)) {
      blocks.push(`<h3>${formatInlineMarkdown(currentTrimmed.replace(/^###\s+/, ''))}</h3>`)
      index += 1
      continue
    }

    if (/^##\s+/.test(currentTrimmed)) {
      blocks.push(`<h2>${formatInlineMarkdown(currentTrimmed.replace(/^##\s+/, ''))}</h2>`)
      index += 1
      continue
    }

    if (/^#\s+/.test(currentTrimmed)) {
      blocks.push(`<h1>${formatInlineMarkdown(currentTrimmed.replace(/^#\s+/, ''))}</h1>`)
      index += 1
      continue
    }

    const paragraphLines: string[] = [currentTrimmed]
    index += 1

    while (index < lines.length) {
      const nextLine = lines[index]
      const nextTrimmed = nextLine.trim()

      if (!nextTrimmed) {
        break
      }

      if (/^#{1,3}\s+/.test(nextTrimmed) || /^[-*]\s+/.test(nextTrimmed)) {
        break
      }

      if (nextLine.includes('|') && index + 1 < lines.length && isTableSeparator(lines[index + 1])) {
        break
      }

      paragraphLines.push(nextTrimmed)
      index += 1
    }

    blocks.push(`<p>${paragraphLines.map((line) => formatInlineMarkdown(line)).join('<br />')}</p>`)
  }

  let output = blocks.join('')

  output = output.replace(/@@CODE_BLOCK_(\d+)@@/g, (_, index: string) => {
    return codeBlocks[Number(index)] || ''
  })

  return output
}

const renderedContent = computed(() => {
  return renderMarkdown(props.message.content || '')
})
</script>

<style scoped lang="scss">
.chat-message {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  margin-bottom: 10px;
  padding-inline: 2px;
  animation: message-in 0.2s ease;

  &.role-system {
    justify-content: center;

    .bubble-wrapper {
      max-width: 100%;
    }

    .meta {
      justify-content: center;
    }

    .bubble {
      background: #f4f8fb;
      border: 1px dashed #c4d8e8;
      text-align: center;
    }
  }

  &.role-user {
    flex-direction: row-reverse;

    .meta {
      justify-content: flex-end;
    }

    .bubble {
      background: linear-gradient(135deg, #e6f3fb 0%, #f2f9fd 100%);
      border-color: #c4deef;
    }

    .avatar {
      color: #245b7d;
      background: #dcecf8;
      border-color: #c3dbed;
    }
  }

  &.role-agent {
    .bubble {
      background: #ffffff;
    }

    .avatar {
      color: #2f546d;
      background: #e7f1f8;
      border-color: #cedfe9;
    }
  }

  &.failed {
    .bubble {
      border-color: #e4bbbb;
      background: #fff7f7;
    }
  }
}

.avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: #265775;
  background: #e3eff8;
  border: 1px solid #c6dae9;
  flex-shrink: 0;
}

.bubble-wrapper {
  max-width: min(86%, 780px);
}

.meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;

  .role-label {
    font-size: 12px;
    color: #4f677b;
    font-weight: 600;
  }

  .time {
    font-size: 12px;
    color: #88a0b3;
  }
}

.bubble {
  border: 1px solid #d5e4ef;
  border-radius: 12px;
  padding: 9px 11px;
  box-shadow: 0 1px 2px rgba(12, 44, 73, 0.04);

  &.is-failed {
    box-shadow: 0 2px 8px rgba(161, 71, 71, 0.1);
  }
}

.file-name {
  font-size: 12px;
  color: #4f677b;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px dashed #d7e5ef;
}

.plain-text {
  color: #2f4354;
  font-size: 13px;
  line-height: 1.65;
  white-space: pre-wrap;
  word-break: break-word;
}

.markdown-body {
  color: #2f4354;
  font-size: 13px;
  line-height: 1.65;
  word-break: break-word;

  :deep(p) {
    margin: 8px 0;
  }

  :deep(ul) {
    margin: 8px 0;
    padding-left: 20px;
  }

  :deep(li) {
    margin: 4px 0;
  }

  :deep(h1),
  :deep(h2),
  :deep(h3) {
    margin: 6px 0;
    line-height: 1.3;
    color: #1f3347;
  }

  :deep(h1) {
    font-size: 18px;
  }

  :deep(h2) {
    font-size: 16px;
  }

  :deep(h3) {
    font-size: 14px;
  }

  :deep(a) {
    color: #0f82c5;
    text-decoration: none;
  }

  :deep(code) {
    background: #f3f8fc;
    border: 1px solid #d5e4ef;
    border-radius: 6px;
    padding: 1px 6px;
    font-family: 'JetBrains Mono', 'Consolas', monospace;
    font-size: 12px;
  }

  :deep(pre) {
    margin: 8px 0;
    padding: 10px;
    border-radius: 10px;
    border: 1px solid #d5e4ef;
    background: #f7fafc;
    overflow-x: auto;
  }

  :deep(pre code) {
    border: none;
    padding: 0;
    background: transparent;
  }

  :deep(.table-wrap) {
    margin: 10px 0;
    overflow-x: auto;
  }

  :deep(table) {
    width: 100%;
    min-width: 440px;
    border-collapse: separate;
    border-spacing: 0;
    border: 1px solid #d5e4ef;
    border-radius: 10px;
    overflow: hidden;
    background: #ffffff;
  }

  :deep(th),
  :deep(td) {
    padding: 7px 10px;
    font-size: 12px;
    line-height: 1.55;
  }

  :deep(th) {
    background: #f1f7fb;
    color: #274357;
    font-weight: 700;
    border-bottom: 1px solid #d5e4ef;
  }

  :deep(td) {
    border-bottom: 1px solid #e4eef5;
  }

  :deep(tr:last-child td) {
    border-bottom: none;
  }

  :deep(.align-left) {
    text-align: left;
  }

  :deep(.align-center) {
    text-align: center;
  }

  :deep(.align-right) {
    text-align: right;
  }
}

@media (max-width: 768px) {
  .bubble-wrapper {
    max-width: calc(100% - 34px);
  }
}

@keyframes message-in {
  0% {
    opacity: 0;
    transform: translateY(4px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
