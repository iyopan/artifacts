#!/usr/bin/env python3
"""Figures 1-4 of the paper, generated from the formulas in the text (matplotlib).
Writes vector PDFs (used by the LaTeX source, fig/) and PNG previews (figures/).
Fig. 4 reads fig4_data.csv produced by estimation_error_check.py.
Parameters of the illustrative curves are stated inline."""
import math, csv, os, sys
from statistics import NormalDist
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
Phi, Phi_inv = NormalDist().cdf, NormalDist().inv_cdf
here = os.path.dirname(os.path.abspath(__file__))
out_png = os.path.join(here, '..', 'figures'); os.makedirs(out_png, exist_ok=True)
out_pdf = sys.argv[1] if len(sys.argv) > 1 else out_png
plt.rcParams.update({'font.size': 7, 'axes.labelsize': 7.5, 'legend.fontsize': 6.5, 'xtick.labelsize': 6.5, 'ytick.labelsize': 6.5,
                     'axes.spines.top': False, 'axes.spines.right': False, 'pdf.fonttype': 42})
W, H = 3.45, 2.55  # inches: one IEEE column
def save(fig, name):
    fig.tight_layout(pad=0.4)
    fig.savefig(os.path.join(out_pdf, name + '.pdf')); fig.savefig(os.path.join(out_png, name + '.png'), dpi=220); plt.close(fig)

# ---------------- Fig. 1: the error floor alpha + beta >= 1 - delta(b) ----------------
fig, ax = plt.subplots(figsize=(W, H))
xs = [i / 400 for i in range(401)]
ax.fill_between(xs, 0, [1 - x for x in xs], color='#f4b183', alpha=0.35, lw=0)
ax.plot(xs, [1 - x for x in xs], color='#d1495b', lw=1.6)
ax.plot(xs, [max(0, 0.5 - x) for x in xs], color='#2a6fdb', lw=1.2, ls='--')
ax.plot(xs, [max(0, 0.1 - x) for x in xs], color='#2a9d8f', lw=1.2, ls=':')
ax.text(0.62, 0.42, r'$\delta=0$', color='#d1495b'); ax.text(0.30, 0.235, r'$\delta=0.5$', color='#2a6fdb'); ax.text(0.03, 0.115, r'$\delta=0.9$', color='#2a9d8f')
ax.annotate('', xy=(0.42, 0.62), xytext=(0.22, 0.32), arrowprops=dict(arrowstyle='->', color='0.35', lw=1))
ax.text(0.50, 0.90, 'Shaded: ' + r'$\alpha+\beta<1-\delta(b)$' + '.\nUnreachable by every rule ' + r'$\psi$' + ',\nincluding a computationally\nunbounded one.', fontsize=6.2, color='#8c2f39', va='top')
ax.text(0.47, 0.47, 'As ' + r'$b$' + ' grows, ' + r'$\delta(b)$' + ' falls and the\nfloor sweeps outward (arrow),\nuntil at ' + r'$\delta=0$' + ' it swallows the\nwhole useful region.', fontsize=6.2, color='#8c2f39', va='top')
ax.set_xlabel(r'$\alpha$ — false-accept probability'); ax.set_ylabel(r'$\beta$ — false-reject probability')
ax.set_xlim(0, 1); ax.set_ylim(0, 1.02); save(fig, 'fig1_error_floor')

# ---------------- Fig. 2: the admission policy's ROC ----------------
fig, ax = plt.subplots(figsize=(W, H))
xs = [i / 500 for i in range(1, 500)]
curves = {2.60: '#2a6fdb', 1.45: '#4f8fe6', 0.80: '#2a9d8f', 0.28: '#57b894'}
for Delta, col in curves.items():
    ys = [Phi(Phi_inv(x) + Delta) for x in xs]; ax.plot(xs, ys, color=col, lw=1.3)
    xi = 0.12 if Delta > 1 else (0.30 if Delta > 0.5 else 0.55); ax.text(xi, Phi(Phi_inv(xi) + Delta) + 0.02, rf'$\Delta={Delta:.2f}$', color=col, fontsize=6.3)
low = [Phi(Phi_inv(x) + 0.28) for x in xs]
ax.fill_between(xs, xs, low, color='#57b894', alpha=0.25, lw=0)
ax.plot([0, 1], [0, 1], color='0.3', lw=0.9)
ax.annotate('', xy=(0.80, 0.80), xytext=(0.80, Phi(Phi_inv(0.80) + 0.28)), arrowprops=dict(arrowstyle='->', color='#d1495b', lw=1))
ax.text(0.33, 0.30, r'$\Delta\to0$' + ': ROC collapses to the diagonal.\n' + r'$\Pr[\mathrm{admit}\mid\mathrm{genuine}]=\Pr[\mathrm{admit}\mid\mathrm{acquired}]$' + '.\nOpenness to new evidence IS leakage.', fontsize=6.0, color='#d1495b', va='top')
ax.text(0.36, 0.04, 'adversary spends on mimicry ' + r'$\rightarrow$', fontsize=6.0, color='0.35')
ax.set_xlabel('leakage  ' + r'$\Pr[\mathrm{admit}\mid\mathrm{acquired}]$'); ax.set_ylabel('openness  ' + r'$\Pr[\mathrm{admit}\mid\mathrm{genuine}]$')
ax.set_xlim(0, 1); ax.set_ylim(0, 1.02); save(fig, 'fig2_admission_roc')

# ---------------- Fig. 3: purchasable indistinguishability by route ----------------
# Illustrative routes: delta_j(b) = sqrt(max(0, 1 - (b/I_j)^2)) with acquisition index I_A(0) = 4 and corruption index I_C(0) = 7.
IA, IC = 4.0, 7.0
def dA(b): return math.sqrt(max(0.0, 1 - (b / IA) ** 2))
def dC(b): return math.sqrt(max(0.0, 1 - (b / IC) ** 2))
bs = [i / 100 for i in range(0, 901)]
mins = [min(dA(b), dC(b)) for b in bs]
env = [max(0.0, 1 - b / IA) for b in bs]   # lower convex envelope of a concave decreasing curve: the chord
fig, ax = plt.subplots(figsize=(W, H))
ax.fill_between(bs, env, mins, color='#57b894', alpha=0.25, lw=0)
ax.plot(bs, [dC(b) for b in bs], color='#2a6fdb', lw=1.6)
ax.plot(bs, mins, color='#e76f51', lw=1.6)
ax.plot(bs, env, color='#1b7f5c', lw=1.8)
for x, col in ((IA, '#e76f51'), (IC, '#2a6fdb')): ax.axvline(x, color=col, lw=0.9, ls=':')
ax.text(4.3, 0.90, 'route A: acquire a source\n= the pointwise min over routes', color='#e76f51', fontsize=6.2, va='top')
ax.text(5.1, 0.64, 'route C: corrupt\nexisting channels', color='#2a6fdb', fontsize=6.2, va='top')
ax.text(1.35, 0.66, 'gap opened by\namortization alone', color='#1b7f5c', fontsize=6.0, ha='center', va='top')
ax.text(0.15, 0.20, 'convex envelope — the amortized adversary\n' + r'$\delta(b)\leq\mathrm{conv}\,\min_j\delta_j(b)$', color='#1b7f5c', fontsize=6.0, va='top')
ax.text(IA, -0.13, r'$I(0)=4$' + '\nacquisition index', color='#e76f51', fontsize=6.0, ha='center', va='top', transform=ax.get_xaxis_transform())
ax.text(IC, -0.13, r'$I_C(0)=7$' + '\ncorruption index', color='#2a6fdb', fontsize=6.0, ha='center', va='top', transform=ax.get_xaxis_transform())
ax.set_xlabel('adversary budget  ' + r'$b$', labelpad=24); ax.set_ylabel(r'$\delta(b)=\inf_{\mathrm{cost}(A)\leq b}\,\mathrm{TV}(P_1,P_2^{(A)})$')
ax.set_xlim(0, 9); ax.set_ylim(0, 1.02); fig.subplots_adjust(bottom=0.34, left=0.13, right=0.98, top=0.97); fig.savefig(os.path.join(out_pdf, 'fig3_by_route.pdf')); fig.savefig(os.path.join(out_png, 'fig3_by_route.png'), dpi=220); plt.close(fig)

# ---------------- Fig. 4: robustness of the admission policy to mis-estimated costs ----------------
data = {}
with open(os.path.join(here, 'fig4_data.csv')) as fh:
    for row in csv.DictReader(fh): data.setdefault(float(row['share_f']), []).append((float(row['rho']), float(row['retained_fraction'])))
fig, ax = plt.subplots(figsize=(W, H))
ax.axhline(1.0, color='0.4', lw=0.8, ls=':'); ax.text(0.12, 1.012, 'no loss: ' + r'$\hat\rho=\rho$', fontsize=6.0, color='0.35')
for f, col in ((0.2, '#2a6fdb'), (0.5, '#e76f51'), (0.8, '#1b9e77')):
    pts = sorted(data[f]); ax.semilogx([p[0] for p in pts], [p[1] for p in pts], color=col, lw=1.6)
    ax.text(0.0012, pts[0][1] + 0.025, f'$f={f}$', color=col, fontsize=6.3)
ax.set_xlabel('true ' + r'$\rho$' + ' of the mis-priced source class   (verifier believes ' + r'$\hat\rho=1$' + r'; $\varepsilon=0.2$)', fontsize=6.6)
ax.set_ylabel(r'$I(\varepsilon;p\propto\hat c)\,/\,I(\varepsilon;p\propto\kappa)$'); ax.set_ylim(0, 1.06); ax.set_xlim(1e-3, 1)
save(fig, 'fig4_estimation_error')
print('figures written:', out_pdf, 'and', out_png)
