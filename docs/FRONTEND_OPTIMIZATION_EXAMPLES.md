# 📘 前端优化应用示例

## 快速开始

本文档提供实际代码示例，展示如何在项目中应用前端优化技术。

---

## 🎯 示例 1：为项目列表添加骨架屏

### 第1步：修改 `templates/layout.html`

在 `<head>` 部分添加样式：

```html
<!-- 骨架屏样式 -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/loading-skeleton.css') }}">
```

在 `</body>` 前添加脚本：

```html
<!-- 懒加载工具 -->
<script src="{{ url_for('static', filename='js/lazy-load.js') }}"></script>
```

### 第2步：修改 `templates/project_list.html`

在表格上方添加骨架屏：

```html
{% block content %}
<div class="card shadow-sm border-0">
    <div class="card-header">
        <!-- ... 现有header代码 ... -->
    </div>
    
    <div class="card-body">
        <!-- 骨架屏（初始显示） -->
        <div id="loading-skeleton" class="table-skeleton">
            <table class="table">
                <tbody>
                    {% for _ in range(10) %}
                    <tr>
                        <td><div class="skeleton"></div></td>
                        <td><div class="skeleton"></div></td>
                        <td><div class="skeleton"></div></td>
                        <td><div class="skeleton"></div></td>
                        <td><div class="skeleton"></div></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <!-- 实际内容（初始隐藏） -->
        <div id="actual-content" style="{% if projects %}display: block;{% else %}display: none;{% endif %}">
            <form id="control-form" method="POST" action="{{ url_for('projects.batch_action') }}">
                <!-- ... 现有表格代码 ... -->
            </form>
        </div>
    </div>
</div>

{% block scripts %}
{{ super() }}
<script>
// 页面加载完成后隐藏骨架屏
document.addEventListener('DOMContentLoaded', function() {
    {% if projects %}
    document.getElementById('loading-skeleton').style.display = 'none';
    document.getElementById('actual-content').style.display = 'block';
    {% endif %}
});
</script>
{% endblock %}
{% endblock %}
```

---

## 🎯 示例 2：添加加载遮罩层

### 创建全局加载遮罩

在 `templates/layout.html` 的 `<body>` 顶部添加：

```html
<body>
    <!-- 全局加载遮罩 -->
    <div class="loading-overlay" id="globalLoading">
        <div class="spinner"></div>
    </div>
    
    <!-- ... 其他内容 ... -->
</body>
```

### 创建全局工具函数

在 `static/js/` 创建 `app.js`：

```javascript
// static/js/app.js

// 显示全局加载
function showLoading() {
    document.getElementById('globalLoading').classList.add('active');
}

// 隐藏全局加载
function hideLoading() {
    document.getElementById('globalLoading').classList.remove('active');
}

// 显示按钮加载状态
function setButtonLoading(button, isLoading) {
    if (isLoading) {
        button.classList.add('btn-loading');
        button.disabled = true;
        button.setAttribute('data-original-text', button.textContent);
    } else {
        button.classList.remove('btn-loading');
        button.disabled = false;
        if (button.hasAttribute('data-original-text')) {
            button.textContent = button.getAttribute('data-original-text');
        }
    }
}

// 全局导出
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.setButtonLoading = setButtonLoading;
```

在 `layout.html` 中引入：

```html
<script src="{{ url_for('static', filename='js/app.js') }}"></script>
```

### 使用示例

```javascript
// 在表单提交时显示加载
document.getElementById('myForm').addEventListener('submit', function(e) {
    showLoading();
    
    // 如果是AJAX提交
    e.preventDefault();
    fetch('/api/submit', {
        method: 'POST',
        body: new FormData(this)
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        alert('提交成功！');
    })
    .catch(error => {
        hideLoading();
        alert('提交失败！');
    });
});
```

---

## 🎯 示例 3：图片懒加载

### 场景：如果你的项目有产品图片

```html
<!-- 原来的写法 -->
<img src="/static/images/product1.jpg" alt="产品1">

<!-- 懒加载写法 -->
<img data-src="/static/images/product1.jpg" 
     src="/static/images/placeholder.png" 
     alt="产品1" 
     class="lazy-image">
```

懒加载会自动处理，无需额外JavaScript代码。

### 高级：带占位符的懒加载

```html
<div class="image-wrapper">
    <img data-src="/static/images/large-image.jpg"
         src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300'%3E%3C/svg%3E"
         alt="示例"
         class="lazy-image">
</div>

<style>
.image-wrapper {
    position: relative;
    background: #f0f0f0;
    aspect-ratio: 4 / 3;
}

.image-wrapper img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}
</style>
```

---

## 🎯 示例 4：AJAX分页（无刷新）

### 为项目列表添加无刷新分页

在 `templates/project_list.html` 的 `{% block scripts %}` 中添加：

```javascript
<script>
// AJAX分页功能
class AjaxPagination {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.bindEvents();
    }
    
    bindEvents() {
        // 监听分页按钮点击
        document.querySelectorAll('.pagination a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const url = link.getAttribute('href');
                if (url && url !== '#') {
                    this.loadPage(url);
                }
            });
        });
    }
    
    async loadPage(url) {
        try {
            // 显示加载状态
            this.container.classList.add('table-loading');
            
            // 请求新页面
            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (!response.ok) {
                throw new Error('加载失败');
            }
            
            const html = await response.text();
            
            // 解析HTML
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            
            // 提取表格内容
            const newTable = doc.querySelector('.table-responsive');
            const newPagination = doc.querySelector('.pagination');
            
            // 更新内容
            if (newTable) {
                this.container.querySelector('.table-responsive').innerHTML = newTable.innerHTML;
            }
            
            if (newPagination) {
                document.querySelector('.pagination').outerHTML = newPagination.outerHTML;
                this.bindEvents(); // 重新绑定事件
            }
            
            // 滚动到顶部
            this.container.scrollIntoView({ behavior: 'smooth' });
            
            // 移除加载状态
            this.container.classList.remove('table-loading');
            
        } catch (error) {
            console.error('加载失败:', error);
            this.container.classList.remove('table-loading');
            alert('加载失败，请刷新页面重试');
        }
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    new AjaxPagination('actual-content');
});
</script>
```

---

## 🎯 示例 5：虚拟滚动（仅在需要时使用）

### 场景：需要在一页显示所有配方成分（假设有很多）

在 `templates/formula_edit.html` 中：

```html
{% block content %}
<!-- 虚拟滚动容器 -->
<div id="composition-virtual-list" style="height: 600px; border: 1px solid #ddd;"></div>

{% block scripts %}
{{ super() }}
<script src="{{ url_for('static', filename='js/virtual-scroll.js') }}"></script>
<script>
// 配方成分数据（从后端获取）
const compositions = {{ composition_json|safe }};

// 创建虚拟滚动
const virtualList = new VirtualScroll(
    document.getElementById('composition-virtual-list'),
    {
        data: compositions,
        itemHeight: 60, // 每行60px
        bufferSize: 3,
        renderItem: (item, index) => {
            const div = document.createElement('div');
            div.className = 'composition-item d-flex align-items-center p-3 border-bottom';
            div.innerHTML = `
                <div class="flex-grow-1">
                    <strong>${item.MaterialName || item.FillerName}</strong>
                    <span class="text-muted ms-2">${item.WeightPercentage}%</span>
                </div>
                <div>
                    <button class="btn btn-sm btn-outline-danger" 
                            onclick="removeComposition(${item.CompositionID})">
                        删除
                    </button>
                </div>
            `;
            return div;
        }
    }
);
</script>
{% endblock %}
{% endblock %}
```

**注意**：通常不需要虚拟滚动，因为分页已经解决了问题。

---

## 🎯 示例 6：批量渲染优化

### 场景：需要前端生成大量DOM元素

```javascript
// 假设有1000条数据需要渲染
const data = {{ large_dataset|safe }};
const tbody = document.querySelector('tbody');

// ❌ 不好的做法（一次性渲染，可能卡顿）
data.forEach(item => {
    const row = createRow(item);
    tbody.appendChild(row);
});

// ✅ 好的做法（批量渲染）
window.lazyLoader.batchRender(
    data,
    (item, index) => {
        const row = createRow(item);
        tbody.appendChild(row);
    },
    20 // 每批20条，不会阻塞UI
);

function createRow(item) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td>${item.id}</td>
        <td>${item.name}</td>
        <td>${item.date}</td>
    `;
    return tr;
}
```

---

## 🎯 示例 7：防抖和节流

### 搜索框防抖

```javascript
// 实时搜索，避免频繁请求
const searchInput = document.getElementById('search');
const debouncedSearch = window.lazyLoader.debounce(function(e) {
    const query = e.target.value;
    // 执行搜索
    searchProjects(query);
}, 500); // 500ms后执行

searchInput.addEventListener('input', debouncedSearch);
```

### 滚动加载节流

```javascript
// 无限滚动加载
const throttledLoadMore = window.lazyLoader.throttle(function() {
    if (isNearBottom()) {
        loadMoreItems();
    }
}, 200); // 200ms内最多执行一次

window.addEventListener('scroll', throttledLoadMore);

function isNearBottom() {
    return window.innerHeight + window.scrollY >= document.body.offsetHeight - 100;
}
```

---

## 📋 快速检查清单

### 基础优化（推荐全部实施）
- [x] ✅ 分页功能（已完成）
- [ ] 🔄 添加骨架屏到主要列表页
- [ ] 🔄 添加全局加载遮罩
- [ ] 🔄 优化按钮提交状态

### 可选优化（按需实施）
- [ ] 📸 图片懒加载（如果有图片）
- [ ] 🔄 AJAX无刷新分页
- [ ] 🔍 搜索框防抖
- [ ] ♾️ 无限滚动（如果需要）

### 高级优化（通常不需要）
- [ ] 📜 虚拟滚动（仅超大列表）
- [ ] 💾 本地缓存（IndexedDB）
- [ ] 👷 Web Worker后台处理

---

## 🎨 样式参考

### 加载按钮示例

```html
<button class="btn btn-primary" id="submitBtn" onclick="handleSubmit()">
    提交
</button>

<script>
function handleSubmit() {
    const btn = document.getElementById('submitBtn');
    
    // 开始加载
    setButtonLoading(btn, true);
    
    // 模拟异步操作
    setTimeout(() => {
        // 结束加载
        setButtonLoading(btn, false);
        alert('操作完成！');
    }, 2000);
}
</script>
```

### 内联加载提示

```html
<div class="inline-loading">
    正在加载数据...
</div>
```

### 进度条

```html
<div class="progress-bar">
    <div class="progress-bar-indeterminate"></div>
</div>
```

---

## 🚀 总结

### 当前状态
- ✅ **分页功能完善** - 性能已优化
- ✅ **工具库完整** - 随时可用
- ✅ **文档详细** - 易于实施

### 建议行动
1. **可选**：添加骨架屏（提升体验）
2. **可选**：添加加载遮罩（用户反馈）
3. **不需要**：虚拟滚动（分页已足够）

### 性能目标
- ✅ 页面加载 < 0.5秒
- ✅ 用户交互流畅
- ✅ 内存占用合理

**现在的分页方案已经很好，其他优化可根据实际需求选择性添加！** 🎉

