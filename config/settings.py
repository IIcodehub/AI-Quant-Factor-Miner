# config/settings.py
import os

# ===========================
# 1. 核心模型配置
# ===========================
# 切换当前使用的提供商: 'deepseek' 或 'gemini'
ACTIVE_PROVIDER = 'deepseek'

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-f1c9c286840c42729f3cca5a4952bbd4")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBdG1ZjV_03j190NO3kNJcyQeo80EH99YM")

MODEL_CONFIG = {
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "ideation_model": "deepseek-reasoner",
        "coding_model": "deepseek-chat",
        "temperature_ideation": 0.7,
        "temperature_coding": 0.0,
    },
    "gemini": {
        "ideation_model": "gemini-3-pro-preview",
        "coding_model": "gemini-2.5-flash",
        "temperature_ideation": 0.7,
        "temperature_coding": 0.0,
    }
}

# ===========================
# 2. 数据与字段定义
# ===========================
# 基础根目录
BASE_OUTPUT_DIR = r"D:\框架\QuantFactorAI\output"
DATA_PATH_STOCK = r"D:\框架\QuantFactorAI\data\data.parquet"
DATA_PATH_INDEX = r"D:\框架\QuantFactorAI\data\index.parquet"

STOCK_COLUMNS_DESC = """
'TradingDay', 'SecuCode', 'PrevClosePrice', 'OpenPrice', 'HighPrice', 'LowPrice',
'ClosePrice', 'TurnOverVolume', 'TurnOverValue', 'TurnOverRate', 'FloatMarketValue'
"""

INDEX_COLUMNS_DESC = """
'TradingDay', 'HS300', 'ZZ500', 'ZZ1000', 'SZ'
"""

REQUIRED_OUTPUT_COLS = ['SecuCode', 'TradingDay']
DEFAULT_NUM_VARIATIONS = 3

# ===========================
# 3. 因子挖掘任务清单
# ===========================
FACTOR_MINING_TASKS = [
    # {
    #     "idea": "过去20个交易日，t日换手率与t日价格的相关系数",
    #     "num_variations": 3
    # },
    {
       "idea": "量价背离因子：价格创新高但成交量未创新高",
       "num_variations": 3
    }
]