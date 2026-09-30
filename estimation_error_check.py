#!/usr/bin/env python3
"""Numerical check of the estimation-error bound (eq. 10 and Lemma 1 in the paper; Appendix D) and the curves of Fig. 4.

Covering model with k = 1 and divisible sources. A source universe has true costs kappa_s and verifier estimates
c_hat_s; rho_s = kappa_s / c_hat_s. The verifier commits to p proportional to c_hat; the adversary must own
mass 1 - eps and buys the cheapest mass first (cost per unit mass under policy p is kappa_s / p_s).

  I(eps; p)               = min { kappa(A) : m(A) >= 1 - eps }   (fractional)
  bound checked           : I(eps; p ~ c_hat) / I(eps; p ~ kappa) >= rho_min / rho_bar,
                            rho_bar = c_hat-weighted mean of rho (equivalently K(U)/C_hat(U)).
  The retained fraction equals the c_hat-weighted mean of rho over the cheapest (1-eps) mass divided by rho_bar,
  hence it is bounded BELOW by rho_min/rho_bar, with equality when the cheapest class alone carries mass >= 1-eps.

Pure Python; no dependencies. Fig. 4 data are written as CSV (plot with figures.py if matplotlib is available).
"""
import random, csv, sys

def index_under_policy(kappa, p, eps):
    """Cheapest true cost of owning mass 1-eps when the verifier draws one source per verdict from p."""
    order = sorted(range(len(kappa)), key=lambda s: kappa[s] / p[s])
    need, cost = 1.0 - eps, 0.0
    for s in order:
        take = min(p[s], need)
        cost += take * (kappa[s] / p[s])
        need -= take
        if need <= 1e-15: break
    return cost

def ratio(kappa, c_hat, eps):
    P = sum(c_hat); Q = sum(kappa)
    p_hat = [c / P for c in c_hat]; p_true = [k / Q for k in kappa]
    return index_under_policy(kappa, p_hat, eps) / index_under_policy(kappa, p_true, eps)

def lemma_value(kappa, c_hat, eps):
    """The lemma's exact value: c_hat-weighted mean of rho over the cheapest mass 1-eps, divided by rho_bar."""
    P = sum(c_hat); rho = sorted(((k / c, c / P) for k, c in zip(kappa, c_hat)))
    need, acc = 1.0 - eps, 0.0
    for r, m in rho:
        take = min(m, need); acc += take * r; need -= take
        if need <= 1e-15: break
    return (acc / (1.0 - eps)) / (sum(kappa) / P)

def bound(kappa, c_hat):
    rho = [k / c for k, c in zip(kappa, c_hat)]
    rho_bar = sum(kappa) / sum(c_hat)
    return min(rho) / rho_bar

def random_instance(rng):
    n_classes = rng.randint(2, 5); sources = []
    for _ in range(n_classes):
        rho = 10 ** rng.uniform(-3, 0.5)          # a class-wide estimation error
        for _ in range(rng.randint(1, 6)):
            c = 10 ** rng.uniform(2, 6); sources.append((rho * c, c))
    return [s[0] for s in sources], [s[1] for s in sources]

if __name__ == '__main__':
    rng = random.Random(20260923); violations = 0; trials = 20000
    eq_violations = 0
    for _ in range(trials):
        kappa, c_hat = random_instance(rng); eps = rng.uniform(0.01, 0.6)
        r = ratio(kappa, c_hat, eps)
        if abs(r - lemma_value(kappa, c_hat, eps)) > 1e-9: eq_violations += 1
        if r < bound(kappa, c_hat) - 1e-9: violations += 1
    print(f'random instances: {trials}, violations of the equality retained = rho_bar_(1-eps)/rho_bar: {eq_violations}, '
          f'violations of the corollary retained >= rho_min/rho_bar: {violations}')
    # equality cases: the cheapest class carries at least mass 1-eps
    eq = 0
    for _ in range(2000):
        kappa, c_hat = random_instance(rng); eps = rng.uniform(0.01, 0.6)
        if abs(ratio(kappa, c_hat, eps) - bound(kappa, c_hat)) < 1e-9: eq += 1
    print(f'equality cases among 2000 further instances: {eq}')
    # worked case of Section VI-C: one class over-estimated 100x carrying 80% of estimated cost, eps = 0.2
    kappa, c_hat = [0.8 * 0.01, 0.2], [0.8, 0.2]
    print(f'worked case: retained fraction {ratio(kappa, c_hat, 0.2):.3f}, bound {bound(kappa, c_hat):.3f}')
    # Fig. 4 data: retained fraction against the true rho of the mis-priced class, for its share f of estimated cost
    with open('fig4_data.csv', 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['share_f', 'rho', 'retained_fraction'])
        for f in (0.2, 0.5, 0.8):
            for i in range(0, 61):
                rho = 10 ** (-3 + 3 * i / 60)
                w.writerow([f, rho, ratio([f * rho, 1 - f], [f, 1 - f], 0.2)])
    print('fig4_data.csv written')
