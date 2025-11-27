import pandas as pd
import numpy as np

def VolStdAdjDivergence(df_raw, df_index):
    """
    (1) 数学公式:
    因子值 = (过去20日价格创新高但成交量未创新高的天数比例) / (过去20日收益率标准差)
    
    其中:
    - 价格创新高: ClosePrice > 过去20日最高价
    - 成交量未创新高: TurnOverVolume <= 过去20日最高成交量
    - 天数比例 = 满足条件的天数 / 20
    - 收益率标准差 = std(ClosePrice.pct_change())
    
    (2) 因子金融逻辑:
    该因子捕捉价格与成交量的背离现象。当价格创新高但成交量未能同步创新高时，
    可能意味着上涨动力不足。通过除以收益率标准差来标准化波动率效应，
    使得因子值在不同波动率水平的股票间具有可比性。
    """
    
    # 复制数据避免修改原数据
    df = df_raw.copy()
    
    # 按个股分组计算滚动窗口指标
    df = df.sort_values(['SecuCode', 'TradingDay'])
    
    # 计算过去20日最高价和最高成交量
    df['rolling_high_20'] = df.groupby('SecuCode')['HighPrice'].transform(
        lambda x: x.rolling(window=20, min_periods=1).max()
    )
    df['rolling_volume_high_20'] = df.groupby('SecuCode')['TurnOverVolume'].transform(
        lambda x: x.rolling(window=20, min_periods=1).max()
    )
    
    # 判断价格创新高但成交量未创新高的条件
    df['price_new_high'] = (df['ClosePrice'] > df['rolling_high_20'].shift(1)).astype(int)
    df['volume_not_new_high'] = (df['TurnOverVolume'] <= df['rolling_volume_high_20'].shift(1)).astype(int)
    df['divergence_signal'] = df['price_new_high'] & df['volume_not_new_high']
    
    # 计算过去20日背离信号的比例
    df['divergence_ratio'] = df.groupby('SecuCode')['divergence_signal'].transform(
        lambda x: x.rolling(window=20, min_periods=1).mean()
    )
    
    # 计算过去20日收益率标准差
    df['returns'] = df.groupby('SecuCode')['ClosePrice'].pct_change()
    df['returns_std_20'] = df.groupby('SecuCode')['returns'].transform(
        lambda x: x.rolling(window=20, min_periods=1).std()
    )
    
    # 计算最终因子值
    df['VolStdAdjDivergence'] = df['divergence_ratio'] / df['returns_std_20']
    
    # 处理无穷值
    df['VolStdAdjDivergence'] = df['VolStdAdjDivergence'].replace([np.inf, -np.inf], np.nan)
    
    # 返回结果
    result = df[['SecuCode', 'TradingDay', 'VolStdAdjDivergence']].copy()
    return result