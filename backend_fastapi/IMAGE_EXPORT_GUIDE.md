# 图片导出功能使用指南

## 功能概述

新增的图片导出功能可以将项目信息、配方成分和测试结果导出为一张完整的PNG图片报告，包含：

1. **项目信息表** - 展示项目基本信息（项目ID、名称、类型、配方编号、设计师等）
2. **配方成分柱状图** - 可视化展示各成分的重量百分比
3. **测试结果雷达图** - 基于行业标准的测试指标雷达图

## 安装依赖

### 1. 安装Python依赖包

```bash
cd backend_fastapi
pip install matplotlib==3.9.0 Pillow==10.4.0 numpy==1.26.4
```

或者直接安装所有依赖：

```bash
pip install -r requirements.txt
```

### 2. Windows系统中文字体支持

图表需要中文字体支持。如果生成的图片中文显示为方框，请确保系统中有以下字体之一：

- **SimHei**（黑体）- Windows系统自带
- **Microsoft YaHei**（微软雅黑）- Windows系统自带
- **Arial Unicode MS** - 部分Windows版本自带

通常Windows系统已经包含这些字体，无需额外配置。

## API接口

### 导出项目图片报告

**请求方式**: `GET`

**接口地址**: `/api/v1/projects/export-image/{project_id}`

**路径参数**:
- `project_id` (integer, required) - 项目ID

**响应**:
- Content-Type: `image/png`
- 返回PNG图片文件

**示例**:
```bash
curl -X GET "http://localhost:8000/api/v1/projects/export-image/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output project_report.png
```

## 前端使用

在项目详情页面，点击 **"导出图片报告"** 按钮即可下载包含项目完整信息的PNG图片。

## 行业标准配置

雷达图基于以下行业标准进行数据标准化（0-100范围）：

### 喷墨项目
- 粘度 (0-100 cP)
- 反应活性 (0-100 s)
- 粒径 (0-500 nm)
- 表面张力 (0-50 mN/m)
- 色度 (0-100 Lab*)

### 涂层项目
- 附着力 (0-100)
- 透明度 (0-100%)
- 表面硬度 (0-10 H)
- 耐化学性 (0-100)
- 成本估算 (0-100 €/kg)

### 3D打印项目
- 收缩率 (0-10%)
- 杨氏模量 (0-5000 MPa)
- 弯曲强度 (0-200 MPa)
- 邵氏硬度 (0-100 Shore)
- 抗冲击性 (0-100 kJ/m²)

### 复合材料项目
- 弯曲强度 (0-200 MPa)
- 杨氏模量 (0-5000 MPa)
- 抗冲击性 (0-100 kJ/m²)
- 转化率 (0-100%)
- 吸水率 (0-10%)

## 技术实现

### 后端架构
- **Chart Generator** (`app/utils/chart_generator.py`): 核心图表生成服务
  - `create_project_info_table()`: 生成项目信息表
  - `create_composition_bar_chart()`: 生成配方成分柱状图
  - `create_test_result_radar_chart()`: 生成测试结果雷达图
  - `combine_images_vertical()`: 垂直组合三张图片

### 前端集成
- **API调用** (`frontend_vue3/src/api/projects.ts`): `exportProjectImageApi(projectId)`
- **UI按钮** (`frontend_vue3/src/views/projects/Detail.vue`): 项目详情页导出按钮

## 故障排除

### 1. 中文显示为方框
**问题**: 生成的图片中中文字符显示为方框

**解决方案**:
- 检查系统是否安装了中文字体（SimHei、Microsoft YaHei等）
- Windows系统通常已包含，无需额外安装

### 2. Matplotlib后端错误
**问题**: `RuntimeError: Cannot generate image`

**解决方案**:
```python
# chart_generator.py 已配置非交互式后端
matplotlib.use('Agg')
```
无需额外配置。

### 3. 测试结果数据无法显示
**问题**: 雷达图显示"暂无测试结果数据"

**原因**: 
- 项目还没有测试结果数据
- 测试结果字段格式不正确（需要包含数字）

**解决方案**:
- 在项目详情页面点击"编辑测试结果"添加测试数据
- 确保测试结果字段包含有效的数值

### 4. 配方成分不显示
**问题**: 柱状图显示"暂无配方成分数据"

**原因**: 项目还没有添加配方成分

**解决方案**:
- 在项目详情页面点击"添加成分"添加配方成分数据

## 性能优化

- 图片生成在服务器端完成，通常耗时 1-3 秒
- 建议项目配方成分不超过 20 个，以确保图表清晰可读
- 图片分辨率设置为 150 DPI，平衡质量和文件大小

## 未来改进

可考虑添加的功能：
- [ ] 支持批量导出多个项目
- [ ] 自定义图表样式和颜色
- [ ] 支持PDF格式导出
- [ ] 添加公司Logo和水印
- [ ] 导出设置（选择要包含的部分）

