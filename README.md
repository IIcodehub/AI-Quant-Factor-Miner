# AI-Quant-Factor-Miner
# AI-Quant-Factor-Miner: 基于大模型的自动化因子挖掘框架

   

## 📖 项目简介

**AI-Quant-Factor-Miner** 是一个模块化、高度可配置的量化金融研究框架。它利用先进的大语言模型（LLM），如 **DeepSeek (R1)** 和 **Google Gemini (Pro/Flash)**，实现了从“因子创意构思”到“生产级代码生成”再到“因子数据计算”的全自动化流水线。

本框架旨在解决量化研究中的痛点：

1.  **创意枯竭**：通过 AI 的头脑风暴，基于一个种子思路裂变出多个差异化变体。
2.  **代码低效**：通过精心设计的 Prompt Engineering，强制 AI 生成内存优化、无前瞻偏差的高性能 Pandas 代码。
3.  **管理混乱**：实现代码与数据的自动分离存储，支持多模型对比测试。

-----

## 🚀 核心特性

  * **多模型支持 (Multi-LLM Strategy)**:
      * 支持无缝切换 **DeepSeek** (擅长深度推理/数学逻辑) 和 **Gemini** (擅长长窗口/快速生成)。
      * 采用策略模式设计，扩展新模型仅需增加一个子类。
  * **工程化代码生成**:
      * 强制执行 **大驼峰命名法 (CamelCase)**。
      * 内置内存优化规范：禁止大表 Merge，禁止 `rolling.corr` (强制使用 `cov/std` 分解公式)。
      * 自动处理 `np.inf` 异常值和 SecuCode 格式化。
  * **沙箱执行环境**:
      * 动态加载生成的 Python 代码，无需重启主程序。
      * 严格的数据校验机制，确保输出 DataFrame 格式统一。
  * **结构化输出**:
      * 根据使用的模型自动分流输出路径 (e.g., `output/deepseek/factors` vs `output/gemini/factors`)。
      * 代码文件 (`.py`) 与 数据文件 (`.parquet`) 物理分离。

-----

## 📂 项目目录结构

```text
QuantFactorAI/
├── config/                  # [配置中心]
│   ├── __init__.py
│   └── settings.py          # 全局配置：Key, 路径, 任务清单 (Single Source of Truth)
│
├── core/                    # [核心逻辑]
│   ├── __init__.py
│   ├── prompts.py           # 精心调优的 System Prompts (含数据字典注入)
│   ├── llm_base.py          # LLM 抽象基类
│   ├── llm_deepseek.py      # DeepSeek 接口实现
│   └── llm_gemini.py        # Gemini 接口实现
│
├── data_loader/             # [数据层]
│   ├── __init__.py
│   └── loader.py            # 高效读取 Parquet 数据，构建 Data Bundle
│
├── engine/                  # [执行引擎]
│   ├── __init__.py
│   ├── code_manager.py      # 代码清洗、持久化与动态模块加载
│   └── executor.py          # 因子函数执行、结果校验、格式修正 (SecuCode截断)
│
├── utils/                   # [工具箱]
│   ├── __init__.py
│   └── logger.py            # 统一日志管理
│
├── main.py                  # [入口] 任务调度主程序
├── requirements.txt         # 项目依赖
└── README.md                # 项目文档
```

-----

## 🛠️ 快速开始

### 1\. 环境准备

确保安装 Python 3.9 或更高版本。

```bash
# 建议创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

`requirements.txt` 参考内容：

```text
pandas
numpy
openai
google-generativeai
pyarrow
fastparquet
```

### 2\. 数据准备

本项目需要两份基础数据（Parquet 格式）：

1.  **股票日行情 (df\_raw)**: 长格式 Panel Data。
2.  **指数日行情 (df\_index)**: 时间序列 Data。

请在 `config/settings.py` 中配置您的本地路径。

### 3\. 配置 API Key 与任务

打开 `config/settings.py`，完成以下三步：

1.  **设置 API Key** (推荐使用环境变量，也可直接填入)：
    ```python
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "your-sk-key")
    ```
2.  **选择模型**:
    ```python
    ACTIVE_PROVIDER = 'deepseek'  # 或 'gemini'
    ```
3.  **定义挖掘任务**:
    ```python
    FACTOR_MINING_TASKS = [
        {
            "idea": "量价背离：股价创新高但换手率下降",
            "num_variations": 3
        }
    ]
    ```

### 4\. 运行程序

```bash
python main.py
```

-----

## ⚙️ 详细配置指南 (`settings.py`)

`config/settings.py` 是本框架的**唯一事实来源 (Single Source of Truth)**。

### 1\. 路径管理

框架会自动根据 `ACTIVE_PROVIDER` 生成输出目录，无需手动创建文件夹：

  * 如果使用 DeepSeek: `BASE_OUTPUT_DIR/deepseek/codes/`
  * 如果使用 Gemini: `BASE_OUTPUT_DIR/gemini/codes/`

### 2\. 数据字典定义

为了防止 AI 幻觉（编造不存在的列），我们在 Settings 中硬编码了数据列描述，并通过 Prompt 动态注入给 AI：

```python
STOCK_COLUMNS_DESC = """
'TradingDay', 'SecuCode', 'OpenPrice', 'ClosePrice', 'TurnOverRate', ...
"""
```

**注意**: 如果您的底层 Parquet 数据增加了新字段（如 `VWAP`），请务必同步更新这里的描述。

### 3\. 任务清单 (Task List)

您可以在 `FACTOR_MINING_TASKS` 列表中批量定义任务。

  * `idea`: 基础因子的自然语言描述。
  * `num_variations`: 希望 AI 基于该思路生成多少个变体（默认为 3）。

-----

## 🧠 设计架构详解

### 阶段一：构思 (Ideation)

  * **输入**: 自然语言描述的种子思路 (e.g., "动量反转")。
  * **处理**: LLM (DeepSeek-Reasoner / Gemini-Flash) 进行金融逻辑推理。
  * **Prompt 约束**:
      * 强制 **JSON** 格式输出。
      * 强制 **大驼峰命名 (CamelCase)**。
      * 要求数学逻辑差异化，而非简单的参数修改。

### 阶段二：代码生成 (Code Generation)

  * **输入**: 因子名称与具体计算逻辑。
  * **处理**: LLM (DeepSeek-Chat / Gemini-Flash) 编写 Python 函数。
  * **性能约束**:
      * **内存安全**: 严禁 `pd.merge` 大表，必须先在小表计算后合并。
      * **计算优化**: 严禁 `rolling.corr`，强制分解为 `cov / (std*std)`。
      * **数据对齐**: 强制 `groupby` 后操作，强制 `reset_index`。

### 阶段三：执行与清洗 (Execution)

  * **动态加载**: 使用 `importlib` 将生成的字符串代码加载为内存函数。
  * **后处理**:
      * `SecuCode` 强制截断为 6 位字符串（修复 `.SZ/.SH` 后缀或 Int 类型问题）。
      * 校验 DataFrame 是否包含 `SecuCode`, `TradingDay` 和 `FactorValue`。

-----

## 📊 输出示例

运行完成后，`output/deepseek/` 目录下将生成：

**1. 代码文件 (`codes/`)**

```python
# codes/VolAdjustedReversal.py
import pandas as pd
import numpy as np

def VolAdjustedReversal(df_raw, df_index):
    # 数学公式: Reversal = -1 * (Ret_20 / Std_20)
    # 逻辑: 经波动率调整后的20日反转因子
    
    # ... (AI 生成的优化代码) ...
    return df_final[['SecuCode', 'TradingDay', 'VolAdjustedReversal']]
```

**2. 因子数据 (`factors/`)**
`VolAdjustedReversal.parquet` (标准 DataFrame 格式，可直接入库回测)。

-----

## ❓ 常见问题 (Troubleshooting)

**Q: 报错 `ImportError: attempted relative import...`**
A: 请务必在项目根目录下运行 `python main.py`，不要直接运行子文件夹里的脚本。

**Q: AI 生成的代码报错 `KeyError`**
A: 检查 `settings.py` 中的 `STOCK_COLUMNS_DESC` 是否与您本地 Parquet 文件的实际列名完全一致。

**Q: 提示 `Authentication Fails`**
A: 请在 `config/settings.py` 中填入正确的 API Key。

-----

## 📝 TODO / 未来计划

  * [ ] **多因子合成**: 增加层级，将生成的多个因子进行 IC 加权合成。
  * [ ] **自动回测**: 集成简单的 Alphalens 或 Backtrader 进行初步绩效评估。
  * [ ] **因子库管理**: 使用 SQLite/MySQL 记录因子元数据和表现。

-----

**Disclaimer**: Quantitative investment involves risks. This framework is for research purposes only.
