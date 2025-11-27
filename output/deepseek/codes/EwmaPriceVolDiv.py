import pandas as pd
import numpy as np

def EwmaPriceVolDiv(df_raw, df_index):
    """
    因子公式:
    EwmaPriceVolDiv = (EWMA_Price_t / max(EWMA_Price_{t-19:t})) - (EWMA_Volume_t / max(EWMA_Volume_{t-19:t}))
    
    金融逻辑:
    计算价格和成交量的指数加权移动平均比率差异。通过比较当前EWMA价格与近期最高EWMA价格的相对位置，
    以及当前EWMA成交量与近期最高EWMA成交量的相对位置，捕捉价格和成交量动量的背离信号。
    正值表示价格动量相对强于成交量动量，负值表示成交量动量相对强于价格动量。
    """
    
    # 复制数据避免修改原数据
    df = df_raw.copy()
    
    # 按股票分组计算EWMA
    df['ewma_price'] = df.groupby('SecuCode')['ClosePrice'].transform(
        lambda x: x.ewm(alpha=0.06, adjust=False).mean()
    )
    df['ewma_volume'] = df.groupby('SecuCode')['TurnOverVolume'].transform(
        lambda x: x.ewm(alpha=0.06, adjust=False).mean()
    )
    
    # 计算过去20日EWMA价格和成交量的滚动最大值
    df['max_ewma_price_20d'] = df.groupby('SecuCode')['ewma_price'].transform(
        lambda x: x.rolling(window=20, min_periods=1).max()
    )
    df['max_ewma_volume_20d'] = df.groupby('SecuCode')['ewma_volume'].transform(
        lambda x: x.rolling(window=20, min_periods=1).max()
    )
    
    # 计算价格和成交量的比率
    df['price_ratio'] = df['ewma_price'] / df['max_ewma_price_20d']
    df['volume_ratio'] = df['ewma_volume'] / df['max_ewma_volume_20d']
    
    # 计算因子值
    df['EwmaPriceVolDiv'] = df['price_ratio'] - df['volume_ratio']
    
    # 处理无穷大值
    df['EwmaPriceVolDiv'] = df['EwmaPriceVolDiv'].replace([np.inf, -np.inf], np.nan)
    
    # 返回结果
    result = df[['SecuCode', 'TradingDay', 'EwmaPriceVolDiv']].copy()
    return result