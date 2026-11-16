"""Deliberately incorrect formula from the roadmap, with n=0 handled."""
import json
from math import factorial
import sys

n = json.load(sys.stdin)["n"]
print(1 if n == 0 else factorial(n) - factorial(n - 1))
