"""Small, independently checkable problems from the project roadmap."""

from itertools import permutations
from random import Random


DESCRIPTIONS = {
    "divisible_pairs": "Count pairs i < j with (a[i] + a[j]) divisible by k. Input: JSON {a: integer array, k: positive integer}. Output: one JSON integer.",
    "derangements": "Count permutations of 0..n-1 with no fixed points. Input: JSON {n: integer}. Output: one JSON integer. D(0) = 1.",
}


def validate(problem: str, case: dict) -> None:
    if not isinstance(case, dict):
        raise ValueError("Case must be a JSON object")
    if problem == "divisible_pairs":
        a, k = case.get("a"), case.get("k")
        if (not isinstance(a, list) or not 0 <= len(a) <= 8
                or any(type(v) is not int or abs(v) > 20 for v in a)
                or type(k) is not int or not 1 <= k <= 10):
            raise ValueError("Oracle domain: 0..8 integers in [-20,20], k in [1,10]")
    elif problem == "derangements":
        if type(case.get("n")) is not int or not 0 <= case["n"] <= 8:
            raise ValueError("Oracle domain: integer n in [0,8]")
    else:
        raise ValueError(f"Unknown problem: {problem}")


def oracle(problem: str, case: dict) -> int:
    validate(problem, case)
    if problem == "divisible_pairs":
        a, k = case["a"], case["k"]
        return sum((a[i] + a[j]) % k == 0
                   for i in range(len(a)) for j in range(i + 1, len(a)))
    n = case["n"]
    return sum(all(i != value for i, value in enumerate(p))
               for p in permutations(range(n)))


def generate_cases(problem: str, seed: int = 42, random_cases: int = 50) -> list[dict]:
    if type(random_cases) is not int or random_cases < 0:
        raise ValueError("random_cases must be a nonnegative integer")
    rng = Random(seed)
    if problem == "divisible_pairs":
        cases = [{"a": [], "k": 1}, {"a": [0], "k": 1},
                 {"a": [1, 2], "k": 3}, {"a": [0, 0, 0], "k": 2},
                 {"a": [-2, 2, 4, -4], "k": 2}, {"a": [2, 2, 2, 2], "k": 4}]
        cases += [{"a": [rng.randint(-20, 20) for _ in range(rng.randint(0, 8))],
                   "k": rng.randint(1, 10)} for _ in range(random_cases)]
        return cases
    if problem == "derangements":
        # Exhaustive small domain: repeats would add no coverage.
        return [{"n": n} for n in range(9)]
    raise ValueError(f"Unknown problem: {problem}")
