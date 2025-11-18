# 前端 LOGO 替换说明文档

**修改日期**: 2025-11-18
**LOGO 文件**: `data_base/img/材料数据库LOGO.png`

---

## 📋 修改内容总结

已将前端所有 LOGO 位置替换为实际的 LOGO 图片（`材料数据库LOGO.png`），所有主题统一使用同一个 LOGO。

### 修改的文件列表

1. ✅ **登录页面** - `src/views/auth/Login.vue`
2. ✅ **侧边栏** - `src/layouts/components/Sidebar.vue`
3. ✅ **网页图标 (Favicon)** - `index.html`
4. ✅ **资源文件** - 复制 LOGO 到多个位置

---

## 🔧 详细修改内容

### 1. 复制 LOGO 图片到前端资源目录

**操作**:
```bash
# 复制到 public 目录（用于 favicon）
cp data_base/img/材料数据库LOGO.png data_base/frontend_vue3/public/logo.png

# 复制到 assets/images 目录（用于组件引用）
cp data_base/img/材料数据库LOGO.png data_base/frontend_vue3/src/assets/images/logo.png
```

**结果**:
- ✅ `public/logo.png` - 用于 favicon
- ✅ `src/assets/images/logo.png` - 用于组件引用

---

### 2. 修改登录页面 LOGO

**文件**: `src/views/auth/Login.vue`

**修改前**:
```vue
<div class="logo-wrapper">
  <div class="logo-icon">
    <el-icon :size="48"><Grid /></el-icon>
  </div>
</div>
```

**修改后**:
```vue
<div class="logo-wrapper">
  <img src="@/assets/images/logo.png" alt="Logo" class="logo-image" />
</div>
```

**样式修改**:
```scss
// 修改前
.logo-icon {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
  color: #fff;
  transition: all 0.3s ease;
}

// 修改后
.logo-image {
  width: 180px;
  height: 180px;
  object-fit: contain;
  transition: all 0.3s ease;
  filter: drop-shadow(0 10px 30px rgba(102, 126, 234, 0.3));

  &:hover {
    transform: translateY(-5px) scale(1.05);
    filter: drop-shadow(0 15px 40px rgba(102, 126, 234, 0.4));
  }
}
```

**效果**:
- ✅ 登录页面显示实际 LOGO 图片
- ✅ 尺寸调整为 180x180px（放大1.5倍）
- ✅ 保留悬停动画效果

---

### 3. 修改侧边栏 LOGO

**文件**: `src/layouts/components/Sidebar.vue`

**修改前**:
```vue
<div class="sidebar-logo">
  <div class="logo-icon">
    <el-icon :size="28"><Grid /></el-icon>
  </div>
  <div class="logo-text">
    <div class="logo-title">Advanced</div>
    <div class="logo-subtitle">PhotoPolymer DB</div>
  </div>
</div>
```

**修改后**:
```vue
<div class="sidebar-logo">
  <img src="@/assets/images/logo.png" alt="Logo" class="logo-image" />
  <div class="logo-text">
    <div class="logo-title">Advanced</div>
    <div class="logo-subtitle">PhotoPolymer DB</div>
  </div>
</div>
```

**样式修改**:
```scss
// 修改前
.logo-icon {
  width: 42px;
  height: 42px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

// 修改后
.logo-image {
  width: 75px;
  height: 75px;
  object-fit: contain;
  flex-shrink: 0;
  transition: all 0.3s ease;

  &:hover {
    transform: scale(1.1);
  }
}
```

**效果**:
- ✅ 侧边栏显示实际 LOGO 图片
- ✅ 尺寸调整为 75x75px（放大1.5倍）
- ✅ 保留悬停缩放效果

---

### 4. 修改网页图标 (Favicon)

**文件**: `index.html`

**修改前**:
```html
<link rel="icon" type="image/svg+xml" href="/vite.svg" />
```

**修改后**:
```html
<link rel="icon" type="image/png" href="/logo.png" />
```

**效果**:
- ✅ 浏览器标签页显示实际 LOGO 图标
- ✅ 书签栏显示实际 LOGO 图标

---

## 🎨 LOGO 显示位置总览

| 位置 | 文件 | 尺寸 | 状态 |
|------|------|------|------|
| **登录页面** | `Login.vue` | 180x180px | ✅ 已替换 |
| **侧边栏** | `Sidebar.vue` | 75x75px | ✅ 已替换 |
| **浏览器标签页** | `index.html` | 自适应 | ✅ 已替换 |
| **书签栏** | `index.html` | 自适应 | ✅ 已替换 |

---

## 🚀 如何查看效果

### 开发环境

```bash
cd data_base/frontend_vue3
pnpm dev
```

访问 `http://localhost:3000`，您将看到：
1. 登录页面中央显示 LOGO
2. 登录后侧边栏左上角显示 LOGO
3. 浏览器标签页显示 LOGO 图标

### 生产环境

```bash
cd data_base/frontend_vue3
pnpm build
```

构建后的文件会包含所有 LOGO 图片。

---

## 📝 注意事项

1. **图片格式**: 当前使用 PNG 格式，支持透明背景
2. **图片路径**: 使用 `@/assets/images/logo.png` 别名路径
3. **响应式**: 使用 `object-fit: contain` 保持图片比例
4. **性能**: 图片会被 Vite 自动优化

---

## 🔄 如何更换 LOGO

如果将来需要更换 LOGO，只需：

1. 替换源文件：
   ```bash
   cp 新LOGO.png data_base/img/材料数据库LOGO.png
   ```

2. 重新复制到前端目录：
   ```bash
   cp data_base/img/材料数据库LOGO.png data_base/frontend_vue3/public/logo.png
   cp data_base/img/材料数据库LOGO.png data_base/frontend_vue3/src/assets/images/logo.png
   ```

3. 重新构建前端：
   ```bash
   cd data_base/frontend_vue3
   pnpm build
   ```

---

**文档版本**: 1.0.0  
**最后更新**: 2025-11-18


