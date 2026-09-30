#!/usr/bin/env python3
"""Enumeration behind the illustrative audit of Appendix J (item (iii) of Open Science).

Seven anchors: one mandatory structural check M, three anchors N1..N3 that pass on the transaction, and three anchors
B1..B3 that block (produce a blocking finding) on the fraudulent transaction. The claimant submits a subset S of the seven
(withholding is free, since the anchors are submitted rather than pulled). Three verdict rules:

  fail-open        V(S) = 1 if M in S and no blocking anchor in S, else 0
  ratio            V(S) = passed(S) / run(S), passed = |S ∩ {M, N1..N3}|, run = |S|   (undefined for S empty)
  full-denominator V(S) = passed(S) / 7

A withholding S (S != all seven) is *profitable* if V(S) is strictly better than the verdict on the complete honest
submission: 1 instead of 0 under fail-open; a ratio above the honest 4/7 under the ratio rule (equivalently, crossing any
financing threshold t with 4/7 < t <= 0.6); no subset exceeds 4/7 under the full denominator.

Reported in the paper: 8 of 128, 63 of 128, 0 of 128. Pure Python; no dependencies.
"""
from itertools import combinations
from fractions import Fraction

ANCHORS = ['M', 'N1', 'N2', 'N3', 'B1', 'B2', 'B3']
PASSING = {'M', 'N1', 'N2', 'N3'}; BLOCKING = {'B1', 'B2', 'B3'}
ALL = frozenset(ANCHORS)

def subsets():
    for k in range(len(ANCHORS) + 1):
        for c in combinations(ANCHORS, k): yield frozenset(c)

def fail_open(S): return 1 if 'M' in S and not (S & BLOCKING) else 0
def ratio(S): return None if not S else Fraction(len(S & PASSING), len(S))
def full_denominator(S): return Fraction(len(S & PASSING), len(ALL))

def count_profitable(rule):
    honest = rule(ALL); n = 0; cheapest = None
    for S in subsets():
        if S == ALL: continue
        v = rule(S)
        if v is not None and v > honest:
            n += 1
            withheld = len(ALL) - len(S)
            if cheapest is None or withheld < cheapest: cheapest = withheld
    return n, cheapest

if __name__ == '__main__':
    total = 2 ** len(ANCHORS)
    for name, rule in (('fail-open (no blocking finding and mandatory check passes)', fail_open),
                       ('ratio of passed to run checks', ratio),
                       ('denominator fixed to the full anchor set', full_denominator)):
        n, cheapest = count_profitable(rule)
        print(f'{name:58s}: {n:3d} of {total} subsets profitable; cheapest profitable deviation withholds '
              f'{cheapest if cheapest is not None else "-"} anchor(s)')
    # threshold reading of the ratio rule: which financing thresholds t reproduce the count
    for t in (Fraction(4, 7), Fraction(58, 100), Fraction(3, 5), Fraction(2, 3)):
        n = sum(1 for S in subsets() if S and S != ALL and ratio(S) >= t and ratio(ALL) < t)
        print(f'  ratio rule with financing threshold t = {float(t):.3f}: {n} subsets reach t while the honest submission does not')
