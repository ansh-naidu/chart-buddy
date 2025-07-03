from config import OPENAI_API_KEY
import openai

openai.api_key = OPENAI_API_KEY

use_openai = OPENAI_API_KEY and not OPENAI_API_KEY.startswith("sk-...")

tone_templates = {
    "Meme 🤡": "You spotted {pattern}! Could be fire or flop. SL at ${sl}, TP at ${tp}. Your call, degenerate. 🤡",
    "Chad 💪": "{pattern} pattern detected. You either ride or hide. Entry ${entry}, SL ${sl}, TP ${tp}. Don't be weak. 💪",
    "Pro 📊": "Pattern: {pattern}. Suggested entry at ${entry}, SL at ${sl}, TP at ${tp}. Confidence is {confidence}%. Trade wisely."
}

def generate_trade_advice(pattern_info, sl_percent, tp_percent, tone):
    entry = pattern_info['entry']
    sl = round(entry * (1 - sl_percent / 100), 2)
    tp = round(entry * (1 + tp_percent / 100), 2)
    confidence = pattern_info['confidence']
    pattern = pattern_info['name']

    if not use_openai:
        return tone_templates[tone].format(pattern=pattern, entry=entry, sl=sl, tp=tp, confidence=confidence)

    prompt = f"""
You're BTC Buddy, a trading pal.

Pattern Detected: {pattern}
Entry Price: ${entry}
Stop Loss: ${sl}
Take Profit: ${tp}
Confidence: {confidence}%

{tone_templates[tone]}

Now give trading advice in this tone.
"""
    try:
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.8
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ OpenAI Error: {e}"
