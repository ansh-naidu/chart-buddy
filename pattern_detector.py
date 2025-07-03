import numpy as np
import pandas as pd
import ta

def detect_head_and_shoulders(df):
    close = df['close']
    window = 5
    maxima = (close.shift(1) < close) & (close.shift(-1) < close)
    peaks = close[maxima]
    if len(peaks) < 3:
        return None
    last_three_peaks = peaks.tail(3)
    if len(last_three_peaks) < 3:
        return None

    left_shoulder_price, head_price, right_shoulder_price = last_three_peaks.values
    left_shoulder_idx, head_idx, right_shoulder_idx = last_three_peaks.index

    # Require reasonable time gap (6h min between peaks)
    if (right_shoulder_idx - head_idx).total_seconds() < 6*3600 or (head_idx - left_shoulder_idx).total_seconds() < 6*3600:
        return None

    # Conditions
    is_head_highest = head_price > left_shoulder_price and head_price > right_shoulder_price
    shoulders_similar = abs(left_shoulder_price - right_shoulder_price) / head_price < 0.15

    # RSI check
    rsi = ta.momentum.rsi(close, window=14).iloc[-1]
    if rsi > 60:
        return None

    confidence = 80 + 10 * (1 - abs(left_shoulder_price - right_shoulder_price) / head_price)
    if confidence < 85:
        return None

    neckline = min(left_shoulder_price, right_shoulder_price)
    entry = neckline

    # Price breakout confirmation
    if close.iloc[-1] < entry * 1.005:
        return None

    return {
        "name": "Head & Shoulders",
        "confidence": round(confidence, 2),
        "entry": entry,
        "key_points": {
            "Left Shoulder": (left_shoulder_idx, left_shoulder_price),
            "Head": (head_idx, head_price),
            "Right Shoulder": (right_shoulder_idx, right_shoulder_price),
            "Neckline": entry
        }
    }

def detect_double_bottom(df):
    close = df['close']
    minima = (close.shift(1) > close) & (close.shift(-1) > close)
    lows = close[minima]

    if len(lows) < 2:
        return None

    first_low_price, second_low_price = lows.tail(2).values
    first_low_idx, second_low_idx = lows.tail(2).index

    # Time gap at least 6h
    if (second_low_idx - first_low_idx).total_seconds() < 6*3600:
        return None

    peak_between = close.loc[first_low_idx:second_low_idx].max()

    lows_close = abs(first_low_price - second_low_price) / max(first_low_price, second_low_price) < 0.05
    if not lows_close or peak_between <= first_low_price:
        return None

    rsi_series = ta.momentum.rsi(close, window=14)
    if rsi_series.loc[second_low_idx] > 40:
        return None

    confidence = 75 + 15 * (1 - abs(first_low_price - second_low_price) / max(first_low_price, second_low_price))
    if confidence < 80:
        return None

    entry = peak_between

    if close.iloc[-1] < entry * 1.005:
        return None

    return {
        "name": "Double Bottom",
        "confidence": round(confidence, 2),
        "entry": entry,
        "key_points": {
            "First Low": (first_low_idx, first_low_price),
            "Second Low": (second_low_idx, second_low_price),
            "Resistance": (close.loc[first_low_idx:second_low_idx].idxmax(), peak_between),
            "Entry": (close.index[-1], close.iloc[-1])
        }
    }

def detect_ascending_triangle(df):
    highs = df['high']
    lows = df['low']

    window = 20
    recent_highs = highs.tail(window)
    recent_lows = lows.tail(window)

    resistance = recent_highs.max()
    resistance_idx = recent_highs.idxmax()
    support_slope = np.polyfit(range(window), recent_lows.values, 1)[0]

    resistance_flat = recent_highs.std() / resistance < 0.01
    support_rising = support_slope > 0

    macd = ta.trend.macd_diff(df['close']).iloc[-1]
    if macd < 0:
        return None

    if not (resistance_flat and support_rising):
        return None

    confidence = 70 + 20 * (1 - recent_highs.std() / resistance)
    if confidence < 80:
        return None

    entry = resistance

    if df['close'].iloc[-1] < entry * 1.005:
        return None

    # Support line points (first and last lows)
    support_start_idx = recent_lows.index[0]
    support_end_idx = recent_lows.index[-1]
    support_start_price = recent_lows.iloc[0]
    support_end_price = recent_lows.iloc[-1]

    return {
        "name": "Ascending Triangle",
        "confidence": round(confidence, 2),
        "entry": entry,
        "key_points": {
            "Resistance": (resistance_idx, resistance),
            "Support Start": (support_start_idx, support_start_price),
            "Support End": (support_end_idx, support_end_price),
            "Entry": (df.index[-1], df['close'].iloc[-1])
        }
    }

def detect_triple_top(df):
    highs = df['high']
    maxima = (highs.shift(1) < highs) & (highs.shift(-1) < highs)
    peaks = highs[maxima]

    if len(peaks) < 3:
        return None

    last_three_peaks = peaks.tail(3)
    if len(last_three_peaks) < 3:
        return None

    p1, p2, p3 = last_three_peaks.values
    i1, i2, i3 = last_three_peaks.index

    # Peaks roughly equal within 1.5%
    if max(p1, p2, p3) - min(p1, p2, p3) > 0.015 * max(p1, p2, p3):
        return None

    # Time gap check (6h minimum between peaks)
    if (i2 - i1).total_seconds() < 6*3600 or (i3 - i2).total_seconds() < 6*3600:
        return None

    resistance = max(p1, p2, p3)
    entry = resistance

    confidence = 75 + 10 * (1 - ((max(p1,p2,p3) - min(p1,p2,p3)) / resistance))

    # Confirm breakout above resistance
    if df['close'].iloc[-1] < entry * 1.005:
        return None

    return {
        "name": "Triple Top",
        "confidence": round(confidence, 2),
        "entry": entry,
        "key_points": {
            "Peak 1": (i1, p1),
            "Peak 2": (i2, p2),
            "Peak 3": (i3, p3),
        }
    }

def detect_bullish_flag(df):
    close = df['close']
    window = 20

    if len(close) < window * 2:
        return None

    # Flagpole: sharp rise in first half of window
    flagpole = close[-window*2:-window]
    flag = close[-window:]

    rise_pct = (flagpole.iloc[-1] - flagpole.iloc[0]) / flagpole.iloc[0]

    if rise_pct < 0.05:  # require at least 5% rise
        return None

    # Flag: small consolidation, price mostly sideways or slight downward slope
    flag_range = flag.max() - flag.min()
    if flag_range / flag.min() > 0.03:  # max 3% price range in flag
        return None

    slope = np.polyfit(range(window), flag.values, 1)[0]
    if slope > 0.001:  # slight downward or flat slope only
        return None

    entry = flag.max()

    confidence = 80 + 10 * (rise_pct / 0.1)  # confidence scales with rise_pct

    # Confirm breakout above flag high
    if df['close'].iloc[-1] < entry * 1.005:
        return None

    return {
        "name": "Bullish Flag",
        "confidence": round(min(confidence, 95), 2),
        "entry": entry,
        "key_points": {
            "Flagpole Start": (flagpole.index[0], flagpole.iloc[0]),
            "Flagpole End": (flagpole.index[-1], flagpole.iloc[-1]),
            "Flag High": (flag.index[flag.argmax()], entry),
        }
    }

def detect_cup_and_handle(df):
    close = df['close']
    window = 50  # analyze last 50 candles

    if len(close) < window:
        return None

    data = close.tail(window)

    # Smooth data (rolling mean) to identify cup shape
    smooth = data.rolling(window=5).mean()

    cup_min_idx = smooth.idxmin()
    cup_min_val = smooth.min()

    left_max = smooth[:cup_min_idx]
    right_max = smooth[cup_min_idx:]

    if len(left_max) < 5 or len(right_max) < 5:
        return None

    left_max_val = left_max.max()
    right_max_val = right_max.max()

    # Cup shape: left and right max roughly equal and significantly above min
    if abs(left_max_val - right_max_val) / max(left_max_val, right_max_val) > 0.05:
        return None

    if (left_max_val - cup_min_val) / cup_min_val < 0.05:
        return None

    # Handle: small consolidation/pullback after cup right max
    handle_start_idx = right_max.idxmax()
    handle = data[handle_start_idx:]

    if len(handle) < 5:
        return None

    handle_range = handle.max() - handle.min()
    if handle_range / handle.min() > 0.03:
        return None

    entry = right_max_val

    confidence = 75 + 15 * (1 - handle_range / handle.min())

    # Confirm breakout above entry
    if df['close'].iloc[-1] < entry * 1.005:
        return None

    return {
        "name": "Cup and Handle",
        "confidence": round(confidence, 2),
        "entry": entry,
        "key_points": {
            "Cup Left Max": (left_max.idxmax(), left_max_val),
            "Cup Bottom": (cup_min_idx, cup_min_val),
            "Cup Right Max": (right_max.idxmax(), right_max_val),
            "Handle End": (handle.index[-1], handle.iloc[-1])
        }
    }

def detect_rising_wedge(df):
    highs = df['high']
    lows = df['low']
    window = 30

    if len(df) < window:
        return None

    recent_highs = highs.tail(window)
    recent_lows = lows.tail(window)

    # Fit lines to highs and lows
    high_slope = np.polyfit(range(window), recent_highs.values, 1)[0]
    low_slope = np.polyfit(range(window), recent_lows.values, 1)[0]

    # Check if both slopes positive (rising wedge)
    if high_slope <= 0 or low_slope <= 0:
        return None

    # Check if lines are converging: distance between highs and lows decreases
    distance_start = recent_highs.iloc[0] - recent_lows.iloc[0]
    distance_end = recent_highs.iloc[-1] - recent_lows.iloc[-1]

    if distance_end >= distance_start:
        return None

    # Entry point: breakout below lower trendline
    entry = recent_lows.min()

    confidence = 75 + 15 * (distance_start - distance_end) / distance_start

    # Confirm price currently below lower trendline? (Bearish breakout)
    if df['close'].iloc[-1] > entry * 1.005:
        return None

    return {
        "name": "Rising Wedge",
        "confidence": round(confidence, 2),
        "entry": entry,
        "key_points": {
            "High Start": (recent_highs.index[0], recent_highs.iloc[0]),
            "High End": (recent_highs.index[-1], recent_highs.iloc[-1]),
            "Low Start": (recent_lows.index[0], recent_lows.iloc[0]),
            "Low End": (recent_lows.index[-1], recent_lows.iloc[-1]),
        }
    }

def detect_symmetrical_triangle(df):
    highs = df['high']
    lows = df['low']
    window = 30

    if len(df) < window:
        return None

    recent_highs = highs.tail(window)
    recent_lows = lows.tail(window)

    # Slopes
    high_slope = np.polyfit(range(window), recent_highs.values, 1)[0]
    low_slope = np.polyfit(range(window), recent_lows.values, 1)[0]

    # Check high slope negative, low slope positive (triangle converging)
    if not (high_slope < 0 and low_slope > 0):
        return None

    # Distance between lines decreasing
    dist_start = recent_highs.iloc[0] - recent_lows.iloc[0]
    dist_end = recent_highs.iloc[-1] - recent_lows.iloc[-1]

    if dist_end >= dist_start:
        return None

    # Entry: breakout above high or below low (detect recent close)
    entry_high = recent_highs.max()
    entry_low = recent_lows.min()
    last_close = df['close'].iloc[-1]

    confidence = 75 + 15 * (dist_start - dist_end) / dist_start

    if last_close > entry_high * 1.005:
        entry = entry_high
        breakout_dir = "bullish"
    elif last_close < entry_low * 0.995:
        entry = entry_low
        breakout_dir = "bearish"
    else:
        return None

    return {
        "name": "Symmetrical Triangle",
        "confidence": round(confidence, 2),
        "entry": entry,
        "breakout": breakout_dir,
        "key_points": {
            "High Start": (recent_highs.index[0], recent_highs.iloc[0]),
            "High End": (recent_highs.index[-1], recent_highs.iloc[-1]),
            "Low Start": (recent_lows.index[0], recent_lows.iloc[0]),
            "Low End": (recent_lows.index[-1], recent_lows.iloc[-1]),
        }
    }


pattern_functions = [
    detect_head_and_shoulders,
    detect_double_bottom,
    detect_ascending_triangle,
    detect_cup_and_handle,
    detect_rising_wedge,
    detect_symmetrical_triangle,
    detect_bullish_flag,
    detect_triple_top,
]

def detect_patterns(df):
    results = []
    for func in pattern_functions:
        try:
            result = func(df)
            if result:
                results.append(result)
        except Exception as e:
            print(f"Error in {func.__name__}: {e}")

    if results:
        return sorted(results, key=lambda x: x["confidence"], reverse=True)[0]
    return None
