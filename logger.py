import csv
import os
from datetime import datetime

LOG_FILE = "trade_log.csv"

def log_trade(pattern_info, sl, tp):
    entry = pattern_info['entry']
    confidence = pattern_info['confidence']
    name = pattern_info['name']
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    headers = ["Time", "Pattern", "Confidence", "Entry", "SL", "TP"]
    row = [now, name, confidence, entry, sl, tp]

    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow(row)
