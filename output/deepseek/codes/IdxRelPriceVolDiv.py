import pandas as pd
import numpy as np

def IdxRelPriceVolDiv(df_raw, df_index):
    """
    (1) 数学公式:
    PriceRatio_t = ClosePrice_t / HS300_t
    PriceRatioMax_20 = max(PriceRatio_{t-19}, ..., PriceRatio_t)
    VolumeMax_20 = max(TurnOverVolume_{t-19}, ..., TurnOverVolume_t)
    Factor_t = (PriceRatio_t / PriceRatioMax_20) - (TurnOverVolume_t / VolumeMax_20)
    
    (2) 因子金融逻辑解释:
    该因子衡量股票价格相对于HS300指数的相对强度与成交量相对强度的差异。
    价格相对强度部分反映当前股价相对于指数表现的历史高位水平，
    成交量相对强度部分反映当前成交活跃度的历史高位水平。
    因子值越大表明价格相对强度较高而成交量相对强度较低，可能预示股票有较好的相对表现。
    """
    
    # 在指数数据上计算HS300指数
    df_index = df_index[['TradingDay', 'HS300']].copy()
    
    # 合并HS300指数到个股数据，仅合并需要的列
    df = pd.merge(df_raw[['TradingDay', 'SecuCode', 'ClosePrice', 'TurnOverVolume']], 
                  df_index, on='TradingDay', how='left')
    
    # 计算价格比值
    df['PriceRatio'] = df['ClosePrice'] / df['HS300']
    
    # 分组计算滚动最大值
    df = df.sort_values(['SecuCode', 'TradingDay'])
    
    # 计算过去20日价格比值最大值
    df['PriceRatioMax_20'] = df.groupby('SecuCode')['PriceRatio'].rolling(
        window=20, min_periods=1).max().reset_index(level=0, drop=True)
    
    # 计算过去20日成交量最大值
    df['VolumeMax_20'] = df.groupby('SecuCode')['TurnOverVolume'].rolling(
        window=20, min_periods=1).max().reset_index(level=0, drop=True)
    
    # 计算因子值
    df['IdxRelPriceVolDiv'] = (df['PriceRatio'] / df['PriceRatioMax_20']) - (df['TurnOverVolume'] / df['VolumeMax_20'])
    
    # 处理无穷值
    df['IdxRelPriceVolDiv'] = df['IdxRelPriceVolDiv'].replace([np.inf, -np.inf], np.nan)
    
    # 返回结果
    return df[['SecuCode', 'TradingDay', 'IdxRelPriceVolDiv']]