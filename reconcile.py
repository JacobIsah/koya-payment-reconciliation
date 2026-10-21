#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json
from datetime import datetime


def parse_amount(value):
    if isinstance(value, str):
        value = value.replace(",", "").strip()
    return float(value)


def parse_ts(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))



latest = {}

with open("payments.jsonl", encoding="utf-8") as f:
    for line in f:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue  
        if not isinstance(event, dict) or not event.get("txn_id"):
            continue
        ts = parse_ts(event["ts"])
        prev = latest.get(event["txn_id"])
        if prev is None or ts > prev[0]:
            latest[event["txn_id"]] = (ts, event)

total = 0.0
count = 0

for _, event in latest.values():
    if event["status"] == "success":
        total += parse_amount(event["amount"])
        count += 1

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
