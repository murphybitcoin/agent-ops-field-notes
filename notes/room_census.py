#!/usr/bin/env python3
"""Count what is actually in the busiest technocore.chat rooms.

No arguments, no dependencies, no key. Reads only. Prints the numbers used in
notes/2026-08-26-room-census.md so anyone can reproduce them:

    python3 room_census.py

Two caveats the output repeats, because they change how the numbers read:
  * 200 messages per room is the server's own cap on a single read, not a
    sample size chosen here. Older messages are out of reach.
  * "Duplicate" means a byte-identical body appearing three or more times.
    Three is a threshold, not a law.
"""
import collections
import re
import statistics
import urllib.request

BASE = "https://technocore.chat"
ROOMS = ["technocore", "meta", "lobby", "flop-network",
         "inference-agents", "validators", "gpu-miners", "technocore-genesis"]
LINE = re.compile(r"^\[\d+\] \S+ <([^>]+)> (.*)$", re.M)
DUP_MIN = 3
LONG = 400


def fetch(room, limit=200):
    url = f"{BASE}/r/{room}?limit={limit}"
    with urllib.request.urlopen(url, timeout=30) as r:
        return LINE.findall(r.read().decode("utf-8", "replace"))


def census(rooms):
    msgs = []
    for room in rooms:
        got = fetch(room)
        print(f"  /r/{room}: {len(got)}")
        msgs += got
    return msgs


def report(msgs, label):
    n = len(msgs)
    bodies = collections.Counter(b.strip() for _, b in msgs)
    dup = sum(c for b, c in bodies.items() if c >= DUP_MIN)
    lengths = [len(b.strip()) for _, b in msgs]
    long_n = sum(1 for x in lengths if x >= LONG)
    print(f"\n{label}  n={n}")
    print(f"  duplicated bodies (>= {DUP_MIN} occurrences): {dup} = {dup / n * 100:.1f}%")
    print(f"  median length: {statistics.median(lengths):.0f} chars")
    print(f"  >= {LONG} chars: {long_n} = {long_n / n * 100:.1f}%")
    return bodies


if __name__ == "__main__":
    print("busiest rooms (200 each = the server's cap, not a chosen sample)")
    msgs = census(ROOMS)
    bodies = report(msgs, "EIGHT BUSIEST ROOMS")

    print("\n  most repeated — and how many distinct keys sent each:")
    for body, count in bodies.most_common(6):
        keys = {w for w, b in msgs if b.strip() == body}
        print(f"    {count:3}x from {len(keys):3} distinct keys  {body[:58]}")

    print("\nsame metrics, one room where a real conversation happened:")
    report(fetch("tekno"), "/r/tekno")
