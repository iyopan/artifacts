#!/usr/bin/env python3
"""Seasoning price T* (eq. 3), the regime boundary N* (eq. 4) and the table of Appendix E.

T*(N) = (1/r) * ln( (N*eps*c_hat + c_maint/r) / (c_reg + c_maint/r) )
N*    ~  c_maint / (r * eps * c_hat)

Illustrative parameters as in Appendix E: c_reg = 200, r = 0.10, c_hat = 100_000, eps = 0.2.
Pure Python; no dependencies.
"""
import math

def T_star(N, c_reg=200.0, r=0.10, c_hat=100_000.0, eps=0.2, c_maint=400.0):
    return (1.0 / r) * math.log((N * eps * c_hat + c_maint / r) / (c_reg + c_maint / r))

def N_star(c_maint, r=0.10, c_hat=100_000.0, eps=0.2):
    return c_maint / (r * eps * c_hat)

if __name__ == '__main__':
    grid = [(400.0, 'existence: age of registration'),
            (5_000.0, 'light activity: filings, a bank account'),
            (50_000.0, 'operations: real counterparties, real money moved')]
    Ns = [1, 10, 100]
    print(f"{'c_maint/yr':>12} " + ' '.join(f'{"N="+str(N):>8}' for N in Ns) + '   N*      what the verifier counts as history')
    for c_maint, label in grid:
        vals = [T_star(N, c_maint=c_maint) for N in Ns]
        print(f'{c_maint:>12,.0f} ' + ' '.join(f'{v:8.2f}' for v in vals) + f'  {N_star(c_maint):6.2f}   {label}')
    # regime readings quoted in Appendix E
    t = {c: [T_star(N, c_maint=c) for N in Ns] for c, _ in grid}
    print()
    print(f'hundredfold increase in N costs the adversary {t[400.0][2]/t[400.0][0]:.1f}x seasoning under registration age, '
          f'{t[50_000.0][2]/t[50_000.0][0]:.0f}x under operational trace')
    print(f'operational edge over registration: {t[400.0][0]/t[50_000.0][0]:.0f}x at N=1, {t[400.0][2]/t[50_000.0][2]:.1f}x at N=100')
