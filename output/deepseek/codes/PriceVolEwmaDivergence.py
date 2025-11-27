import pandas as pd
import numpy as np

def PriceVolEwmaDivergence(df_raw, df_index):
    """
    (1) 数学公式:
    对于每只股票，计算过去20个交易日：
    - 价格创新高信号: I(ClosePrice_t == max(ClosePrice_{t-19:t}))
    - 成交量未创新高信号: I(TurnOverVolume_t < max(TurnOverVolume_{t-19:t}))
    - 每日发散信号 = 价格创新高信号 × 成交量未创新高信号
    - 因子值 = EWMA(每日发散信号, 半衰期=5日) 的20日总和
    
    (2) 金融逻辑解释:
    该因子捕捉价格与成交量的背离现象。当价格创出新高但成交量未能同步创新高时，
    可能意味着上涨动力不足，存在反转风险。使用指数加权移动平均平滑可以更敏感地
    反映近期的背离信号，半衰期5日意味着近期数据的权重更大。
    """
    
    # 复制数据避免修改原数据
    df = df_raw.copy()
    
    # 按股票分组计算滚动窗口内的最大值
    df = df.sort_values(['SecuCode', 'TradingDay'])
    
    # 计算过去20日最高价和最高成交量
    df['price_20d_high'] = df.groupby('SecuCode')['ClosePrice'].transform(
        lambda x: x.rolling(window=20, min_periods=1).max()
    )
    df['volume_20d_high'] = df.groupby('SecuCode')['TurnOverVolume'].transform(
        lambda x: x.rolling(window=20, min_periods=1).max()
    )
    
    # 生成发散信号：价格创新高但成交量未创新高
    df['price_new_high'] = (df['ClosePrice'] == df['price_20d_high']).astype(int)
    df['volume_not_new_high'] = (df['TurnOverVolume'] < df['volume_20d_high']).astype(int)
    df['divergence_signal'] = df['price_new_high'] * df['volume_not_new_high']
    
    # 使用半衰期5日的指数加权移动平均平滑发散信号
    df['ewma_divergence'] = df.groupby('SecuCode')['divergence_signal'].transform(
        lambda x: x.ewm(halflife=5, min_periods=1).mean()
    )
    
    # 计算过去20日EWMA发散信号的总和
    df['PriceVolEwmaDivergence'] = df.groupby('SecuCode')['ewma_divergence'].transform(
        lambda x: x.rolling(window=20, min_periods=1).sum()
    )
    
    # 处理无穷值
    df['PriceVolEwmaDivergence'] = df['PriceVolEwmaDivergence'].replace([np.inf, -np.inf], np.nan)
    
    # 返回结果
    result = df[['SecuCode', 'TradingDay', 'PriceVolEwmaDivergence']].copy()
    return result