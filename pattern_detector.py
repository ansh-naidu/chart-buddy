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

pattern_functions = [
    detect_head_and_shoulders,
    detect_double_bottom,
    detect_ascending_triangle,
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
