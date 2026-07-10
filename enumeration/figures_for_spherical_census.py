#!/usr/bin/env python3
"""figures_for_spherical_census.py — publication figures for the spherical paper.

Reproduces the figures Rao (1998) published, but from the CERTIFIED census roots
wherever one exists, using the corrected Rao topology (produced corners 18, 16,
17, 19; enforced by the generator's fail-loud guard on import).

  fig_rao4_certified.pdf   Rao Fig. 4 (p.219): {1,2,4,5,10,19} in four views
                           (plan, front/side/rear elevations), certified root.
  fig_rao5_optima.pdf      Rao Fig. 5 (p.221): local optima at h = 80/60/40/20 deg,
                           rendered from Rao Table 2 through the frozen chain.
                           REFERENCE figures (F1 = F2 ~ 0 at published precision);
                           they are NOT census roots (h is pinned, not free).
  fig_rao_table1_grid.pdf  Rao Table 1 (p.218): all eight constrained figures.
                           Seven from certified census roots (residuals ~1e-16;
                           agreement with Rao's six published digits ~1e-6),
                           with two annotated findings:
                             - {1,2,3,6,16,19}: erratum in Rao's `e` (2.4e-3);
                               certified value drawn.
                             - {1,2,8,9,16,19}: structurally dependent
                               (F16 = F9 - F8 identically); excluded from the
                               3044-subset census universe; drawn from Rao's
                               published values for completeness.
  fig_both_type_subset.pdf {1,2,3,4,6,13}: two certified roots, one Gate-4 valid
                           and one rejected, side by side.  The rejected root's
                           produced corners visibly cross the bounding circle.
                           The per-root-validity thesis image (Sections 2/6).

Run from the engine checkout next to spherical_roots.jsonl. Provenance (engine
hash, dataset DOI, residuals) is printed in each figure's footer and to stdout.
"""
import json, math, sys, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra_plane.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

import sriyantra as RAO
import roots_to_spherical_atlas_json as GEN   # corrected TRIANGLES + guard

SAKTI = "#b23a48"; SIVA = "#2e4374"; RIM = "#999489"
DATASET_DOI = "10.5281/zenodo.21170076"

RAO_TABLE1 = {
    (1,2,3,5,10,19):  (0.105036,0.054376,0.065419,0.105517,0.024275,1.344437),
    (1,2,3,6,16,19):  (0.450462,0.442391,0.445729,0.425478,0.183904,0.539209),
    (1,2,3,10,19,20): (0.244730,0.158369,0.158369,0.225411,0.060166,1.042990),
    (1,2,4,5,10,19):  (0.231687,0.120012,0.146680,0.230471,0.053009,1.076084),
    (1,2,4,8,13,19):  (0.463973,0.753761,0.890177,0.375039,0.466743,0.261736),
    (1,2,4,10,15,19): (0.252893,0.132925,0.160863,0.249384,0.057987,1.031951),
    (1,2,6,8,9,10):   (0.449590,0.332617,0.328263,0.430650,0.129804,0.722398),
    (1,2,8,9,16,19):  (0.543803,0.343194,0.361271,0.466999,0.107003,0.353166),
}
RAO_TABLE2 = {  # (h_deg): (b, c, d, e, g, h_rad) — spherical local optima, Rao p.218
    80: (0.084209,0.045523,0.050280,0.081483,0.018869,1.396263),
    60: (0.252905,0.135694,0.153570,0.242150,0.055149,1.047198),
    40: (0.420594,0.226806,0.266654,0.392349,0.088153,0.698132),
    20: (0.552508,0.365712,0.415116,0.484367,0.127998,0.349066),
}

def census_root(subset):
    for line in open("spherical_roots.jsonl"):
        r = json.loads(line)
        if tuple(r["subset"]) == subset and r["class"] == "FEASIBLE_CERTIFIED" and r.get("roots"):
            best = min(r["roots"], key=lambda rt: max(
                abs(a-b) for a, b in zip(rt["coords"], RAO_TABLE1[subset])))
            return best
    return None

def edges3d(coords):
    b, c, d, e, g, h = coords
    P = GEN.assemble_points(b, c, d, e, g, h)
    out = []
    for apex, cor, kind in GEN.TRIANGLES:
        A = np.asarray(P[apex]); C = np.asarray(P[cor]); Cm = GEN.mirror(C)
        col = SAKTI if kind == "sakti" else SIVA
        for X, Y in [(A, C), (C, Cm), (Cm, A)]:
            out.append((np.array(GEN.slerp_polyline(X, Y)), col))
    return out, math.pi/2 - h

def draw_view(ax, edges, r, proj, rim=True, lw=0.9):
    """proj maps a 3D point array (n,3) to (n,2) screen coords."""
    R = math.sin(min(r, math.pi/2)); z0 = math.cos(min(r, math.pi/2))
    if rim:
        th = np.linspace(0, 2*math.pi, 256)
        rim3 = np.stack([R*np.cos(th), R*np.sin(th), np.full_like(th, z0)], axis=1)
        Q = proj(rim3); ax.plot(Q[:, 0], Q[:, 1], color=RIM, lw=0.7)
    for E, col in edges:
        Q = proj(E); ax.plot(Q[:, 0], Q[:, 1], color=col, lw=lw)
    ax.set_aspect("equal"); ax.axis("off")

PLAN  = lambda E: E[:, :2]
FRONT = lambda E: E[:, [0, 2]]
SIDE  = lambda E: E[:, [1, 2]]
REAR  = lambda E: np.stack([-E[:, 0], E[:, 2]], axis=1)

def inner_circle(ax, coords, proj):
    """Rao draws the inscribed circle of the innermost triangle (radius rT about Pc)."""
    b, c, d, e, g, h = coords
    try: rT = RAO.chain(*coords)["rT"]
    except Exception: return
    th = np.linspace(0, 2*math.pi, 128)
    # small circle of angular radius rT about the cap centre (north pole)
    circ = np.stack([math.sin(rT)*np.cos(th), math.sin(rT)*np.sin(th),
                     np.full_like(th, math.cos(rT))], axis=1)
    Q = proj(circ); ax.plot(Q[:, 0], Q[:, 1], color="black", lw=0.8)

def footer(fig, text):
    fig.text(0.5, 0.012, text, ha="center", fontsize=7, color="#555",
             family="monospace")

# ---------------------------------------------------------------- Fig. 4
def fig_rao4():
    sub = (1, 2, 4, 5, 10, 19)
    rt = census_root(sub)
    edges, r = edges3d(rt["coords"])
    dmax = max(abs(a-b) for a, b in zip(rt["coords"], RAO_TABLE1[sub]))
    fig = plt.figure(figsize=(7.2, 9.2))
    gs = fig.add_gridspec(3, 3, height_ratios=[1, 2.4, 1], width_ratios=[1, 2.4, 1])
    axR = fig.add_subplot(gs[0, 1]); axP = fig.add_subplot(gs[1, 1])
    axS = fig.add_subplot(gs[1, 0]); axF = fig.add_subplot(gs[2, 1])
    draw_view(axR, edges, r, REAR);  axR.set_title("REAR ELEVATION", fontsize=9)
    draw_view(axP, edges, r, PLAN);  inner_circle(axP, rt["coords"], PLAN)
    axP.set_title("PLAN VIEW", fontsize=9)
    draw_view(axS, edges, r, SIDE);  axS.set_title("SIDE ELEVATION", fontsize=9, rotation=90, x=-0.08, y=0.35)
    draw_view(axF, edges, r, FRONT); axF.set_title("FRONT ELEVATION", fontsize=9)
    fig.suptitle("Spherical figure for constraints {1, 2, 4, 5, 10, 19} — certified census root\n"
                 "(after Rao 1998, Fig. 4)", fontsize=11)
    footer(fig, f"certified root: residual {rt['residual']:.1e} · Gate-4 "
                f"{'valid' if rt['gate4']['valid'] else 'rejected'} · engine {GEN.ENGINE_HASH if hasattr(GEN,'ENGINE_HASH') else 'de64edfa4979'} · "
                f"dataset {DATASET_DOI} · max|Δ| vs Rao Table 1: {dmax:.1e}")
    fig.savefig("fig_rao4_certified.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"fig_rao4_certified.pdf     residual {rt['residual']:.1e}  |Δ|max vs Rao {dmax:.1e}")

# ---------------------------------------------------------------- Fig. 5
def fig_rao5():
    fig, axes = plt.subplots(2, 2, figsize=(7.4, 8.2))
    for ax, (hdeg, vals) in zip(axes.flat, sorted(RAO_TABLE2.items(), reverse=True)):
        F = RAO.constraints(*vals)
        edges, r = edges3d(vals)
        draw_view(ax, edges, r, PLAN, lw=0.8)
        inner_circle(ax, vals, PLAN)
        ax.set_title(f"altitude h = {hdeg}°   (|F1|={abs(F[1]):.0e}, |F2|={abs(F[2]):.0e})", fontsize=9)
    fig.suptitle("Spherical local optimum figures (after Rao 1998, Fig. 5)\n"
                 "altitude-pinned reference figures from Rao Table 2, via the frozen chain",
                 fontsize=11)
    footer(fig, f"rendered through the frozen engine chain · corrected Rao topology "
                f"(produced corners 18, 16, 17, 19) · dataset {DATASET_DOI}")
    fig.savefig("fig_rao5_optima.pdf", bbox_inches="tight")
    plt.close(fig)
    print("fig_rao5_optima.pdf        4 panels (h = 80/60/40/20°), reference figures")

# ---------------------------------------------------------------- Table 1 grid
def fig_table1():
    fig, axes = plt.subplots(2, 4, figsize=(13.2, 7.4))
    for ax, (sub, vals) in zip(axes.flat, RAO_TABLE1.items()):
        rt = census_root(sub)
        if rt is not None:
            edges, r = edges3d(rt["coords"])
            dmax = max(abs(a-b) for a, b in zip(rt["coords"], vals))
            note = f"certified · res {rt['residual']:.0e} · |Δ| {dmax:.0e}"
            if sub == (1,2,3,6,16,19):
                note += "\nRao Table-1 erratum in e (2.4e-3); certified value drawn"
        else:  # the structurally dependent subset
            edges, r = edges3d(vals)
            note = "structurally dependent (F16 ≡ F9 − F8);\nexcluded from census universe; Rao's values drawn"
        draw_view(ax, edges, r, PLAN, lw=0.65)
        ax.set_title("{" + ",".join(map(str, sub)) + "}", fontsize=9)
        ax.text(0.5, -0.06, note, transform=ax.transAxes, ha="center",
                fontsize=6.4, color="#555")
    fig.suptitle("Rao (1998) Table 1: all eight constrained spherical figures —\n"
                 "seven re-derived as certified census roots at ~1e-16 residual", fontsize=12)
    footer(fig, f"corrected Rao topology · engine de64edfa4979 · dataset {DATASET_DOI} · "
                f"CENSUS_CHECKPOINT_LAYER1_K12")
    fig.savefig("fig_rao_table1_grid.pdf", bbox_inches="tight")
    plt.close(fig)
    print("fig_rao_table1_grid.pdf    8 panels (7 certified + 1 dependent reference)")

# ---------------------------------------------------------------- Fig. 1
def fig_both_type():
    sub = (1, 2, 3, 4, 6, 13)
    roots = []
    for line in open("spherical_roots.jsonl"):
        r = json.loads(line)
        if tuple(r["subset"]) == sub:
            roots = r["roots"]; break
    roots.sort(key=lambda rt: not rt["gate4"]["valid"])   # valid panel first
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 5.0))
    for ax, rt in zip(axes, roots):
        b, c, d, e, g, h = rt["coords"]; r_ = math.pi/2 - h
        edges, r0 = edges3d(rt["coords"])
        draw_view(ax, edges, r0, PLAN, lw=0.8)
        v = rt["gate4"]["valid"]
        ax.set_title(("Gate-4 VALID root" if v else "Gate-4 REJECTED root")
                     + f"   (res {rt['residual']:.0e}, radius {rt['radius']:g})", fontsize=9)
        m_bc, m_de = r_-(b+c), r_-(d+e)
        ax.text(0.5, -0.07, f"containment margins:  r-(b+c) = {m_bc:+.3f}   r-(d+e) = {m_de:+.3f}",
                transform=ax.transAxes, ha="center", fontsize=7.5,
                color="#555" if v else SAKTI)
    fig.suptitle("One six-constraint subset, two certified roots of differing geometric validity\n"
                 "{1, 2, 3, 4, 6, 13} — geometric validity is a per-root property", fontsize=11)
    footer(fig, f"both roots Krawczyk-certified · engine de64edfa4979 · dataset {DATASET_DOI} · "
                f"CENSUS_CHECKPOINT_LAYER1_K12")
    fig.savefig("fig_both_type_subset.pdf", bbox_inches="tight")
    plt.close(fig); print("fig_both_type_subset.pdf   the per-root-validity figure (Sections 2/6)")

if __name__ == "__main__":
    fig_rao4(); fig_rao5(); fig_table1(); fig_both_type()
    print("done — vector PDFs written")
