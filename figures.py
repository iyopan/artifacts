#!/usr/bin/env python3
"""Figures 1-4 of the paper, generated from the formulas in the text (matplotlib 3.6 or later).

    python3 figures.py [output dir]      (default: figures/ next to this script)

Each figure is written as a vector PDF (the version used in the paper) and as a PNG preview at 300 dpi.
Fig. 4 reads fig4_data.csv, which estimation_error_check.py writes.
Direct labels sit exactly GAP points from the line they name. Before saving, every label is checked for
clearance from every line, arrow, marker, axis and other label; the script stops if any clearance is
below MIN_GAP_PT."""
import csv, math, os, sys
from statistics import NormalDist
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.legend import Legend

here = os.path.dirname(os.path.abspath(__file__))
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, 'figures')
os.makedirs(out, exist_ok=True)

# ---------------------------------------------------------------- style -------------------------------------------
# One IEEE column (3.5 in); the height keeps the printed size of the figures in the paper unchanged.
FIG_W, FIG_H = 3.5, 2.55 * 3.5 / 3.45
MARGIN = dict(left=0.52, right=0.12, bottom=0.44, top=0.06)        # inches, identical for all four figures
AX_W_PT = (FIG_W - MARGIN['left'] - MARGIN['right']) * 72
AX_H_PT = (FIG_H - MARGIN['bottom'] - MARGIN['top']) * 72
YMAX = 1.1                                                          # same vertical scale in all four figures
INK, INK2, TICK, AXIS = '#1f1e1c', '#52514e', '#3d3c39', '#8a8882'  # text, secondary text, tick labels, axes
ORANGE = ['#ff9265', '#e05e29', '#ae3100']                          # ordinal ramp, light to dark (validated)
BLUE = ['#86b6ef', '#5598e7', '#256abf', '#104281']                 # ordinal ramp, light to dark (validated)
CAT = {'blue': '#2a78d6', 'orange': '#eb6834', 'aqua': '#1baf7a'}   # categorical slots 1-3 (validated all pairs)
LW, LW_REF, LW_ARROW = 1.5, 0.9, 0.8                                # series, reference lines, arrows (pt)
FS, FS_AXIS = 8, 8.5                                                # labels and ticks; axis titles (pt)
GAP = 4.0                                                           # label to its line, and label to the plot edge (pt)
MIN_GAP_PT = 2.0                                                    # hard floor enforced by the check

plt.rcParams.update({
    'font.family': 'STIXGeneral', 'mathtext.fontset': 'stix', 'font.size': FS,
    'axes.labelsize': FS_AXIS, 'axes.labelcolor': INK, 'axes.labelpad': 3.0,
    'axes.edgecolor': AXIS, 'axes.linewidth': 0.6, 'axes.spines.top': False, 'axes.spines.right': False,
    'xtick.labelsize': FS, 'ytick.labelsize': FS, 'xtick.color': AXIS, 'ytick.color': AXIS,
    'xtick.labelcolor': TICK, 'ytick.labelcolor': TICK, 'xtick.major.size': 2.5, 'ytick.major.size': 2.5,
    'xtick.major.width': 0.6, 'ytick.major.width': 0.6, 'xtick.major.pad': 2.5, 'ytick.major.pad': 2.5,
    'xtick.minor.size': 1.5, 'xtick.minor.width': 0.5,
    'lines.solid_capstyle': 'round', 'lines.dash_capstyle': 'butt',
    'legend.fontsize': FS, 'legend.title_fontsize': FS, 'legend.frameon': False, 'legend.handlelength': 1.6,
    'legend.handletextpad': 0.5, 'legend.labelspacing': 0.35, 'legend.borderaxespad': 0.0, 'legend.borderpad': 0.0,
    'legend.labelcolor': INK, 'pdf.fonttype': 42, 'savefig.dpi': 300, 'figure.dpi': 300})


def new_figure():
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    l, b = MARGIN['left'] / FIG_W, MARGIN['bottom'] / FIG_H
    ax = fig.add_axes([l, b, AX_W_PT / 72 / FIG_W, AX_H_PT / 72 / FIG_H])
    for side in ('left', 'bottom'):
        ax.spines[side].set_position(('outward', 4))      # detached axes: nothing crowds the origin
    return fig, ax


def normal_step(ax):
    """Data units per point along the normal of a line of slope -1 or +1 in data space (linear axes)."""
    (x0, x1), (y0, y1) = ax.get_xlim(), ax.get_ylim()
    sx, sy = AX_W_PT / (x1 - x0), AX_H_PT / (y1 - y0)
    return math.hypot(1 / sx, 1 / sy), sx, sy


def series(ax, x, y, **kw):
    kw.setdefault('lw', LW)
    kw.setdefault('clip_on', False)                        # a line along the frame keeps its full width
    return ax.plot(x, y, **kw)[0]


def label(ax, x, y, s, ha='left', va='baseline', **kw):
    return ax.text(x, y, s, ha=ha, va=va, color=kw.pop('color', INK), fontsize=kw.pop('fontsize', FS), **kw)


def arrow(ax, xy_from, xy_to, shrink_from, shrink_to):
    """Arrow that starts and ends 1 pt clear of the lines it connects (shrink = half their width + 1 pt)."""
    ax.annotate('', xy=xy_to, xytext=xy_from,
                arrowprops=dict(arrowstyle='-|>', color=INK2, lw=LW_ARROW, shrinkA=shrink_from, shrinkB=shrink_to,
                                mutation_scale=7, capstyle='round'))


def legend(ax, handles, labels, **kw):
    leg = ax.legend(handles, labels, alignment='left', **kw)
    for h in leg.legend_handles:                           # line samples end flush with the text column
        if isinstance(h, Line2D):
            h.set_solid_capstyle('butt'); h.set_dash_capstyle('butt')
    leg.get_title().set_color(INK)
    return leg


# ------------------------------------------------------- clearance check -----------------------------------------
def _seg_rect_dist(p, q, r):
    """Distance between segment pq and axis-aligned rectangle r = (x0, y0, x1, y1); 0 if they touch."""
    x0, y0, x1, y1 = r
    def inside(pt): return x0 <= pt[0] <= x1 and y0 <= pt[1] <= y1
    if inside(p) or inside(q): return 0.0
    edges = [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]
    def cross(a, b, c): return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    def seg_seg_intersect(a, b, c, d):
        d1, d2, d3, d4 = cross(c, d, a), cross(c, d, b), cross(a, b, c), cross(a, b, d)
        return (d1 * d2 < 0) and (d3 * d4 < 0)
    if any(seg_seg_intersect(p, q, e0, e1) for e0, e1 in edges): return 0.0
    def pt_seg(pt, a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        t = 0.0 if dx == dy == 0 else max(0.0, min(1.0, ((pt[0] - a[0]) * dx + (pt[1] - a[1]) * dy) / (dx * dx + dy * dy)))
        return math.hypot(pt[0] - (a[0] + t * dx), pt[1] - (a[1] + t * dy))
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    return min([pt_seg(c, p, q) for c in corners] + [pt_seg(p, *e) for e in edges] + [pt_seg(q, *e) for e in edges])


def _rect_rect_dist(a, b):
    return math.hypot(max(0.0, max(a[0], b[0]) - min(a[2], b[2])), max(0.0, max(a[1], b[1]) - min(a[3], b[3])))


def check_clearance(fig, name):
    """Every visible label keeps MIN_GAP_PT from every line, arrow, marker, spine, tick and other label."""
    fig.canvas.draw()
    rnd = fig.canvas.get_renderer()
    ppt = fig.dpi / 72.0
    texts, polylines = [], []
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            for tick in axis._update_ticks():
                if tick.label1.get_visible() and tick.label1.get_text():
                    texts.append(('tick label ' + tick.label1.get_text(), tick.label1.get_window_extent(rnd)))
                if tick.tick1line.get_visible():
                    tl = tick.tick1line
                    x, y = tl.get_transform().transform(tl.get_xydata())[0]
                    size = tl.get_markersize() * ppt
                    seg = [(x, y), (x, y - size)] if axis is ax.xaxis else [(x, y), (x - size, y)]
                    polylines.append(('tick mark', seg, tl.get_markeredgewidth() * ppt / 2, 'tick'))
        for lab in (ax.xaxis.label, ax.yaxis.label):
            if lab.get_text(): texts.append(('axis title', lab.get_window_extent(rnd)))
        for sname, sp in ax.spines.items():
            if sp.get_visible():
                pts = sp.get_transform().transform(sp.get_path().vertices)
                polylines.append((f'{sname} axis', [tuple(p) for p in pts], sp.get_linewidth() * ppt / 2, 'spine'))
        for ln in ax.lines:
            if not ln.get_visible(): continue
            pts = [tuple(p) for p in ln.get_transform().transform(ln.get_xydata())]
            if ln.get_linestyle() not in ('None', '', ' ') and len(pts) > 1:
                polylines.append((f'line {ln.get_label()}', pts, ln.get_linewidth() * ppt / 2, 'data'))
            if ln.get_marker() not in (None, 'None', '', ' '):
                r = (ln.get_markersize() / 2 + ln.get_markeredgewidth()) * ppt
                for p in pts: polylines.append((f'marker {ln.get_label()}', [p, p], r, 'data'))
        for t in ax.texts:
            if t.get_text().strip():
                texts.append((f'label "{t.get_text()}"', t.get_window_extent(rnd)))
            patch = getattr(t, 'arrow_patch', None)
            if patch is not None:
                for poly in patch.get_path().to_polygons(closed_only=False):
                    polylines.append(('arrow', [tuple(p) for p in poly], patch.get_linewidth() * ppt / 2, 'data'))
        for leg in [c for c in ax.get_children() if isinstance(c, Legend)]:
            texts.append(('legend', leg.get_window_extent(rnd)))
    problems, nearest = [], {}
    gap = MIN_GAP_PT * ppt
    fb = fig.bbox
    for i, (tn, tb) in enumerate(texts):
        r = (tb.x0, tb.y0, tb.x1, tb.y1)
        if tb.x0 < fb.x0 or tb.y0 < fb.y0 or tb.x1 > fb.x1 or tb.y1 > fb.y1:
            problems.append(f'{tn} leaves the figure')
        for pn, pts, hw, kind in polylines:
            if tn.startswith('tick label') and kind in ('tick', 'spine'): continue
            if tn == 'axis title' and kind in ('tick', 'spine'): continue
            d = min(_seg_rect_dist(pts[k], pts[k + 1], r) for k in range(len(pts) - 1)) - hw
            if kind == 'data' and d / ppt < nearest.get(tn, (1e9, ''))[0]: nearest[tn] = (d / ppt, pn)
            if d < gap: problems.append(f'{tn} is {d / ppt:.2f} pt from {pn}')
        for j, (un, ub) in enumerate(texts):
            if j <= i: continue
            need = 1.0 * ppt if tn.startswith('tick label') and un.startswith('tick label') else gap
            d = _rect_rect_dist(r, (ub.x0, ub.y0, ub.x1, ub.y1))
            if d < need: problems.append(f'{tn} is {d / ppt:.2f} pt from {un}')
    if problems:
        raise SystemExit(f'{name}: clearance check failed:\n  ' + '\n  '.join(problems))
    shown = [f'{k} {v[0]:.1f} pt from {v[1]}' for k, v in sorted(nearest.items(), key=lambda kv: kv[1][0])
             if not k.startswith('tick label') and k != 'axis title']
    print(f'{name}: clearance check passed; nearest line to each label: ' + '; '.join(shown))


def frame_to_ticks(ax):
    """Axis lines span exactly the first to the last tick (range frame)."""
    lo, hi = ax.get_xlim(); xt = [t for t in ax.get_xticks() if lo - 1e-12 <= t <= hi + 1e-12]
    lo, hi = ax.get_ylim(); yt = [t for t in ax.get_yticks() if lo - 1e-12 <= t <= hi + 1e-12]
    ax.spines['bottom'].set_bounds(min(xt), max(xt)); ax.spines['left'].set_bounds(min(yt), max(yt))


def save(fig, name):
    for ax in fig.axes: frame_to_ticks(ax)
    check_clearance(fig, name)
    fig.savefig(os.path.join(out, name + '.pdf'))
    fig.savefig(os.path.join(out, name + '.png'), dpi=300)
    plt.close(fig)


TICKS01 = [0, 0.2, 0.4, 0.6, 0.8, 1.0]

# ------------------------------------------ Fig. 1: the error floor alpha + beta >= 1 - delta(b) -------------------
fig, ax = new_figure()
ax.set_xlim(0, 1); ax.set_ylim(0, YMAX)
n, sx, sy = normal_step(ax)
xs = [i / 400 for i in range(401)]
for delta, col in zip((0.9, 0.5, 0.0), ORANGE):
    c = 1 - delta
    ax.fill_between(xs, 0, [max(0.0, c - x) for x in xs], color=ORANGE[1], alpha=0.08, lw=0)
    series(ax, [0, c], [c, 0], color=col, label=f'delta={delta:g}', clip_on=True)   # ends flush with the fills
    x0 = GAP / sx                                           # GAP in from the vertical axis ...
    label(ax, x0, c - x0 + (GAP + LW / 2) * n, rf'$\delta={delta:g}$', va='baseline')  # ... and the glyphs GAP above the line
arrow(ax, (0.25, 0.25), (0.5, 0.5), LW / 2 + 1, LW / 2 + 1)                # floor at delta = 0.5 to floor at delta = 0
xa = 0.375                                                                 # hangs GAP below the arrow's midpoint
label(ax, xa, xa - (GAP + LW_ARROW / 2) * n, r'budget $b$ grows', va='top')
ax.set_xticks(TICKS01); ax.set_yticks(TICKS01)
ax.set_xlabel(r'false-accept probability $\alpha$'); ax.set_ylabel(r'false-reject probability $\beta$')
save(fig, 'fig1_error_floor')

# ------------------------------------------------- Fig. 2: the admission policy's ROC ------------------------------
Phi, Phi_inv = NormalDist().cdf, NormalDist().inv_cdf
fig, ax = new_figure()
ax.set_xlim(0, 1); ax.set_ylim(0, YMAX)
n, sx, sy = normal_step(ax)
xs = [0.0] + [i / 1000 for i in range(1, 1000)] + [1.0]
curves = []
for D, col in zip((0.28, 0.80, 1.45, 2.60), BLUE):
    curves.append(series(ax, xs, [0.0] + [Phi(Phi_inv(x) + D) for x in xs[1:-1]] + [1.0], color=col, label=rf'$\Delta={D:.2f}$'))
series(ax, [0, 1], [0, 1], color=INK2, lw=LW_REF, label='diagonal')
xd = 0.22                                                                  # the diagonal is named where it runs alone
label(ax, xd, xd - (GAP + LW_REF / 2) * n, r'$\Delta=0$', va='top')
COL_X = 0.53                                                               # arrow caption and legend share this left edge
arrow(ax, (Phi(-1.30), Phi(1.30)), (0.5, 0.5), LW / 2 + 1, LW_REF / 2 + 1)  # along the anti-diagonal, Delta = 2.60 to 0
cap = label(ax, COL_X, COL_X - (GAP + LW_REF / 2) * n, r'mimicry spending: $\Delta\to0$', va='top')
fig.canvas.draw()
cap_bottom = ax.transData.inverted().transform((0, cap.get_window_extent(fig.canvas.get_renderer()).y0))[1]
legend(ax, curves[::-1], [c.get_label() for c in curves[::-1]], loc='upper left',
       bbox_to_anchor=(COL_X, (cap_bottom - 3 * GAP / sy) / YMAX))           # set apart: the caption names the arrow
ax.set_xticks(TICKS01); ax.set_yticks(TICKS01)
ax.set_xlabel(r'leakage, $\mathrm{Pr}[\mathrm{admit}\mid\mathrm{acquired}]$')
ax.set_ylabel(r'openness, $\mathrm{Pr}[\mathrm{admit}\mid\mathrm{genuine}]$')
save(fig, 'fig2_admission_roc')

# ------------------------------------------- Fig. 3: purchasable indistinguishability by route ----------------------
# Illustrative routes: delta_j(b) = sqrt(1 - (b / I_j)^2) on [0, I_j], acquisition index I(0) = 4, corruption index I_C(0) = 7.
IA, IC = 4.0, 7.0
def route(I): bs = [I * i / 400 for i in range(401)]; return bs, [math.sqrt(max(0.0, 1 - (b / I) ** 2)) for b in bs]
fig, ax = new_figure()
ax.set_xlim(0, 9); ax.set_ylim(0, YMAX)
bA, dA = route(IA); bC, dC = route(IC)
gap_fill = ax.fill_between(bA, [max(0.0, 1 - b / IA) for b in bA], dA, color=CAT['aqua'], alpha=0.12, lw=0,
                           label='amortization gap')
lC = series(ax, bC, dC, color=CAT['blue'], label='route C: corruption')
lA = series(ax, bA, dA, color=CAT['orange'], label='route A: acquisition')
lE = series(ax, [IA, 0], [0, 1], color=CAT['aqua'], ls=(1.9, (3.2, 2.2)), zorder=1.9, label='convex envelope')  # gaps at both ends
for I, col in ((IA, CAT['orange']), (IC, CAT['blue'])):
    ax.plot([I], [0], ls='none', marker='o', ms=3.6, mfc=col, mec='white', mew=0.9, clip_on=False, zorder=5,
            label='_nolegend_')
leg = legend(ax, [lC, lA, lE, gap_fill], [h.get_label() for h in (lC, lA, lE, gap_fill)], loc='upper right')
leg.legend_handles[2].set_linestyle((0, (3.2, 2.2)))                          # the sample starts on a full dash
ax.set_xticks(range(10)); ax.set_yticks(TICKS01)
tl = [str(k) for k in range(10)]; tl[4] = r'$I(0)$'; tl[7] = r'$I_{\mathrm{C}}(0)$'
ax.set_xticklabels(tl)
ax.set_xlabel(r'adversary budget $b$'); ax.set_ylabel(r'$\delta(b)=\inf_{\mathrm{cost}(A)\leq b}\,\mathrm{TV}(P_1,P_2^{(A)})$')
save(fig, 'fig3_by_route')

# ---------------------------------- Fig. 4: robustness of the admission policy to mis-estimated costs ----------------
data = {}
with open(os.path.join(here, 'fig4_data.csv')) as fh:
    for row in csv.DictReader(fh):
        data.setdefault(float(row['share_f']), []).append((float(row['rho']), float(row['retained_fraction'])))
fig, ax = new_figure()
ax.set_xscale('log'); ax.set_xlim(1e-3, 1); ax.set_ylim(0, YMAX)
sy = AX_H_PT / YMAX
x_in = 1e-3 * 10 ** (3 * GAP / AX_W_PT)                                  # GAP in from the vertical axis
series(ax, [1e-3, 0.56], [1, 1], color=INK2, lw=LW_REF, ls=(0, (0.01, 2.5)), dash_capstyle='round', label='no loss')  # stops before the curves meet it
label(ax, x_in, 1 + (GAP + LW_REF / 2) / sy, r'no loss, $\rho=\hat\rho$', va='bottom', color=INK2)
lines = []
for f, col in zip((0.2, 0.5, 0.8), BLUE[1:]):
    pts = sorted(data[f])
    lines.append(series(ax, [p[0] for p in pts], [p[1] for p in pts], color=col, label=rf'$f={f}$'))
top = min(y for x, y in sorted(data[0.5])) - (GAP + LW / 2) / sy          # GAP below the f = 0.5 plateau
legend(ax, lines, [l.get_label() for l in lines], loc='upper left', bbox_to_anchor=(GAP / AX_W_PT, top / YMAX),
       title=r'share $f$ of estimated cost')
ax.set_yticks(TICKS01)
ax.set_xlabel(r'true $\rho$ of the mis-priced class ($\hat\rho=1$, $\varepsilon=0.2$)')
ax.set_ylabel(r'$I(\varepsilon;p\propto\hat c)\,/\,I(\varepsilon;p\propto\kappa)$')
save(fig, 'fig4_estimation_error')
print('figures written to', out)
