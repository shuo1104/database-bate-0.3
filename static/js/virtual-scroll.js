/**
 * 虚拟滚动实现
 * 只渲染可见区域的元素，大幅提升长列表性能
 */

class VirtualScroll {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            itemHeight: options.itemHeight || 50,      // 每行高度
            bufferSize: options.bufferSize || 5,       // 缓冲区大小（上下各多渲染几行）
            data: options.data || [],                  // 数据数组
            renderItem: options.renderItem || null,    // 渲染函数
            ...options
        };

        this.viewportHeight = 0;
        this.scrollTop = 0;
        this.visibleStart = 0;
        this.visibleEnd = 0;

        this.init();
    }

    /**
     * 初始化
     */
    init() {
        if (!this.container) {
            console.error('容器元素不存在');
            return;
        }

        // 创建虚拟滚动容器结构
        this.createScrollContainer();
        
        // 绑定滚动事件
        this.bindEvents();
        
        // 初始渲染
        this.update();
    }

    /**
     * 创建滚动容器
     */
    createScrollContainer() {
        // 保存原始内容
        this.originalContent = this.container.innerHTML;
        
        // 清空容器
        this.container.innerHTML = '';
        
        // 设置容器样式
        this.container.style.position = 'relative';
        this.container.style.overflow = 'auto';
        this.container.style.height = this.options.containerHeight || '600px';
        
        // 创建占位元素（用于撑开滚动条）
        this.spacer = document.createElement('div');
        this.spacer.style.position = 'absolute';
        this.spacer.style.top = '0';
        this.spacer.style.left = '0';
        this.spacer.style.width = '1px';
        this.spacer.style.height = `${this.getTotalHeight()}px`;
        this.container.appendChild(this.spacer);
        
        // 创建可见内容容器
        this.content = document.createElement('div');
        this.content.style.position = 'absolute';
        this.content.style.top = '0';
        this.content.style.left = '0';
        this.content.style.width = '100%';
        this.container.appendChild(this.content);
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        // 使用节流优化滚动性能
        this.handleScroll = this.throttle(() => {
            this.scrollTop = this.container.scrollTop;
            this.update();
        }, 16); // 约60fps

        this.container.addEventListener('scroll', this.handleScroll);

        // 监听窗口大小变化
        this.handleResize = this.throttle(() => {
            this.update();
        }, 200);

        window.addEventListener('resize', this.handleResize);
    }

    /**
     * 更新可见区域
     */
    update() {
        this.viewportHeight = this.container.clientHeight;
        
        // 计算可见范围
        const start = Math.floor(this.scrollTop / this.options.itemHeight);
        const end = Math.ceil((this.scrollTop + this.viewportHeight) / this.options.itemHeight);
        
        // 添加缓冲区
        this.visibleStart = Math.max(0, start - this.options.bufferSize);
        this.visibleEnd = Math.min(this.options.data.length, end + this.options.bufferSize);
        
        // 渲染可见项
        this.render();
    }

    /**
     * 渲染可见项
     */
    render() {
        if (!this.options.renderItem) {
            console.error('未提供 renderItem 函数');
            return;
        }

        // 清空当前内容
        this.content.innerHTML = '';
        
        // 设置内容偏移
        const offsetY = this.visibleStart * this.options.itemHeight;
        this.content.style.transform = `translateY(${offsetY}px)`;
        
        // 创建文档片段（优化性能）
        const fragment = document.createDocumentFragment();
        
        // 渲染可见项
        for (let i = this.visibleStart; i < this.visibleEnd; i++) {
            const item = this.options.data[i];
            if (!item) continue;
            
            const element = this.options.renderItem(item, i);
            if (element) {
                // 设置固定高度
                element.style.height = `${this.options.itemHeight}px`;
                fragment.appendChild(element);
            }
        }
        
        this.content.appendChild(fragment);
    }

    /**
     * 获取总高度
     */
    getTotalHeight() {
        return this.options.data.length * this.options.itemHeight;
    }

    /**
     * 更新数据
     */
    updateData(newData) {
        this.options.data = newData;
        
        // 更新占位元素高度
        this.spacer.style.height = `${this.getTotalHeight()}px`;
        
        // 重新渲染
        this.update();
    }

    /**
     * 滚动到指定索引
     */
    scrollToIndex(index) {
        const offset = index * this.options.itemHeight;
        this.container.scrollTop = offset;
    }

    /**
     * 节流函数
     */
    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    /**
     * 销毁
     */
    destroy() {
        this.container.removeEventListener('scroll', this.handleScroll);
        window.removeEventListener('resize', this.handleResize);
        this.container.innerHTML = this.originalContent;
    }
}

// 导出
window.VirtualScroll = VirtualScroll;

