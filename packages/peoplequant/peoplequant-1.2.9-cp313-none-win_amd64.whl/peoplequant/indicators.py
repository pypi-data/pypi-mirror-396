import polars as pl
import numpy as np
from typing import Union

def _expr(column: str | pl.Expr ) -> pl.Expr:
    if isinstance(column, str):
        expr = pl.col(column)
    else:
        expr = column
    return expr

# ================ EMA / MA ==================

def EMA_expr(column: str | pl.Expr, span: int) -> pl.Expr:
    '''
    Args:
        column: 列名或该列的polars表达式
        span： 周期
    Return:
        polars.Expr
    '''
    col = _expr(column)
    return col.ewm_mean(span=span, adjust=False)

def EMA_df(df: pl.DataFrame, span: int, column: str = "close", output_name: str = "ema") -> pl.DataFrame:
    '''
    Args:
        df: K线数据,polars.DataFrame
        span： 周期
        column： 计算数据列
        output_name： 输出结果列名
    Return:
        包含原数据df和计算结果的polars.DataFrame
    '''
    return df.with_columns(EMA_expr(column, span).alias(output_name))

def MA_expr(column: str | pl.Expr, window: int) -> pl.Expr:
    '''
    Args:
        column: 列名或该列的polars表达式
        window： 周期
    Return:
        polars.Expr
    '''
    col = _expr(column)
    return col.rolling_mean(window_size=window)

def MA_df(df: pl.DataFrame, window: int, column: str = "close", output_name: str = "ma") -> pl.DataFrame:
    '''
    Args:
        df: K线数据,polars.DataFrame
        window： 周期
        column： 计算数据列
        output_name： 输出结果列名
    Return:
        包含原数据df和计算结果的polars.DataFrame
    '''
    return df.with_columns(MA_expr(column, window).alias(output_name))

# ================ MACD ==================

def MACD_expr(
    column: str | pl.Expr = "close",
    short: int = 12,
    long: int = 26,
    signal: int = 9,
    output_name: str = ""
) -> pl.Expr:
    '''
    Args:
        column: 列名或该列的polars表达式
        short： 短周期
        long： 长周期
        signal： 信号周期
    Return:
        polars.Expr
    '''
    price = _expr(column)
    diff = EMA_expr(price, short) - EMA_expr(price, long)
    dea = diff.ewm_mean(span=signal, adjust=False)
    bar = (diff - dea) * 2
    return pl.struct(**{f"{output_name}diff": diff, f"{output_name}dea": dea, f"{output_name}bar": bar})

def MACD_df(
    df: pl.DataFrame,
    short: int = 12,
    long: int = 26,
    signal: int = 9,
    column: str = "close",
    output_name: str = ""
) -> pl.DataFrame:
    '''
    Args:
        df: K线数据,polars.DataFrame
        short： 短周期
        long： 长周期
        signal： 信号周期
        column: 列名或该列的polars表达式
    Return:
        包含原数据df和计算结果的polars.DataFrame
    '''
    return df.with_columns(MACD_expr(column, short, long, signal,output_name).alias("macd")).unnest("macd")

# ================ BOLL (布林带) ==================

def BOLL_expr(
    column: str | pl.Expr = "close",
    n: int = 20,
    p: float = 2.0,
    output_name: str = ""
) -> pl.Expr:
    '''
    Args:
        column: 列名或该列的polars表达式
        n： 周期
        p: 倍数
    Return:
        polars.Expr
    '''
    price = _expr(column)
    mid = price.rolling_mean(window_size=n)
    std = price.rolling_std(window_size=n, ddof=0)
    top = mid + p * std
    bottom = mid - p * std
    return pl.struct(**{f"{output_name}mid": mid, f"{output_name}top": top, f"{output_name}bottom": bottom})

def BOLL_df(
    df: pl.DataFrame,
    n: int = 20,
    p: float = 2.0,
    column: str = "close",
    output_name: str = ""
) -> pl.DataFrame:
    '''
    Args:
        df: K线数据,polars.DataFrame
        n： 周期
        p: 倍数
        column: 列名或该列的polars表达式
    Return:
        包含原数据df和计算结果的polars.DataFrame
    '''
    return df.with_columns(BOLL_expr(column, n, p,output_name).alias("boll")).unnest("boll")

# ================ RSI ==================

def RSI_expr(column: str | pl.Expr = "close", window: int = 14) -> pl.Expr:
    price = _expr(column)
    delta = price.diff()
    
    # 替代 clip_min(0)
    up = delta.clip(0, None)      # 相当于 max(delta, 0)
    down = (-delta).clip(0, None) # 相当于 max(-delta, 0)
    
    ema_up = up.ewm_mean(span=window, adjust=False)
    ema_down = down.ewm_mean(span=window, adjust=False)
    
    rs = pl.when(ema_down == 0).then(float('inf')).otherwise(ema_up / ema_down)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi.fill_null(100.0).fill_nan(100.0)  # 防止 NaN/Null

def RSI_df(
    df: pl.DataFrame,
    window: int = 14,
    column: str = "close",
    output_name: str = "rsi"
) -> pl.DataFrame:
    return df.with_columns(RSI_expr(column, window).alias(output_name))

# ================ ATR ==================

def ATR_expr(window: int = 14) -> pl.Expr:
    hl = pl.col("high") - pl.col("low")
    hc = (pl.col("high") - pl.col("close").shift(1)).abs()
    lc = (pl.col("low") - pl.col("close").shift(1)).abs()
    tr = pl.max_horizontal([hl, hc, lc])
    return tr.ewm_mean(span=window, adjust=False)

def ATR_df(
    df: pl.DataFrame,
    window: int = 14,
    output_name: str = "atr"
) -> pl.DataFrame:
    return df.with_columns(ATR_expr(window).alias(output_name))

# ================ KDJ ==================

def KDJ_expr(n: int = 9, m1: int = 3, m2: int = 3, output_name = '') -> pl.Expr:
    hv = pl.col("high").rolling_max(window_size=n)
    lv = pl.col("low").rolling_min(window_size=n)
    rsv = pl.when(hv == lv).then(0.0).otherwise((pl.col("close") - lv) / (hv - lv) * 100)
    k = rsv.ewm_mean(alpha=m1 / n, adjust=False)
    d = k.ewm_mean(alpha=m2 / m1, adjust=False)
    j = 3 * k - 2 * d
    return pl.struct(**{f"{output_name}k": k, f"{output_name}d": d, f"{output_name}j": j})

def KDJ_df(
    df: pl.DataFrame,
    n: int = 9,
    m1: int = 3,
    m2: int = 3,
    output_name = ''
) -> pl.DataFrame:
    return df.with_columns(KDJ_expr(n, m1, m2, output_name).alias("kdj")).unnest("kdj")

# ================ CCI ==================

def CCI_expr(window: int = 20 ) -> pl.Expr:
    typ = (pl.col("high") + pl.col("low") + pl.col("close")) / 3.0
    ma_typ = typ.rolling_mean(window_size=window)
    std_typ = typ.rolling_std(window_size=window, ddof=0)
    return (typ - ma_typ) / (0.015 * std_typ)

def CCI_df(
    df: pl.DataFrame,
    window: int = 20,
    output_name: str = "cci"
) -> pl.DataFrame:
    return df.with_columns(CCI_expr(window).alias(output_name))

# ================ OBV ==================

def OBV_expr() -> pl.Expr:
    close = pl.col("close")
    volume = pl.col("volume")
    obv_delta = (
        pl.when(close > close.shift(1)).then(volume)
        .when(close < close.shift(1)).then(-volume)
        .otherwise(0)
    )
    return obv_delta.cumsum()

def OBV_df(
    df: pl.DataFrame,
    output_name: str = "obv"
) -> pl.DataFrame:
    return df.with_columns(OBV_expr().alias(output_name))

# ================ DMI (包含 ATR) ==================
# 注意：DMI 较复杂，表达式版仍返回 struct

def DMI_expr(n: int = 14, m: int = 6, output_name = '') -> pl.Expr:
    # ATR
    hl = pl.col("high") - pl.col("low")
    hc = (pl.col("high") - pl.col("close").shift(1)).abs()
    lc = (pl.col("low") - pl.col("close").shift(1)).abs()
    tr = pl.max_horizontal([hl, hc, lc])
    atr = tr.ewm_mean(span=n, adjust=False)

    # Directional Movement
    pre_high = pl.col("high").shift(1)
    pre_low = pl.col("low").shift(1)
    hd = pl.col("high") - pre_high
    ld = pre_low - pl.col("low")

    admp = pl.when((hd > 0) & (hd > ld)).then(hd).otherwise(0.0)
    admm = pl.when((ld > 0) & (ld > hd)).then(ld).otherwise(0.0)

    ma_admp = admp.rolling_mean(window_size=n)
    ma_admm = admm.rolling_mean(window_size=n)

    pdi = pl.when(atr > 0).then(ma_admp / atr * 100).otherwise(None).forward_fill()
    mdi = pl.when(atr > 0).then(ma_admm / atr * 100).otherwise(None).forward_fill()

    ad = (pdi - mdi).abs() / (pdi + mdi) * 100
    adx = ad.rolling_mean(window_size=m)
    adxr = (adx + adx.shift(m)) / 2

    return pl.struct(**{
        f"{output_name}atr": atr,
        f"{output_name}pdi": pdi,
        f"{output_name}mdi": mdi,
        f"{output_name}adx": adx,
        f"{output_name}adxr": adxr
    })

def DMI_df(
    df: pl.DataFrame,
    n: int = 14,
    m: int = 6,
    output_name = ''
) -> pl.DataFrame:
    return df.with_columns(DMI_expr(n, m, output_name).alias("dmi")).unnest("dmi")

# ================ SAR ==================
# 注意：SAR 无法向量化，仅提供 DataFrame 版本（或接受性能损失）

def SAR_df(
    df: pl.DataFrame,
    step: float = 0.02,
    max_step: float = 0.2,
    output_name: str = "sar"
) -> pl.DataFrame:
    def calculate_sar(rows):
        if not rows:
            return []
        sar_vals = []
        high0, low0 = rows[0][0], rows[0][1]
        ep = high0
        af = step
        trend = 1  # 1=up, -1=down
        sar = low0  # initial sar
        sar_vals.append(sar)

        for i in range(1, len(rows)):
            high, low = rows[i]
            prev_sar = sar_vals[-1]

            if trend == 1:
                sar = prev_sar + af * (ep - prev_sar)
                if low < sar:
                    trend = -1
                    sar = ep
                    af = step
                    ep = low
                else:
                    if high > ep:
                        ep = high
                        af = min(af + step, max_step)
            else:
                sar = prev_sar - af * (prev_sar - ep)
                if high > sar:
                    trend = 1
                    sar = ep
                    af = step
                    ep = high
                else:
                    if low < ep:
                        ep = low
                        af = min(af + step, max_step)
            sar_vals.append(sar)
        return sar_vals

    hl_rows = df.select(["high", "low"]).rows()
    sar_series = calculate_sar(hl_rows)
    return df.with_columns(pl.Series(output_name, sar_series))


def REF_expr(column: str | pl.Expr , n: int) -> pl.Expr:
    """引用前 n 周期的值"""
    expr = _expr(column)
    return expr.shift(n)

def REF_df(df: pl.DataFrame, column: str, n: int, output: str = 'ref') -> pl.DataFrame:
    """引用前 n 周期的值"""
    return df.with_columns(REF_expr(column, n).alias(output))

def HHV_expr(column: str | pl.Expr, n: int) -> pl.Expr:
    """n 周期内最高值"""
    expr = _expr(column)
    return expr.rolling_max(window_size=n)

def HHV_df(df: pl.DataFrame, column: str, n: int, output: str = 'hhv') -> pl.DataFrame:
    """引用前 n 周期的值"""
    return df.with_columns(HHV_expr(column, n).alias(output))

def LLV_expr(column: str | pl.Expr, n: int) -> pl.Expr:
    """n 周期内最高值"""
    expr = _expr(column)
    return expr.rolling_min(window_size=n)

def LLV_df(df: pl.DataFrame, column: str, n: int, output: str = 'llv') -> pl.DataFrame:
    """引用前 n 周期的值"""
    return df.with_columns(LLV_expr(column, n).alias(output))

def CROSSUP_expr(column_a: str | pl.Expr, column_b: str | pl.Expr) -> pl.Expr:
    """a 上穿 b"""
    a = _expr(column_a)
    b = _expr(column_b)
    return (a > b) & (REF_expr(a, 1) <= REF_expr(b, 1))

def CROSSUP_df(
    df: pl.DataFrame,
    column_a: str,
    column_b: str,
    output: str = "crossup"
) -> pl.DataFrame:
    """a 上穿 b"""
    return df.with_columns(
        CROSSUP_expr(pl.col(column_a), pl.col(column_b)).alias(output)
    )

def CROSSDOWN_expr(column_a: str | pl.Expr, column_b: str | pl.Expr) -> pl.Expr:
    """a 下穿 b"""
    a = _expr(column_a)
    b = _expr(column_b)
    return (a < b) & (REF_expr(a, 1) >= REF_expr(b, 1))

def CROSSDOWN_df(
    df: pl.DataFrame,
    column_a: str,
    column_b: str,
    output: str = "crossdown"
) -> pl.DataFrame:
    """a 下穿 b"""
    return df.with_columns(
        CROSSDOWN_expr(pl.col(column_a), pl.col(column_b)).alias(output)
    )

def BARSLAST_expr(condition: pl.Expr) -> pl.Expr:
    """
    返回上一次 condition == True 到当前的 bar 数（不包含当前）
    若从未发生，返回 null
    """
    # 创建分组：每次 condition 为 True 时开启新组
    group = condition.cast(pl.Int32).cum_sum().fill_null(0)
    # 在每组内计算行号（从 0 开始）
    row_num = pl.int_range(0, pl.len()).over(group)
    # 如果当前 condition 为 True，则 barslast = 0；否则 = row_num - 1
    return pl.when(condition).then(0).otherwise(row_num - 1)

def BARSLAST_df(
    df: pl.DataFrame,
    condition_col: str,
    output_name: str = "barslast"
) -> pl.DataFrame:
    """
    添加一列：从上一次 condition_col == True 到当前的周期数
    condition_col 必须是 bool 类型列
    """
    return df.with_columns(
        BARSLAST_expr(pl.col(condition_col)).alias(output_name)
    )

def VALUEWHEN_expr(condition: pl.Expr, source: pl.Expr) -> pl.Expr:
    """当 condition 为 True 时取 source 值，并向前填充"""
    return pl.when(condition).then(source).otherwise(None).forward_fill()

def VALUEWHEN_df(
    df: pl.DataFrame,
    condition_col: str,
    source_col: str,
    output_name: str = "valuewhen"
) -> pl.DataFrame:
    """
    当 condition_col 为 True 时，取 source_col 的值，并向前填充
    
    Parameters:
        df: 输入 DataFrame
        condition_col: 布尔类型列名（如 'gold_cross'）
        source_col: 源数据列名（如 'close'）
        output_name: 输出列名
    """
    return df.with_columns(
        VALUEWHEN_expr(pl.col(condition_col), pl.col(source_col)).alias(output_name)
    )

# ================ STD (标准差) ==================
def STD_expr(column: str | pl.Expr, window: int) -> pl.Expr:
    col = _expr(column)
    return col.rolling_std(window_size=window, ddof=0)

def STD_df(df: pl.DataFrame, column: str, window: int, output_name: str = "std") -> pl.DataFrame:
    return df.with_columns(STD_expr(column, window).alias(output_name))

# ================ MAX / MIN ==================
# 为兼容性，提供 MAX_expr / MIN_expr 别名
MAX_expr = HHV_expr
MIN_expr = LLV_expr

def MAX_df(df: pl.DataFrame, column: str, n: int, output_name: str = "max") -> pl.DataFrame:
    return df.with_columns(MAX_expr(column, n).alias(output_name))

def MIN_df(df: pl.DataFrame, column: str, n: int, output_name: str = "min") -> pl.DataFrame:
    return df.with_columns(MIN_expr(column, n).alias(output_name))

# ================ SMA (简单移动平均) ==================
# SMA 就是 MA，这里提供别名
SMA_expr = MA_expr
SMA_df = MA_df

# ================ DMA (动态移动平均) ==================
# 常见定义1：(H + L + C) / 3 的 MA
# 常见定义2：短期 MA - 长期 MA（类似 MACD 的 diff）
# 这里采用 **定义2**（更常见于 A 股软件）

def DMA_expr(
    column: str | pl.Expr = "close",
    short: int = 10,
    long: int = 50
) -> pl.Expr:
    col = _expr(column)
    ma_short = col.rolling_mean(window_size=short)
    ma_long = col.rolling_mean(window_size=long)
    return ma_short - ma_long

def DMA_df(
    df: pl.DataFrame,
    column: str = "close",
    short: int = 10,
    long: int = 50,
    output_name: str = "dma"
) -> pl.DataFrame:
    return df.with_columns(DMA_expr(column, short, long).alias(output_name))

# ================ MTM (动量) ==================
def MTM_expr(column: str | pl.Expr, n: int) -> pl.Expr:
    col = _expr(column)
    return col - col.shift(n)

def MTM_df(
    df: pl.DataFrame,
    column: str,
    n: int,
    output_name: str = "mtm"
) -> pl.DataFrame:
    return df.with_columns(MTM_expr(column, n).alias(output_name))


# ================ MACD 背离检测（表达式版）=================

def MACD_divergence_expr(
    close: pl.Expr | str = "close",
    macd_diff: pl.Expr | str = "diff",   # 可替换为 "bar"
    lookback: int = 20,                  # 寻找高低点的窗口
    output_prefix: str = "macd_"
) -> pl.Expr:
    """
    检测 MACD 顶背离与底背离
    
    返回 struct 包含：
      - bearish: bool (顶背离)
      - bullish: bool (底背离)
    """
    close = _expr(close)
    macd_diff = _expr(macd_diff)
    
    # 1. 识别有效高点和低点（排除平台）
    is_high = (close == HHV_expr(close, lookback)) & (close > REF_expr(close, 1))
    is_low  = (close == LLV_expr(close, lookback)) & (close < REF_expr(close, 1))

    # 2. 记录最近一次高点/低点的价格和 MACD
    last_high_price = VALUEWHEN_expr(is_high, close)
    last_high_macd  = VALUEWHEN_expr(is_high, macd_diff)
    prev_high_price = REF_expr(last_high_price, 1)
    prev_high_macd  = REF_expr(last_high_macd, 1)

    last_low_price = VALUEWHEN_expr(is_low, close)
    last_low_macd  = VALUEWHEN_expr(is_low, macd_diff)
    prev_low_price = REF_expr(last_low_price, 1)
    prev_low_macd  = REF_expr(last_low_macd, 1)

    # 3. 顶背离：当前是高点，且 price > 前高，但 MACD < 前高 MACD
    bearish = (
        is_high &
        prev_high_price.is_not_null() &
        (close > prev_high_price) &
        (macd_diff < prev_high_macd)
    )

    # 4. 底背离：当前是低点，且 price < 前低，但 MACD > 前低 MACD
    bullish = (
        is_low &
        prev_low_price.is_not_null() &
        (close < prev_low_price) &
        (macd_diff > prev_low_macd)
    )

    return pl.struct(**{
        f"{output_prefix}bearish": bearish,
        f"{output_prefix}bullish": bullish
    })

# ================ DataFrame 版本 ==================

def MACD_divergence_df(
    df: pl.DataFrame,
    close_col: str = "close",
    macd_diff_col: str = "diff",   # 确保已计算 MACD 并 unnest
    lookback: int = 20,
    output_prefix: str = "macd_"
) -> pl.DataFrame:
    """
    在 DataFrame 中添加 MACD 背离信号列
    
    要求：df 必须包含 'diff' 列（来自 MACD_df）
    """
    return (
        df
        .with_columns(
            MACD_divergence_expr(close_col, macd_diff_col, lookback, output_prefix)
            .alias("_div_signal")
        )
        .unnest("_div_signal")
    )

# ================ Donchian Channel ==================

def DONCHIAN_expr(
    high: pl.Expr | str = "high",
    low: pl.Expr | str = "low",
    window: int = 20,
    output_name: str = "donchian_"
) -> pl.Expr:
    """
    唐奇安通道（Donchian Channel）
    
    Returns:
        struct { upper, lower, middle }
    """
    high = _expr(high)
    low = _expr(low)
    upper = high.rolling_max(window_size=window)
    lower = low.rolling_min(window_size=window)
    middle = (upper + lower) / 2.0
    return pl.struct(**{
        f"{output_name}upper": upper,
        f"{output_name}lower": lower,
        f"{output_name}middle": middle
    })

def DONCHIAN_df(
    df: pl.DataFrame,
    high_col: str = "high",
    low_col: str = "low",
    window: int = 20,
    output_name: str = "donchian_"
) -> pl.DataFrame:
    """
    添加唐奇安通道三轨
    """
    return (
        df
        .with_columns(
            DONCHIAN_expr(high_col, low_col, window,output_name).alias("_donchian")
        )
        .unnest("_donchian")
    )


def _linear_regression_channel_numpy(
    prices: np.ndarray,
    window: int,
    k: float = 2.0
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    使用 NumPy 向量化计算滚动线性回归通道
    
    Returns:
        mid, upper, lower (all np.ndarray, same length as prices)
    """
    n = len(prices)
    if n < window:
        nan_array = np.full(n, np.nan)
        return nan_array, nan_array, nan_array

    # 构造滚动窗口：shape = (n - window + 1, window)
    windows = np.lib.stride_tricks.sliding_window_view(prices, window_shape=window)

    # 时间索引 x = [0, 1, ..., window-1]
    x = np.arange(window, dtype=np.float64)
    x_mean = (window - 1) / 2.0
    S_xx = np.sum((x - x_mean) ** 2)  # 标量，所有窗口相同

    # 计算每个窗口的 y_mean
    y_means = np.mean(windows, axis=1)  # shape: (n - window + 1,)

    # 计算 S_xy = sum((x_i - x_mean) * (y_i - y_mean))
    # 等价于: sum(x_i * y_i) - window * x_mean * y_mean
    xy_sum = np.sum(x * windows, axis=1)
    S_xy = xy_sum - window * x_mean * y_means

    # 斜率和截距
    slopes = S_xy / S_xx  # shape: (n - window + 1,)
    intercepts = y_means - slopes * x_mean

    # 当前点（窗口最后一个）的预测值: y_pred = slope * (window-1) + intercept
    y_pred = slopes * (window - 1) + intercepts

    # 计算残差标准差
    y_fitted = slopes[:, None] * x[None, :] + intercepts[:, None]  # 广播，shape: (..., window)
    residuals = windows - y_fitted
    std_devs = np.std(residuals, axis=1, ddof=0)  # 总体标准差

    # 构建完整长度的结果数组
    full_length = n
    mid = np.full(full_length, np.nan)
    upper = np.full(full_length, np.nan)
    lower = np.full(full_length, np.nan)

    start_idx = window - 1
    mid[start_idx:] = y_pred
    upper[start_idx:] = y_pred + k * std_devs
    lower[start_idx:] = y_pred - k * std_devs

    return mid, upper, lower


def LINREG_CHANNEL_df(
    df: pl.DataFrame,
    price_col: str = "close",
    window: int = 14,
    k: float = 2.0,
    output_prefix: str = "lr"
) -> pl.DataFrame:
    """
    高性能线性回归通道（基于 NumPy 向量化）
    
    Parameters:
        df: 输入 Polars DataFrame
        price_col: 价格列名
        window: 回归窗口
        k: 通道宽度倍数（标准差）
        output_prefix: 输出列前缀
    
    Returns:
        pl.DataFrame with {prefix}_mid, {prefix}_upper, {prefix}_lower
    """
    # 提取价格列并转为 NumPy
    prices = df[price_col].to_numpy()

    # 计算通道
    mid, upper, lower = _linear_regression_channel_numpy(prices, window, k)

    # 转回 Polars 并合并
    result_df = df.with_columns([
        pl.Series(f"{output_prefix}_mid", mid, dtype=pl.Float64),
        pl.Series(f"{output_prefix}_upper", upper, dtype=pl.Float64),
        pl.Series(f"{output_prefix}_lower", lower, dtype=pl.Float64)
    ])

    return result_df

def ROC_expr(column: str | pl.Expr, n: int) -> pl.Expr:
    '''变动率，Rate of Change'''
    col = _expr(column)
    return (col - col.shift(n)) / col.shift(n) * 100

def ROC_df(df: pl.DataFrame, column: str, n: int, output_name: str = "roc") -> pl.DataFrame:
    '''变动率，Rate of Change'''
    return df.with_columns(ROC_expr(column, n).alias(output_name))

def WR_expr(high: str | pl.Expr = "high", low: str | pl.Expr = "low", close: str | pl.Expr = "close", n: int = 14) -> pl.Expr:
    '''威廉指标，Williams %R'''
    high = _expr(high)
    low = _expr(low)
    close = _expr(close)
    hh = high.rolling_max(window_size=n)
    ll = low.rolling_min(window_size=n)
    return (hh - close) / (hh - ll) * -100  # 通常范围 [-100, 0]

def WR_df(
    df: pl.DataFrame,
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
    n: int = 14,
    output_name: str = "wr"
) -> pl.DataFrame:
    '''威廉指标，Williams %R'''
    return df.with_columns(WR_expr(high_col, low_col, close_col, n).alias(output_name))

def BIAS_expr(close: str | pl.Expr, ma_window: int) -> pl.Expr:
    '''乖离率'''
    close = _expr(close)
    ma = close.rolling_mean(window_size=ma_window)
    return (close - ma) / ma * 100

def BIAS_df(
    df: pl.DataFrame,
    close_col: str = "close",
    ma_window: int = 12,
    output_name: str = "bias"
) -> pl.DataFrame:
    '''乖离率'''
    return df.with_columns(BIAS_expr(close_col, ma_window).alias(output_name))

def ENV_expr(
    close: str | pl.Expr = "close",
    window: int = 20,
    percent: float = 2.0,  # 2% 通道
    output_name: str = "env_"
) -> pl.Expr:
    '''价格通道，Envelopes'''
    close = _expr(close)
    ma = close.rolling_mean(window_size=window)
    dev = ma * (percent / 100.0)
    return pl.struct(**{
        f"{output_name}upper": ma + dev,
        f"{output_name}lower": ma - dev,
        f"{output_name}mid": ma
    })

def ENV_df(
    df: pl.DataFrame,
    close_col: str = "close",
    window: int = 20,
    percent: float = 2.0,
    output_name: str = "env_"
) -> pl.DataFrame:
    '''价格通道，Envelopes'''
    return df.with_columns(ENV_expr(close_col, window, percent, output_name).alias("_env")).unnest("_env")

def VOL_MA_expr(volume: str | pl.Expr, window: int) -> pl.Expr:
    '''成交量均线'''
    vol = _expr(volume)
    return vol.rolling_mean(window_size=window)

def VOL_MA_df(
    df: pl.DataFrame,
    volume_col: str = "volume",
    window: int = 5,
    output_name: str = "vol_ma"
) -> pl.DataFrame:
    '''成交量均线'''
    return df.with_columns(VOL_MA_expr(volume_col, window).alias(output_name))

def CMO_expr(close: str | pl.Expr = "close", window: int = 14) -> pl.Expr:
    '''钱德动量摆动指标'''
    price = _expr(close)
    diff = price.diff()
    up = diff.clip(0, None)
    down = (-diff).clip(0, None)
    sum_up = up.rolling_sum(window_size=window)
    sum_down = down.rolling_sum(window_size=window)
    return (sum_up - sum_down) / (sum_up + sum_down) * 100

def CMO_df(
    df: pl.DataFrame,
    close_col: str = "close",
    window: int = 14,
    output_name: str = "cmo"
) -> pl.DataFrame:
    '''钱德动量摆动指标'''
    return df.with_columns(CMO_expr(close_col, window).alias(output_name))

def TRIX_expr(close: str | pl.Expr = "close", window: int = 12) -> pl.Expr:
    '''三重指数平滑平均线'''
    price = _expr(close)
    ema1 = price.ewm_mean(span=window, adjust=False)
    ema2 = ema1.ewm_mean(span=window, adjust=False)
    ema3 = ema2.ewm_mean(span=window, adjust=False)
    trix = (ema3 - ema3.shift(1)) / ema3.shift(1) * 100
    return trix

def TRIX_df(
    df: pl.DataFrame,
    close_col: str = "close",
    window: int = 12,
    output_name: str = "trix"
) -> pl.DataFrame:
    '''三重指数平滑平均线'''
    return df.with_columns(TRIX_expr(close_col, window).alias(output_name))

def VR_expr(close: str | pl.Expr = "close", volume: str | pl.Expr = "volume", window: int = 26) -> pl.Expr:
    '''成交量比率，Volume Ratio'''
    close = _expr(close)
    volume = _expr(volume)
    
    # 比较今日收盘 vs 昨日收盘
    is_up = close > close.shift(1)
    is_down = close < close.shift(1)
    is_equal = close == close.shift(1)
    
    av = pl.when(is_up).then(volume).otherwise(0).rolling_sum(window_size=window)
    bv = pl.when(is_down).then(volume).otherwise(0).rolling_sum(window_size=window)
    cv = pl.when(is_equal).then(volume).otherwise(0).rolling_sum(window_size=window)
    
    # 避免除零
    denominator = pl.when(bv + cv/2 == 0).then(1).otherwise(bv + cv/2)
    vr = (av + cv/2) / denominator * 100
    
    return vr

def VR_df(
    df: pl.DataFrame,
    close_col: str = "close",
    volume_col: str = "volume",
    window: int = 26,
    output_name: str = "vr"
) -> pl.DataFrame:
    '''成交量比率，Volume Ratio'''
    return df.with_columns(VR_expr(close_col, volume_col, window).alias(output_name))

def VWAP_expr(high: str | pl.Expr = "high", low: str | pl.Expr = "low", close: str | pl.Expr = "close", volume: str | pl.Expr = "volume") -> pl.Expr:
    '''Volume Weighted Average Price'''
    high, low, close, volume = map(_expr, [high, low, close, volume])
    typical_price = (high + low + close) / 3.0
    return (typical_price * volume).cumsum() / volume.cumsum()

def VWAP_df(
    df: pl.DataFrame,
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
    volume_col: str = "volume",
    output_name: str = "vwap"
) -> pl.DataFrame:
    '''Volume Weighted Average Price'''
    return df.with_columns(VWAP_expr(high_col, low_col, close_col, volume_col).alias(output_name))

#  若需按日期重置（推荐）：
def VWAP_daily_df(df: pl.DataFrame, date_col: str, **kwargs) -> pl.DataFrame:
    '''Volume Weighted Average Price'''
    return df.with_columns(
        VWAP_expr(**{k: v for k, v in kwargs.items() if k != 'output_name'})
        .over(pl.col(date_col))
        .alias(kwargs.get("output_name", "vwap"))
    )

def MFI_expr(
    high: str | pl.Expr = "high",
    low: str | pl.Expr = "low",
    close: str | pl.Expr = "close",
    volume: str | pl.Expr = "volume",
    window: int = 14
) -> pl.Expr:
    '''Money Flow Index 带成交量的 RSI，范围 [0, 100]'''
    high, low, close, volume = map(_expr, [high, low, close, volume])
    typical_price = (high + low + close) / 3.0
    raw_money_flow = typical_price * volume
    delta = typical_price.diff()
    positive_flow = pl.when(delta > 0).then(raw_money_flow).otherwise(0.0)
    negative_flow = pl.when(delta < 0).then(raw_money_flow).otherwise(0.0)
    pos_sum = positive_flow.rolling_sum(window_size=window)
    neg_sum = negative_flow.rolling_sum(window_size=window)
    mfi = 100.0 - (100.0 / (1.0 + pos_sum / neg_sum))
    return mfi

def MFI_df(
    df: pl.DataFrame,
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
    volume_col: str = "volume",
    window: int = 14,
    output_name: str = "mfi"
) -> pl.DataFrame:
    '''Money Flow Index 带成交量的 RSI，范围 [0, 100]'''
    return df.with_columns(MFI_expr(high_col, low_col, close_col, volume_col, window).alias(output_name))

def STOCH_RSI_expr(
    close: str | pl.Expr = "close",
    rsi_window: int = 14,
    stoch_window: int = 3,
    smooth_k: int = 3,
    smooth_d: int = 3,
    output_name: str = "stoch_rsi_"
) -> pl.Expr:
    '''对 RSI 做随机化处理，增强震荡市信号'''
    close = _expr(close)
    # Step 1: 计算 RSI
    delta = close.diff()
    up = delta.clip(0, None)
    down = (-delta).clip(0, None)
    ema_up = up.ewm_mean(span=rsi_window, adjust=False)
    ema_down = down.ewm_mean(span=rsi_window, adjust=False)
    rs = ema_up / ema_down
    rsi = 100.0 - (100.0 / (1.0 + rs))
    
    # Step 2: 对 RSI 做 Stochastic
    rsi_min = rsi.rolling_min(window_size=stoch_window)
    rsi_max = rsi.rolling_max(window_size=stoch_window)
    stoch_k = pl.when(rsi_max == rsi_min).then(0.0).otherwise((rsi - rsi_min) / (rsi_max - rsi_min) * 100)
    
    # Step 3: 平滑
    stoch_k_smooth = stoch_k.rolling_mean(window_size=smooth_k)
    stoch_d = stoch_k_smooth.rolling_mean(window_size=smooth_d)
    
    return pl.struct(**{
        f"{output_name}k": stoch_k_smooth,
        f"{output_name}d": stoch_d
    })

def STOCH_RSI_df(
    df: pl.DataFrame,
    close_col: str = "close",
    rsi_window: int = 14,
    stoch_window: int = 3,
    smooth_k: int = 3,
    smooth_d: int = 3,
    output_name: str = "stoch_rsi"
) -> pl.DataFrame:
    '''对 RSI 做随机化处理，增强震荡市信号'''
    return df.with_columns(
        STOCH_RSI_expr(close_col, rsi_window, stoch_window, smooth_k, smooth_d, output_name).alias("_stoch_rsi")
    ).unnest("_stoch_rsi")

def SUPERTREND_expr(
    high: str | pl.Expr = "high",
    low: str | pl.Expr = "low",
    close: str | pl.Expr = "close",
    atr_window: int = 10,
    multiplier: float = 3.0,
    output_name: str = ""
) -> pl.Expr:
    '''基于 ATR 的趋势跟踪指标（需先计算 ATR）'''
    high, low, close = map(_expr, [high, low, close])
    
    # 计算 ATR（简化版，不依赖外部）
    hl = high - low
    hc = (high - close.shift(1)).abs()
    lc = (low - close.shift(1)).abs()
    tr = pl.max_horizontal([hl, hc, lc])
    atr = tr.ewm_mean(span=atr_window, adjust=False)
    
    # 基础上下轨
    src = (high + low) / 2.0
    upper_band = src + multiplier * atr
    lower_band = src - multiplier * atr

    # 趋势逻辑（向量化难点：需递归）
    # Polars 无法高效递归 → 使用近似：用前值判断方向（非严格 SuperTrend，但实用）
    prev_close = close.shift(1)
    prev_upper = upper_band.shift(1)
    prev_lower = lower_band.shift(1)

    # 初始方向
    trend = pl.lit(1)  # 1=up, -1=down

    # 简化版：若收盘上穿下轨 → 转多；下穿上轨 → 转空
    is_uptrend = (close > prev_lower) & (prev_close <= prev_lower)
    is_downtrend = (close < prev_upper) & (prev_close >= prev_upper)

    # 实际使用中建议用循环或 Rust UDF 实现完整版
    # 此处返回上下轨和方向信号
    direction = (
        pl.when(is_uptrend).then(1)
        .when(is_downtrend).then(-1)
        .otherwise(None)
        .forward_fill()
        .fill_null(1)
    )

    supertrend = pl.when(direction == 1).then(lower_band).otherwise(upper_band)
    
    return pl.struct(**{
        f"{output_name}supertrend": supertrend,
        f"{output_name}direction": direction
    })

def SUPERTREND_df(
    df: pl.DataFrame,
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
    atr_window: int = 10,
    multiplier: float = 3.0,
    output_name: str = ""
) -> pl.DataFrame:
    '''基于 ATR 的趋势跟踪指标（需先计算 ATR）'''
    return df.with_columns(
        SUPERTREND_expr(high_col, low_col, close_col, atr_window, multiplier, output_name).alias("_st")
    ).unnest("_st")

def ICHIMOKU_expr(
    high: str | pl.Expr = "high",
    low: str | pl.Expr = "low",
    close: str | pl.Expr = "close",
    tenkan_period: int = 9,
    kijun_period: int = 26,
    senkou_span_b_period: int = 52,
    output_name: str = "ichimoku_"
) -> pl.Expr:
    '''一目均衡表 五线系统：转换线、基准线、先行带A/B、迟行线'''
    high, low = map(_expr, [high, low])
    
    tenkan_sen = (high.rolling_max(tenkan_period) + low.rolling_min(tenkan_period)) / 2
    kijun_sen = (high.rolling_max(kijun_period) + low.rolling_min(kijun_period)) / 2
    
    senkou_span_a = (tenkan_sen + kijun_sen) / 2
    senkou_span_b = (high.rolling_max(senkou_span_b_period) + low.rolling_min(senkou_span_b_period)) / 2
    
    chikou_span = _expr(close).shift(-kijun_period)  # 未来偏移（仅用于绘图，策略中慎用）

    return pl.struct(**{
        f"{output_name}tenkan": tenkan_sen,
        f"{output_name}kijun": kijun_sen,
        f"{output_name}senkou_a": senkou_span_a,
        f"{output_name}senkou_b": senkou_span_b,
        f"{output_name}chikou": chikou_span
    })

def ICHIMOKU_df(
    df: pl.DataFrame,
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
    tenkan_period: int = 9,
    kijun_period: int = 26,
    senkou_span_b_period: int = 52,
    output_name: str = "ichimoku_"
) -> pl.DataFrame:
    '''一目均衡表 五线系统：转换线、基准线、先行带A/B、迟行线'''
    return df.with_columns(
        ICHIMOKU_expr(high_col, low_col, close_col, tenkan_period, kijun_period, senkou_span_b_period, output_name)
        .alias("_ichimoku")
    ).unnest("_ichimoku")

def WMA_expr(column: str | pl.Expr, window: int) -> pl.Expr:
    """简单加权移动平均（权重线性递增）"""
    col = _expr(column)
    weights = np.arange(1, window + 1, dtype=np.float64)
    weights = weights / weights.sum()
    # Polars 无 rolling_dot → 用 apply（性能妥协）
    return col.rolling_map(
        function=lambda x: np.dot(x, weights) if len(x) == window else np.nan,
        window_size=window,
        min_periods=window
    )

def HMA_expr(close: str | pl.Expr = "close", window: int = 16) -> pl.Expr:
    '''HMA 平滑且响应快，公式： HMA = WMA(2*WMA(n/2) - WMA(n), sqrt(n))'''
    close = _expr(close)
    half_window = window // 2
    wma_half = WMA_expr(close, half_window)
    wma_full = WMA_expr(close, window)
    raw = 2 * wma_half - wma_full
    hma = WMA_expr(raw, int(np.sqrt(window)))
    return hma

def HMA_df(
    df: pl.DataFrame,
    close_col: str = "close",
    window: int = 16,
    output_name: str = "hma"
) -> pl.DataFrame:
    '''HMA 平滑且响应快，公式： HMA = WMA(2*WMA(n/2) - WMA(n), sqrt(n))'''
    return df.with_columns(HMA_expr(close_col, window).alias(output_name))

def zigzag_with_pivots_and_types(
    high: np.ndarray,
    low: np.ndarray,
    threshold: float,
    mode: str = "percent"
):
    """
    计算 ZigZag，并精确标记每个 pivot 是 'high' 还是 'low'。
    
    Returns:
        tuple:
            - zigzag_prices: np.ndarray (len=N, 转折点处为价格，其余 np.nan)
            - pivot_indices: np.ndarray[int]
            - pivot_prices: np.ndarray[float]
            - pivot_types: np.ndarray[str]  # 'high' or 'low'
    """
    n = len(high)
    if n == 0:
        return (
            np.array([]),
            np.array([], dtype=int),
            np.array([]),
            np.array([], dtype='<U4')
        )
    
    zigzag_prices = np.full(n, np.nan)
    pivot_indices = []
    pivot_prices = []
    pivot_types = []  # 'high' or 'low'
    
    # 初始状态
    last_pivot_price = (high[0] + low[0]) / 2.0
    last_pivot_idx = 0
    trend = 0  # 0=初始, 1=上升中, -1=下降中
    
    for i in range(1, n):
        h, l = high[i], low[i]
        
        if mode == "percent":
            up_move = (h - last_pivot_price) / last_pivot_price
            down_move = (last_pivot_price - l) / last_pivot_price
        else:  # points
            up_move = h - last_pivot_price
            down_move = last_pivot_price - l
        
        # 情况1: 当前处于下降或初始，且出现足够大的上涨 → 确认前一个低点
        if trend <= 0 and up_move >= threshold:
            if trend == -1:  # 前一个是下降趋势 → 刚才的 last_pivot 是一个 **低点**
                zigzag_prices[last_pivot_idx] = last_pivot_price
                pivot_indices.append(last_pivot_idx)
                pivot_prices.append(last_pivot_price)
                pivot_types.append('low')
            # 更新为新的高点候选
            last_pivot_price = h
            last_pivot_idx = i
            trend = 1  # 进入上升趋势
            
        # 情况2: 当前处于上升或初始，且出现足够大的下跌 → 确认前一个高点
        elif trend >= 0 and down_move >= threshold:
            if trend == 1:  # 前一个是上升趋势 → 刚才的 last_pivot 是一个 **高点**
                zigzag_prices[last_pivot_idx] = last_pivot_price
                pivot_indices.append(last_pivot_idx)
                pivot_prices.append(last_pivot_price)
                pivot_types.append('high')
            # 更新为新的低点候选
            last_pivot_price = l
            last_pivot_idx = i
            trend = -1  # 进入下降趋势
    
    # 注意：最后一个 pivot 未被“反向确认”，通常不视为有效转折点（可选）
    
    return (
        zigzag_prices,
        np.array(pivot_indices, dtype=np.int32),
        np.array(pivot_prices, dtype=np.float64),
        np.array(pivot_types, dtype='<U4')  # '<U4' 表示最多4字符的 Unicode 字符串（'high'/'low'）
    )

def ZigZag(
    df: pl.DataFrame,
    high_col: str = "high",
    low_col: str = "low",
    threshold: float = 0.05,
    mode: str = "percent",
    alias: str = "zigzag"
):
    """
    返回：
        - 原始 DataFrame 增加 zigzag 列（非转折点为 null）
        - 转折点子表：包含 datetime、price、type、index
    示例:
    # 计算 ZigZag（3% 阈值）
    df_zz, pivots = ZigZag(df, threshold=0.03, mode="percent")
    print("转折点详情:")
    print(pivots.select(["datetime", "zigzag_price", "pivot_type"]))
    """
    high = df[high_col].to_numpy()
    low = df[low_col].to_numpy()
    
    zz, idxs, prices, types = zigzag_with_pivots_and_types(high, low, threshold, mode)
    
    # 添加 zigzag 列（Polars 中 NaN 会自动转为 null）
    df_with_zz = df.with_columns(pl.Series(alias, zz))
    
    # 构建转折点表
    if len(idxs) > 0:
        pivot_df = (
            df
            .with_row_index("temp_idx")
            .filter(pl.col("temp_idx").is_in(idxs.tolist()))
            .with_columns(
                pl.Series("zigzag_price", prices),
                pl.Series("pivot_type", types),
                pl.col("temp_idx").alias("original_index")
            )
            .drop("temp_idx")
        )
    else:
        pivot_df = pl.DataFrame({
            "zigzag_price": pl.Series([], dtype=pl.Float64),
            "pivot_type": pl.Series([], dtype=pl.Utf8),
            "original_index": pl.Series([], dtype=pl.Int32)
        })
        # 合并原始 schema（除索引外）
        pivot_df = pivot_df.with_columns([
            pl.lit(None).cast(df.schema[col]).alias(col)
            for col in df.columns
        ])
    
    return df_with_zz, pivot_df

