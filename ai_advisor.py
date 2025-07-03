from config import OPENAI_API_KEY
import openai

openai.api_key = OPENAI_API_KEY

tone_templates = {
    "Meme 🤡": "Give a casual, sarcastic, meme-ish take on this pattern. Use emojis. Act like a trading bro on Twitter.",
    "Chad 💪": "Be bold, confident, throw in crypto slang. Keep it intense, call them champ, boss, etc.",
    "Pro 📊": "Write like a calm financial analyst. Clean advice, no emojis, very rational tone."
}

def generate_trade_advice(pattern_info, sl_percent, tp_percent, tone):
    entry = pattern_info['entry']
    sl = round(entry * (1 - sl_percent / 100), 2)
    tp = round(entry * (1 + tp_percent / 100), 2)
    confidence = pattern_info['confidence']
    pattern = pattern_info['name']

    prompt = f"""
You're BTC Buddy, a personal trading assistant.

Pattern Detected: {pattern}
Entry Price: ${entry}
Stop Loss: ${sl}
Take Profit: ${tp}
Confidence: {confidence}%

{tone_templates[tone]}

Now, explain what this pattern suggests, and whether it's worth taking the trade or not. Mention entry, SL, TP again. Add flair based on the tone.
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
