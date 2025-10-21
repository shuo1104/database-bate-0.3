"""
常量定义模块
集中管理应用中的常量，避免魔法数字和字符串
"""

# 配方重量限制
MAX_FORMULA_WEIGHT_PERCENTAGE = 100.5  # 允许微小的精度误差

# 用户角色
ROLE_ADMIN = 'admin'
ROLE_USER = 'user'

# 项目类型映射到测试结果表
TEST_RESULT_TABLE_MAPPING = {
    '喷墨': 'tbl_TestResults_Ink',
    '涂层': 'tbl_TestResults_Coating',
    '3D打印': 'tbl_TestResults_3DPrint',
    '复合材料': 'tbl_TestResults_Composite'
}

# 组件类型
COMPONENT_TYPE_MATERIAL = 'material'
COMPONENT_TYPE_FILLER = 'filler'

# 密码验证
MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 128

# 用户名验证
MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 50

# 数据库字段长度限制
MAX_TRADE_NAME_LENGTH = 255
MAX_SUPPLIER_LENGTH = 255
MAX_PROJECT_NAME_LENGTH = 255

# 会话有效期（秒）
DEFAULT_SESSION_LIFETIME = 28800  # 8小时

