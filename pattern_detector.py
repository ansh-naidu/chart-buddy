import pandas as pd

def detect_head_and_shoulders(df):
    # Simplified logic — placeholder
    recent = df.tail(50)
    confidence = 82  # mock score
    return {"name": "Head & Shoulders", "confidence": confidence, "entry": recent["close"].iloc[-1]}

def detect_double_bottom(df):
    # Simplified logic — placeholder
    recent = df.tail(50)
    confidence = 75
    return {"name": "Double Bottom", "confidence": confidence, "entry": recent["close"].iloc[-1]}

def detect_triangle(df):
    recent = df.tail(50)
    confidence = 78
    return {"name": "Descending Triangle", "confidence": confidence, "entry": recent["close"].iloc[-1]}

def detect_cup_and_handle(df):
    # Your logic...
    return {"name": "Cup and Handle", "confidence": 80, "entry": df['close'].iloc[-1]}

# ✅ Add new patterns here
pattern_functions = [
    detect_head_and_shoulders,
    detect_double_bottom,
    detect_triangle,
    detect_cup_and_handle,
]

def detect_patterns(df):
    results = []
    for func in pattern_functions:
        try:
            result = func(df)
            if result: results.append(result)
        except Exception as e:
            print(f"Pattern function {func.__name__} failed:", e)
    if results:
        return sorted(results, key=lambda x: x["confidence"], reverse=True)[0]
    return None
