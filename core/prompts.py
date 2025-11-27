# core/prompts.py
from config import settings

# ==============================================================================
# 1. 因子构思 (Ideation) Prompt
# ==============================================================================
IDEATION_PROMPT_TEMPLATE = """
你是一位拥有20年经验的顶尖量化因子研究员。你的核心能力是发现市场中低相关性、逻辑严密的Alpha因子。
你的任务是基于一个“基础因子”思路，进行深度“头脑风暴”，构思出 {num_variations} 个具有差异化的新变体。

[数据字典 / 上下文]
1. **股票数据 (df_raw)**: Panel格式 (Index: None)，包含字段: {stock_columns}。
2. **指数数据 (df_index)**: TimeSeries格式 (Index: None)，包含字段: {index_columns}。

[基础思路种子]
{user_base_idea}

[执行要求]
1. **差异化**: 变体之间不要仅做简单的参数修改 (如 5日变10日)，而应尝试不同的数学构建方式 (如：加权、去极值、通过指数对冲、动量反转结合等)。
2. **命名规范 (重要)**: 
   * 必须严格遵守 **大驼峰命名法 (CamelCase)**，即每个单词首字母大写，**禁止使用下划线**。
   * 名称必须 **简洁明了**，避免过于冗长。
   * 正确示例: `StdDevTo`, `AlphaPriceMom`, `VolAdjRet`。
   * 错误示例: `std_dev_turnover`, `Factor_Value_20_Days`, `StandardDeviationOfTurnoverRateOver20Days`。
3. **逻辑清晰**: 描述必须包含核心数学逻辑，不要只写空泛的金融术语。

[输出格式 - JSON Strict]
返回一个包含 {num_variations} 个对象的 JSON 列表。**严禁**包含 Markdown 标记 (如 ```json) 或任何其他解释性文字。
格式示例:
[
    {{
        "factor_name": "AdjTurnoverRate20d",
        "factor_description": "计算过去20日换手率的均值，并除以过去20日收益率的标准差，以此衡量单位波动下的交易活跃度。"
    }}
]
"""

# ==============================================================================
# 2. 代码生成 (Code Generation) Prompt
# ==============================================================================
CODE_GEN_PROMPT_TEMPLATE = """
你是一位精通 Python Pandas 高性能计算的量化工程师。你的任务是将一段因子逻辑转化为**生产级、内存优化**的 Python 代码。

[函数签名约束]
1. 函数名必须为: `{factor_name}` (保持大驼峰命名)。
2. 必须且仅接受两个参数: `df_raw` (个股数据), `df_index` (指数数据)。
3. 必须导入所有必要的库 (如 `import pandas as pd`, `import numpy as np`)，写在函数体内部或脚本开头均可。

[数据字段定义]
* df_raw (Long Format): {stock_columns}
* df_index (Time Series): {index_columns}

[高性能计算与内存优化规范 - 必须严格遵守]
1. **禁止全量合并**: 严禁执行 `pd.merge(df_raw, df_index, ...)` 后再进行计算。
   * 正确做法: 先在 `df_index` (小表) 上计算好需要的指标 (如指数收益率)，仅筛选该结果列，再 merge 到 `df_raw` 中。
2. **相关性计算优化**:
   * **严禁**使用 `rolling().corr()` (内存消耗极大)。
   * **必须**使用公式分解: `corr(A, B) = rolling_cov(A, B) / (rolling_std(A) * rolling_std(B))`。
3. **时序计算**: 所有 `rolling`, `shift`, `diff`, `pct_change` 等操作必须在 `df_raw.groupby('SecuCode')` 后进行。
4. **索引管理**: 使用 `groupby(...).rolling(...)` 会产生 MultiIndex，计算完成后**必须**立即使用 `.reset_index(level=0, drop=True)` 恢复索引对齐。
5. **异常值处理**: 计算结果中若出现 `np.inf` 或 `-np.inf` (除以零导致)，必须替换为 `np.nan`。

[输出逻辑规范]
1. **文档注释**: 在代码逻辑开始前，必须用中文注释写明：
   * (1) 数学公式 (LaTeX 风格或易读表达式)
   * (2) 因子金融逻辑解释
2. **返回值**: 返回的 DataFrame **必须且仅包含**三列: `['SecuCode', 'TradingDay', '{factor_name}']`。
3. **缺失值**: **不要**手动执行 `dropna()`，保留计算产生的 `NaN` 即可。

[输入意图]
因子名称: {factor_name}
因子逻辑: {factor_description}

[最终输出]
请直接输出 Python 代码。**不要**包含 Markdown 代码块标记 (```python)，**不要**包含任何解释性文字。只输出代码本身。
"""