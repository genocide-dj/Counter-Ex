"""Recurrence D(n) = (n-1) * (D(n-1) + D(n-2))."""
import json
import sys

n = json.load(sys.stdin)["n"]
previous, current = 1, 0
for i in range(2, n + 1):
    previous, current = current, (i - 1) * (current + previous)
print(previous if n == 0 else current)
