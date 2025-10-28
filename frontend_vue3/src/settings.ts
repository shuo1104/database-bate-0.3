/**
 * 项目全局配置
 */
export default {
  /**
   * 项目标题
   */
  title: import.meta.env.VITE_APP_TITLE || 'Advanced - PhotoPolymer Formulation Management DB',

  /**
   * 是否显示设置
   */
  showSettings: true,

  /**
   * 是否显示标签视图
   */
  tagsView: true,

  /**
   * 是否固定头部
   */
  fixedHeader: true,

  /**
   * 是否显示侧边栏Logo
   */
  sidebarLogo: true,

  /**
   * Token在Cookie中存储的天数，默认1天
   */
  tokenCookieExpires: 1,

  /**
   * Token在LocalStorage中存储的天数，默认7天
   */
  tokenLocalExpires: 7,
}

