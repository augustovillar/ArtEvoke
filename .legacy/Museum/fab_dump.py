#!/usr/bin/env python
import json
import lzma
import sys
from collections import Counter

def process(json_in, mode="--count"):
    if json_in.endswith(".xz"):
        with lzma.open(json_in, "rt") as f:
            data = json.load(f)
    else:
        with open(json_in, "r") as f:
            data = json.load(f)

    counter = Counter()
    total = 0
    for rec in data:
        creators = rec.get("objectWork", {}).get("creatorDescription", None)
        total += 1
        if isinstance(creators, str):
            counter[creators.strip()] += 1
        elif isinstance(creators, list):
            for c in creators:
                if isinstance(c, str):
                    counter[c.strip()] += 1

    # Define ranges
    buckets = {
        "1": 0,
        "2–5": 0,
        "6–10": 0,
        "11–20": 0,
        "21–50": 0,
        "51–100": 0,
        ">100": 0
    }

    for count in counter.values():
        if count == 1:
            buckets["1"] += 1
        elif 2 <= count <= 5:
            buckets["2–5"] += 1
        elif 6 <= count <= 10:
            buckets["6–10"] += 1
        elif 11 <= count <= 20:
            buckets["11–20"] += 1
        elif 21 <= count <= 50:
            buckets["21–50"] += 1
        elif 51 <= count <= 100:
            buckets["51–100"] += 1
        else:
            buckets[">100"] += 1

    print("Artist count by occurrence range:")
    for label, num_artists in buckets.items():
        print(f"{label}: {num_artists}")

    if mode == "--print":
        total_high_freq = 0
        print("\nArtists with more than 50 entries:")
        for name, count in counter.most_common():
            if count > 50:
                total_high_freq += count
                print(f"{name}: {count}")
        print(f"Total records from artists with >50 entries: {total_high_freq}")

    print(f"\nTotal unique artists: {len(counter)}")
    print(f"Total records processed: {total}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: script.py <input_file> [--print|--count]")
        sys.exit(1)
    input_file = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "--count"
    process(input_file, mode)
