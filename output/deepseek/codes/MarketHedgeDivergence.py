import pandas as pd
import numpy as np

def MarketHedgeDivergence(df_raw, df_index):
    """
    (1) 数学公式:
    股票指标 = (过去20日内 ClosePrice > 前20日最高价 且 TurnOverVolume < 前20日最大成交量 的天数) / 20
    指数指标 = (过去20日内 HS300 > 前20日最高价 且 指数成交量 < 前20日最大成交量的天数) / 20
    因子值 = 股票指标 - 指数指标
    
    (2) 因子金融逻辑解释:
    该因子捕捉价格与成交量的背离现象。当股票价格创新高但成交量未创新高时，可能表明上涨动力不足。
    通过减去HS300指数的相同指标，去除市场整体影响，得到个股相对于市场的独特背离特征。
    """
    
    # 复制数据避免修改原数据
    df_stock = df_raw.copy()
    df_idx = df_index.copy()
    
    # 股票端计算
    df_stock = df_stock.sort_values(['SecuCode', 'TradingDay'])
    
    # 计算20日滚动最高价和最大成交量
    df_stock['rolling_high_20'] = df_stock.groupby('SecuCode')['HighPrice'].transform(
        lambda x: x.rolling(window=20, min_periods=1).max()
    )
    df_stock['rolling_volume_max_20'] = df_stock.groupby('SecuCode')['TurnOverVolume'].transform(
        lambda x: x.rolling(window=20, min_periods=1).max()
    )
    
    # 计算价格创新高但成交量未创新高的条件
    df_stock['price_new_high'] = (df_stock['ClosePrice'] > df_stock.groupby('SecuCode')['rolling_high_20'].shift(1))
    df_stock['volume_not_new_high'] = (df_stock['TurnOverVolume'] < df_stock.groupby('SecuCode')['rolling_volume_max_20'].shift(1))
    df_stock['divergence_flag'] = (df_stock['price_new_high'] & df_stock['volume_not_new_high']).astype(int)
    
    # 计算20日滚动求和
    df_stock['stock_divergence_ratio'] = df_stock.groupby('SecuCode')['divergence_flag'].transform(
        lambda x: x.rolling(window=20, min_periods=1).sum() / 20
    )
    
    # 指数端计算
    df_idx = df_idx.sort_values('TradingDay')
    
    # 计算HS300的20日滚动最高价
    df_idx['hs300_rolling_high_20'] = df_idx['HS300'].rolling(window=20, min_periods=1).max()
    
    # 由于指数数据没有成交量，使用市场总成交量作为代理
    df_idx['market_volume'] = df_idx['SZ']  # 使用深证成指作为成交量代理
    df_idx['market_volume_rolling_max_20'] = df_idx['market_volume'].rolling(window=20, min_periods=1).max()
    
    # 计算指数价格创新高但成交量未创新高的条件
    df_idx['hs300_price_new_high'] = (df_idx['HS300'] > df_idx['hs300_rolling_high_20'].shift(1))
    df_idx['market_volume_not_new_high'] = (df_idx['market_volume'] < df_idx['market_volume_rolling_max_20'].shift(1))
    df_idx['index_divergence_flag'] = (df_idx['hs300_price_new_high'] & df_idx['market_volume_not_new_high']).astype(int)
    
    # 计算指数20日滚动求和
    df_idx['index_divergence_ratio'] = df_idx['index_divergence_flag'].rolling(window=20, min_periods=1).sum() / 20
    
    # 仅保留需要的指数列用于合并
    df_idx_result = df_idx[['TradingDay', 'index_divergence_ratio']].copy()
    
    # 合并股票和指数数据
    df_result = pd.merge(df_stock, df_idx_result, on='TradingDay', how='left')
    
    # 计算最终因子值
    df_result['MarketHedgeDivergence'] = df_result['stock_divergence_ratio'] - df_result['index_divergence_ratio']
    
    # 处理无穷值
    df_result['MarketHedgeDivergence'] = df_result['MarketHedgeDivergence'].replace([np.inf, -np.inf], np.nan)
    
    # 返回指定列
    return df_result[['SecuCode', 'TradingDay', 'MarketHedgeDivergence']]