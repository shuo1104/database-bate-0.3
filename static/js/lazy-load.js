/**
 * 懒加载工具类
 * 用于优化页面加载性能
 */

class LazyLoader {
    constructor() {
        this.observers = new Map();
        this.initIntersectionObserver();
    }

    /**
     * 初始化 Intersection Observer
     */
    initIntersectionObserver() {
        // 检查浏览器支持
        if (!('IntersectionObserver' in window)) {
            console.warn('浏览器不支持 IntersectionObserver，懒加载功能降级');
            this.fallbackMode = true;
            return;
        }

        // 创建图片懒加载观察器
        this.imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadImage(entry.target);
                    this.imageObserver.unobserve(entry.target);
                }
            });
        }, {
            rootMargin: '50px 0px', // 提前50px开始加载
            threshold: 0.01
        });

        // 创建内容懒加载观察器
        this.contentObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadContent(entry.target);
                    this.contentObserver.unobserve(entry.target);
                }
            });
        }, {
            rootMargin: '100px 0px',
            threshold: 0.01
        });
    }

    /**
     * 懒加载图片
     * 用法: <img data-src="image.jpg" class="lazy-image" alt="">
     */
    lazyLoadImages(container = document) {
        if (this.fallbackMode) {
            // 降级模式：直接加载所有图片
            const images = container.querySelectorAll('img[data-src]');
            images.forEach(img => this.loadImage(img));
            return;
        }

        const images = container.querySelectorAll('img[data-src]:not(.loaded)');
        images.forEach(img => {
            this.imageObserver.observe(img);
        });
    }

    /**
     * 加载单张图片
     */
    loadImage(img) {
        const src = img.getAttribute('data-src');
        if (!src) return;

        // 添加加载状态
        img.classList.add('loading');

        // 创建新图片对象预加载
        const tempImg = new Image();
        tempImg.onload = () => {
            img.src = src;
            img.classList.remove('loading');
            img.classList.add('loaded');
            img.removeAttribute('data-src');
        };
        tempImg.onerror = () => {
            img.classList.remove('loading');
            img.classList.add('error');
            console.error(`图片加载失败: ${src}`);
        };
        tempImg.src = src;
    }

    /**
     * 懒加载表格行
     * 用法: <tr data-lazy-load="true">...</tr>
     */
    lazyLoadTableRows(tableBody) {
        if (this.fallbackMode) {
            // 降级模式：直接显示所有行
            const rows = tableBody.querySelectorAll('tr[data-lazy-load]');
            rows.forEach(row => {
                row.removeAttribute('data-lazy-load');
                row.style.visibility = 'visible';
            });
            return;
        }

        const rows = tableBody.querySelectorAll('tr[data-lazy-load]:not(.loaded)');
        rows.forEach(row => {
            this.contentObserver.observe(row);
        });
    }

    /**
     * 加载内容
     */
    loadContent(element) {
        element.classList.add('loaded');
        element.style.visibility = 'visible';
        element.removeAttribute('data-lazy-load');

        // 触发自定义事件
        element.dispatchEvent(new CustomEvent('lazyloaded'));
    }

    /**
     * 批量渲染优化
     * 将大量DOM操作分批执行，避免阻塞主线程
     */
    batchRender(items, renderCallback, batchSize = 20) {
        let index = 0;

        const renderBatch = () => {
            const end = Math.min(index + batchSize, items.length);
            
            for (let i = index; i < end; i++) {
                renderCallback(items[i], i);
            }

            index = end;

            if (index < items.length) {
                // 使用 requestAnimationFrame 确保不阻塞渲染
                requestAnimationFrame(renderBatch);
            }
        };

        renderBatch();
    }

    /**
     * 防抖函数
     */
    debounce(func, wait = 300) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * 节流函数
     */
    throttle(func, limit = 200) {
        let inThrottle;
        return function executedFunction(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    /**
     * 清理所有观察器
     */
    destroy() {
        if (this.imageObserver) {
            this.imageObserver.disconnect();
        }
        if (this.contentObserver) {
            this.contentObserver.disconnect();
        }
        this.observers.clear();
    }
}

// 创建全局实例
window.lazyLoader = new LazyLoader();

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    // 懒加载所有图片
    window.lazyLoader.lazyLoadImages();
    
    // 懒加载表格（如果有）
    const tableBodies = document.querySelectorAll('tbody');
    tableBodies.forEach(tbody => {
        window.lazyLoader.lazyLoadTableRows(tbody);
    });
});

