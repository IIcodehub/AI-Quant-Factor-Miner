import pandas as pd
import numpy as np

def MedPriceVolDiv(df_raw, df_index):
    """
    因子公式:
    MedPriceVolDiv = (当前价格中位数 / 过去20日价格中位数最高值) - (当前成交量中位数 / 过去20日成交量中位数最高值)
    
    金融逻辑:
    该因子通过比较当前价格和成交量相对于近期历史最高中位数的相对位置，捕捉价格和成交量的相对强度。
    当价格相对强度高于成交量相对强度时，因子值为正，反之为负。
    """
    
    # 按个股分组计算
    result = df_raw.groupby('SecuCode').apply(lambda x: pd.DataFrame({
        'TradingDay': x['TradingDay'],
        'SecuCode': x['SecuCode'],
        # 计算20日滚动中位数
        'price_median': x['ClosePrice'].rolling(window=20, min_periods=1).median(),
        'volume_median': x['TurnOverVolume'].rolling(window=20, min_periods=1).median()
    })).reset_index(drop=True)
    
    # 计算过去20日价格中位数最高值
    result['price_median_max'] = result.groupby('SecuCode')['price_median'].rolling(
        window=20, min_periods=1).max().reset_index(level=0, drop=True)
    
    # 计算过去20日成交量中位数最高值
    result['volume_median_max'] = result.groupby('SecuCode')['volume_median'].rolling(
        window=20, min_periods=1).max().reset_index(level=0, drop=True)
    
    # 计算因子值
    result['MedPriceVolDiv'] = (
        result['price_median'] / result['price_median_max'] - 
        result['volume_median'] / result['volume_median_max']
    )
    
    # 处理无穷值
    result['MedPriceVolDiv'] = result['MedPriceVolDiv'].replace([np.inf, -np.inf], np.nan)
    
    # 返回指定列
    return result[['SecuCode', 'TradingDay', 'MedPriceVolDiv']]