"""
Alpha#1 因子

公式: rank(Ts_ArgMax(SignedPower(((returns<0)?stddev(returns,20):close),2.),5))-0.5)

说明：
- rank: 对所有股票进行某个指标的排序（标准化后除以总数，平均值是0）
- Ts_ArgMax: 在过去5天中找到最大值的索引位置
- SignedPower: 带符号的幂运算（保留符号）
- (returns<0)?stddev(returns,20):close: 如果收益率为负，使用20日下行波动率，否则使用收盘价
- 策略逻辑：对每只股票过去5天按照收盘价最高或下行波动率最高进行排名。
  下行波动率最高的一天离计算时间越近，越可以投资。收盘价最高离计算时间越近，越可以投资。

标签：mean-reversion+momentum
"""

data_list = [
    "/Users/user/Desktop/repo/crypto_trading/tmp/data/BTCUSDT_futures/BTCUSDT_1d_1095_20251127_113603.json",
    "/Users/user/Desktop/repo/crypto_trading/tmp/data/ETHUSDT_futures/ETHUSDT_1d_1095_20251127_114210.json",  
    "/Users/user/Desktop/repo/crypto_trading/tmp/data/TRUMPUSDT_futures/TRUMPUSDT_1d_1095_20251127_174403.json",
]


import pandas as pd
import numpy as np
from typing import Optional


def signed_power(x: float, power: float) -> float:
    """
    带符号的幂运算
    
    保留原始符号，然后取绝对值幂次方
    
    Args:
        x: 输入值
        power: 幂次
    
    Returns:
        带符号的幂运算结果
    """
    return np.sign(x) * (np.abs(x) ** power)


def alpha1_factor(
    data_slice: 'pd.DataFrame',
    lookback_days: int = 5,
    stddev_period: int = 20,
    power: float = 2.0
) -> float:
    """
    Alpha#1 因子计算
    
    计算过去lookback_days天内，哪个时间点具有最高的收盘价（当收益为正时）
    或最高的下行波动率（当收益为负时），距离当前时间越近，因子值越大。
    
    Args:
        data_slice: 数据切片，必须包含至少 max(lookback_days, stddev_period)+1 行数据
                   最后一行是当前数据点，前面是历史数据
        lookback_days: 回看天数（默认5，对应公式中的5）
        stddev_period: 标准差计算周期（默认20，对应公式中的20）
        power: 幂次（默认2.0，对应公式中的2.）
    
    Returns:
        因子值：
        - 正数：看多（最近的时间点具有更高的值）
        - 负数：看空（较远的时间点具有更高的值）
        - 0：数据不足
    """
    try:
        # 需要至少 lookback_days + stddev_period 行数据
        # 因为我们需要过去lookback_days天的数据，每一天可能需要过去stddev_period天的数据来计算stddev
        total_required = lookback_days + stddev_period
        if len(data_slice) < total_required + 1:
            return 0.0
        
        # 提取价格数据
        # 最后一行是当前数据点，我们需要过去 total_required 行的数据
        prices = data_slice.iloc[-(total_required + 1):]['close_price'].values
        
        # 计算收益率：从第i天到第i+1天的收益率
        # returns[i] = (prices[i+1] - prices[i]) / prices[i]
        returns = np.diff(prices) / prices[:-1]
        
        # 计算每个时间点的值（过去lookback_days天）
        values = []
        
        # 遍历过去lookback_days天（从最近到最远）
        # data_slice.iloc[-1] 是当前点（t）
        # data_slice.iloc[-2] 是 t-1
        # data_slice.iloc[-lookback_days-1] 是 t-lookback_days
        # 我们需要计算 t-1, t-2, ..., t-lookback_days 这lookback_days天的值
        
        for i in range(lookback_days):
            # i=0 表示 t-1（最近的一天），i=lookback_days-1 表示 t-lookback_days（最远的一天）
            # 在prices数组中的索引（从0开始，最后一个是当前点）
            # prices[0] 是最早的点，prices[-1] 是当前点
            # 对于 t-(i+1)，在prices中的索引是 len(prices) - 2 - i
            day_idx = len(prices) - 2 - i  # t-(i+1) 在prices中的索引
            
            # 需要至少stddev_period个收益率来计算stddev，且需要day_idx > 0来获取结束于day_idx的收益率
            if day_idx < stddev_period or day_idx == 0:
                # 数据不足，无法计算stddev
                return 0.0
            
            # 获取该天的收盘价
            close_price = prices[day_idx]
            
            # 计算结束于day_idx的收益率（从day_idx-1到day_idx）
            # returns[day_idx-1] = (prices[day_idx] - prices[day_idx-1]) / prices[day_idx-1]
            current_return = returns[day_idx - 1]
            
            # 根据收益率选择指标
            if current_return < 0:
                # 如果收益率为负，使用过去stddev_period天的收益率标准差
                # 获取过去stddev_period天的收益率（结束于day_idx）
                # 注意：returns[i] 是从 prices[i] 到 prices[i+1] 的收益率
                # 所以结束于 day_idx 的过去 stddev_period 个收益率是 returns[day_idx-stddev_period:day_idx]
                start_idx = day_idx - stddev_period
                end_idx = day_idx
                returns_window = returns[start_idx:end_idx]
                
                # 计算收益率的标准差（下行波动率）
                # 根据描述"下行波动率"，只考虑负收益的标准差
                if len(returns_window) > 0:
                    negative_returns = returns_window[returns_window < 0]
                    if len(negative_returns) > 0:
                        downside_std = np.std(negative_returns)
                        value = downside_std
                    else:
                        # 如果没有负收益，使用所有收益的标准差
                        value = np.std(returns_window)
                else:
                    # 数据不足（理论上不应该发生，因为我们已经检查了day_idx >= stddev_period）
                    value = 0.0
            else:
                # 如果收益率为正或0，使用收盘价
                value = close_price
            
            # 应用SignedPower
            powered_value = signed_power(value, power)
            values.append(powered_value)
        
        # 找到最大值的索引（argmax）
        # values[0]是最新的（t-1），values[-1]是最旧的（t-lookback_days）
        if len(values) == 0:
            return 0.0
        
        # 处理NaN值
        values_array = np.array(values)
        valid_mask = ~np.isnan(values_array)
        if not np.any(valid_mask):
            return 0.0
        
        # 找到有效值中的最大值索引
        valid_values = values_array[valid_mask]
        valid_indices = np.where(valid_mask)[0]
        max_idx_in_valid = np.argmax(valid_values)
        argmax = valid_indices[max_idx_in_valid]
        
        # argmax: 0表示最近的一天（t-1），lookback_days-1表示最远的一天（t-lookback_days）
        # 距离当前时间越近（argmax越小），因子值应该越大
        
        # 归一化：将argmax转换为[0, 1]范围，然后减去0.5得到[-0.5, 0.5]
        # argmax=0 (最近) -> normalized=1.0 -> factor=0.5 (最看多)
        # argmax=lookback_days-1 (最远) -> normalized=0.0 -> factor=-0.5 (最看空)
        if lookback_days > 1:
            normalized = 1.0 - (argmax / (lookback_days - 1))
        else:
            normalized = 1.0
        
        factor_value = normalized - 0.5
        
        return float(factor_value)
        
    except Exception as e:
        # 如果计算出错，返回0
        return 0.0

