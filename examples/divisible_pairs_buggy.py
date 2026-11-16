"""Deliberate bug: counts each unordered pair twice."""
import json
import sys

case = json.load(sys.stdin)
a, k = case["a"], case["k"]
print(sum((a[i] + a[j]) % k == 0 for i in range(len(a)) for j in range(len(a)) if i != j))
