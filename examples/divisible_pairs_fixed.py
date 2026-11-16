"""O(n) candidate: count matching remainders only among earlier elements."""
import json
import sys

case = json.load(sys.stdin)
counts = {}
answer = 0
for value in case["a"]:
    remainder = value % case["k"]
    answer += counts.get((-remainder) % case["k"], 0)
    counts[remainder] = counts.get(remainder, 0) + 1
print(answer)
