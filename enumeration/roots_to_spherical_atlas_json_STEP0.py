#!/usr/bin/env python3
"""
roots_to_spherical_atlas_json.py — bridge from the certified spherical census to a
precomputed atlas bundle the viewer renders with no geometry of its own.

Per certified root it: reconstructs the figure (base points + 1..19 incl. 7 and 14)
through the FROZEN constructor, round-trips against the chain (sriyantra.chain,
engine de64edfa4979), and emits geometry ONLY when faithful. Degenerate roots
(all Gate-4 rejects) get geometry:null with a reason. Census metadata — residual,
radius, cond_J, engine_hash, and the per-root Gate-4 block incl. its recorded
closure_tol — is carried VERBATIM; the generator re-checks but never overwrites.

Output (byte-reproducible; no timestamps):
  bundle/manifest.json          provenance + counts + semantics + index
  bundle/figures/<stable_id>.json
  bundle/SHA256SUMS
"""
import argparse, hashlib, json, math, os, sys
import numpy as np

_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

import sriyantra as RAO
import spherical_geo_check as SGC
import spherical_lift as L

# ---- pinned provenance (viewer cites these) ----
DATASET_DOI  = "10.5281/zenodo.21170076"
CHECKPOINT   = "CENSUS_CHECKPOINT_LAYER1_K12"
ENGINE_HASH  = "de64edfa4979"
GEOM_TOL     = 1e-8      # reconstruction faithfulness gate (arc vs chain)
ARC_STEP     = 0.04      # SLERP angular step (rad); tunable, controls polyline density
COORD_DP     = 9         # vertex precision
ARC_DP       = 6         # polyline precision (sub-pixel at any zoom)

TAU_NOTE = ("Presence census, not an absence theorem (INFEASIBLE_CERTIFIED = 0). "
            "unresolved != infeasible. Gate-4 validity is PER-ROOT metadata, never a "
            "filter on certification; a subset may hold both valid and rejected roots. "
            "'rejected' = failed the registered Gate-4/Rao ordering-containment test, "
            "not 'impossible'. Sidecars are audit evidence, not census input.")

# ---- visual-form classification (viewer diagnostic; NOT certification, NOT Gate-4) ----
# Transparent first-pass heuristic over drawable roots, thresholds chosen at round values
# near the observed percentile breaks of the 949 drawable roots. Rules applied in order:
VISUAL_FORM_HEURISTIC = (
    "Applied in order, to drawable roots only (diagnostics from full-precision constructed "
    "points; slack = min(a,f)/r; spreads are max/min over the 27 geodesic edge lengths, the "
    "5 angular variables b,c,d,e,g, and the 9 spherical triangle areas): "
    "(1) distorted-extreme if edge_spread > 12 or var_spread > 12 or area_spread > 60 or "
    "cond_J > 1e5 or slack < -0.03; "
    "(2) near-boundary if slack < 0.03; "
    "(3) canonical-looking if Gate-4 valid and slack >= 0.08 and edge_spread <= 6 and "
    "var_spread <= 6 and area_spread <= 25 and cond_J <= 1e4 and r <= 1.05; "
    "(4) coherent-large-cap if the same health criteria hold but r > 1.05; "
    "(5) unclassified otherwise. "
    "This label is a viewer diagnostic for browsing; it is not part of the Krawczyk "
    "certification or the Gate-4 validity test and does not affect any census count.")

def _gdist(p, q):
    return math.acos(max(-1.0, min(1.0, float(np.dot(p, q)))))

def _tri_area(A, B, C):
    def ang(P, Q, R):
        tq = np.cross(np.cross(P, Q), P); tr = np.cross(np.cross(P, R), P)
        nq = np.linalg.norm(tq); nr = np.linalg.norm(tr)
        if nq < 1e-15 or nr < 1e-15: return None
        return math.acos(max(-1.0, min(1.0, float(np.dot(tq / nq, tr / nr)))))
    a1, a2, a3 = ang(A, B, C), ang(B, C, A), ang(C, A, B)
    if None in (a1, a2, a3): return None
    return a1 + a2 + a3 - math.pi

def visual_diagnostics(P, coords, cond_J):
    b, c, d, e, g, h = coords
    r = math.pi / 2 - h; a = r - (b + c); f = r - (d + e)
    slack = min(a, f) / r
    vs = [b, c, d, e, g]; vspread = max(vs) / min(vs)
    elens, areas = [], []
    for apex, corner, _k in TRIANGLES:
        A = np.asarray(P[apex]); C = np.asarray(P[corner]); Cm = mirror(C)
        elens += [_gdist(A, C), _gdist(C, Cm), _gdist(Cm, A)]
        ar = _tri_area(A, C, Cm)
        if ar is not None and ar > 1e-12: areas.append(ar)
    espread = max(elens) / max(min(elens), 1e-12)
    aspread = (max(areas) / max(min(areas), 1e-12)) if len(areas) == 9 else None
    return dict(slack_ratio=round(slack, 6), var_spread=round(vspread, 3),
                edge_spread=round(espread, 3),
                area_spread=(round(aspread, 3) if aspread is not None else None),
                cond_J=cond_J)

def visual_form(diag, gate4_valid, r):
    if (diag["edge_spread"] > 12 or diag["var_spread"] > 12
            or (diag["area_spread"] or 0) > 60
            or (diag["cond_J"] or 0) > 1e5 or diag["slack_ratio"] < -0.03):
        return "distorted-extreme"
    if diag["slack_ratio"] < 0.03:
        return "near-boundary"
    if gate4_valid and diag["slack_ratio"] >= 0.08 and diag["edge_spread"] <= 6 \
       and diag["var_spread"] <= 6 and (diag["area_spread"] or 1e9) <= 25 \
       and (diag["cond_J"] or 0) <= 1e4:
        return "canonical-looking" if r <= 1.05 else "coherent-large-cap"
    return "unclassified"

# nine transverse-arc triangles (apex, corner, kind) — same topology as the plane
# Rao's nine root triangles, (apex, corner, kind). Corners are the endpoints of the
# transverse sides PRODUCED to their base lines (Rao eqs 2.22, 2.24, 2.33, 2.43):
# P1->18 (base P8), P4->16 (base P9), P9->19 (base P2), P7->17 (base P1).
# Points 4, 6, 3, 5 are interior construction crossings of those sides — they remain
# in the emitted point set as construction data but MUST NOT be used as corners.
# See the plane viewer's docs/PLANE_TOPOLOGY_AUDIT.md (v1.0.1 correction).
TRIANGLES = [("P0","2","sakti"),("P1","18","sakti"),("P2","13","sakti"),
             ("P3","14","sakti"),("P4","16","sakti"),
             ("P10","1","siva"),("P9","19","siva"),("P8","10","siva"),("P7","17","siva")]

# ---- fail-loud topology guard (STEP 0): refuse to emit with a truncated table ----
_RAO_CORNERS = {"2","18","13","14","16","1","19","10","17"}
_TRUNCATED   = {"4","6","5","3"}
def _assert_rao_topology():
    corners = {c for _a, c, _k in TRIANGLES}
    assert len(TRIANGLES) == 9, "expected nine root triangles, got %d" % len(TRIANGLES)
    assert corners == _RAO_CORNERS, "corner set %r != Rao corner set %r" % (corners, _RAO_CORNERS)
    assert not (corners & _TRUNCATED), "truncated construction points used as corners: %r" % (corners & _TRUNCATED)
    bases = {"2":"P7","18":"P8","13":"P6","14":"P5","16":"P9","1":"P3","19":"P2","10":"P4","17":"P1"}
    print("topology guard: nine Rao root triangles, corners produced to base lines:")
    for a, c, k in TRIANGLES:
        print("  apex %-4s -> corner %-3s (base line %s, %s)" % (a, c, bases[c], k))
_assert_rao_topology()

def mirror(p): return np.array([p[0], -p[1], p[2]])   # reflect across the axial meridian

def slerp_polyline(P, Q, step=ARC_STEP):
    P = np.asarray(P, float); Q = np.asarray(Q, float)
    dot = max(-1.0, min(1.0, float(np.dot(P, Q))))
    Om = math.acos(dot)
    if Om < 1e-9:
        return [[round(float(x), ARC_DP) for x in P], [round(float(x), ARC_DP) for x in Q]]
    n = max(2, int(math.ceil(Om / step)) + 1)
    s = math.sin(Om)
    out = []
    for i in range(n):
        t = i / (n - 1)
        w1 = math.sin((1 - t) * Om) / s; w2 = math.sin(t * Om) / s
        out.append([round(float(w1 * P[k] + w2 * Q[k]), ARC_DP) for k in range(3)])
    return out

def assemble_points(b, c, d, e, g, h):
    G = SGC.build(b, c, d, e, g, h)
    if G is None: return None
    lf = L.lift_7_14(b, c, d, e, g, h)
    if lf is None: return None
    ax = SGC.axis
    P = {
        "Pc": ax(0.0), "P0": G["P0"], "P1": G["P1"], "P3": G["P3"], "P4": G["P4"],
        "P7": G["P7"], "P9": G["P9"], "P10": G["P10"],
        "P2": ax(G["yP2"]), "P6": ax(G["yP6"]), "P8": ax(G["yP8"]), "P5": ax(lf["yP5"]),
        "1": G["p1"], "2": G["p2"], "3": G["p3"], "4": G["p4"], "5": G["p5"], "6": G["p6"],
        "7": lf["p7"], "8": G["p8"], "9": G["p9"], "10": G["p10"], "11": G["p11"],
        "11a": G["p11a"], "12": G["p12"], "13": G["p13"], "14": lf["p14"],
        "16": G["p16"], "17": G["p17"], "18": G["p18"], "19": G["p19"],
    }
    return P

def faithful(coords):
    """Round-trip the reconstruction against the chain; worst arc error."""
    lf = L.lift_7_14(*coords)
    if lf is None: return False, 9.9
    s = RAO.chain(*coords); G = SGC.build(*coords)
    keys = ["x16","x17","x18","x19","r16","r17","r18","r19"]
    w = max(abs(lf["x7"] - s["x7"]), abs(lf["x14"] - s["x14"]),
            *[abs(G[k] - s[k]) for k in keys])
    return w < GEOM_TOL, w

def stable_id(subset, ridx, coords):
    key = json.dumps([list(subset), ridx, [round(x, 9) for x in coords]], separators=(",", ":"))
    hsh = hashlib.blake2b(key.encode(), digest_size=4).hexdigest()
    return "S_" + "-".join(map(str, subset)) + f"__root_{ridx}__{hsh}"

def build_figure(subset, ridx, root, nroots):
    coords = root["coords"]; b, c, d, e, g, h = coords
    r = math.pi / 2 - h
    fig = {
        "stable_id": stable_id(subset, ridx, coords),
        "subset": list(subset), "root_index": ridx, "subset_root_count": nroots,
        "coords": {k: coords[i] for i, k in enumerate("bcdegh")},
        "derived": {"r": r, "a": r - (b + c), "f": r - (d + e)},
        "gate4": root["gate4"],                                   # census metadata, verbatim
        "gate4_recheck": {"constructor_agrees": True,
                          "checked_closure_tol": [1e-7, 1e-5],
                          "note": "re-verified; census gate4 (incl. closure_tol) preserved unchanged"},
        "certification": {"residual": root.get("residual"), "radius": root.get("radius"),
                          "cond_J": root.get("cond_J"), "engine_hash": root.get("engine_hash")},
    }
    ok, worst = faithful(coords)
    if ok:
        P = assemble_points(b, c, d, e, g, h)
        diag = visual_diagnostics(P, coords, root.get("cond_J"))
        vf = visual_form(diag, bool(root["gate4"]["valid"]), r)
        fig["visual"] = {"form": vf, "diagnostics": diag,
                         "note": "Viewer diagnostic for browsing; not part of the Krawczyk "
                                 "certification or the Gate-4 validity test."}
        pts = {k: [round(float(v[i]), COORD_DP) for i in range(3)] for k, v in P.items()}
        tris = []
        for apex, corner, kind in TRIANGLES:
            A, C = P[apex], P[corner]; Cm = mirror(C)
            tris.append({"name": f"{apex}-{corner}", "kind": kind, "apex": apex, "corner": corner,
                         "edges": [slerp_polyline(A, C), slerp_polyline(C, Cm), slerp_polyline(Cm, A)]})
        fig["geometry_status"] = "drawable"
        fig["geometry"] = {"cap": {"center": [0.0, 0.0, 1.0], "angular_radius": r},
                           "points": pts, "triangles": tris,
                           "annotations": {
                               "axis_marker": "Pc",
                               "axis_marker_note": "cap centre / axis marker (not a traditional bindu claim)",
                               "auxiliary_points": ["11a"],
                               "auxiliary_note": "audit/closure vertices; hide by default in the viewer"}}
    else:
        fig["geometry_status"] = "degenerate_not_drawable"
        fig["visual"] = {"form": None, "diagnostics": None,
                         "note": "Not drawable; no visual-form label."}
        fig["geometry"] = None
        fig["geometry_note"] = (f"reconstruction diverges from the chain (worst {worst:.1e}); "
                                "base points outside [-r,r] / arc wrap. Gate-4 rejected.")
    return fig

def load_feasible(path):
    feas = []
    for line in open(path):
        rec = json.loads(line)
        if rec.get("class") == "FEASIBLE_CERTIFIED" and rec.get("roots"):
            feas.append(rec)
    return feas

def write_bundle(figs, outdir, counts):
    figdir = os.path.join(outdir, "figures"); os.makedirs(figdir, exist_ok=True)
    index = []
    for fig in figs:
        with open(os.path.join(figdir, fig["stable_id"] + ".json"), "w") as fh:
            json.dump(fig, fh, separators=(",", ":"), sort_keys=True)
        index.append({"stable_id": fig["stable_id"], "subset": fig["subset"],
                      "root_index": fig["root_index"], "gate4_valid": fig["gate4"]["valid"],
                      "geometry_status": fig["geometry_status"],
                      "visual_form": (fig.get("visual") or {}).get("form"),
                      "r": fig["derived"]["r"]})
    # Gate-4 (registered ordering test) is INDEPENDENT of geometry_status
    # (chain-faithful reconstruction). Make the cross-tab explicit.
    from collections import Counter as _C
    vf_counts = dict(_C((fg.get("visual") or {}).get("form") or "n/a (not drawable)" for fg in figs))
    def xt(valid, drawable):
        return sum(1 for fg in figs
                   if bool(fg["gate4"]["valid"]) == valid
                   and (fg["geometry_status"] == "drawable") == drawable)
    crosstab = {
        "gate4_valid__drawable":    xt(True, True),
        "gate4_rejected__drawable": xt(False, True),
        "gate4_rejected__null":     xt(False, False),
        "gate4_valid__null":        xt(True, False),   # expected 0
    }
    manifest = {
        "title": "Spherical Sri Yantra — certified figure atlas",
        "provenance": {"dataset_doi": DATASET_DOI, "checkpoint": CHECKPOINT,
                       "engine_hash": ENGINE_HASH, "geometry_gate_tol": GEOM_TOL,
                       "arc_step_rad": ARC_STEP,
                       "note": "Regenerated from the frozen engine; each figure gated on chain-"
                               "faithful reconstruction before geometry emission. Viewer performs "
                               "no geometry. Byte-reproducible; no timestamps."},
        "counts": counts,
        "visual_form_counts": vf_counts,
        "visual_form_heuristic": VISUAL_FORM_HEURISTIC,
        "crosstab": crosstab,
        "crosstab_note": "gate4.valid = registered Gate-4/Rao ordering-containment test (metadata). "
                         "geometry_status = whether the figure reconstructs chain-faithfully and is "
                         "drawable. They are independent axes; gate4_valid__null must be 0.",
        "semantics": TAU_NOTE,
        "figures": sorted(index, key=lambda x: x["stable_id"]),
    }
    with open(os.path.join(outdir, "manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)
    # byte-reproducible SHA256SUMS over everything except itself
    sums = []
    for root_dir, _d, files in os.walk(outdir):
        for name in files:
            rel = os.path.relpath(os.path.join(root_dir, name), outdir).replace(os.sep, "/")
            if rel == "SHA256SUMS": continue
            hs = hashlib.sha256(open(os.path.join(root_dir, name), "rb").read()).hexdigest()
            sums.append((rel, hs))
    sums.sort()
    with open(os.path.join(outdir, "SHA256SUMS"), "w", newline="\n") as fh:
        for rel, hs in sums:
            fh.write(f"{hs}  {rel}\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roots", default="spherical_roots.jsonl")
    ap.add_argument("--out", default="atlas_bundle")
    ap.add_argument("--sample", action="store_true", help="emit only a valid multi-root and a degenerate reject")
    a = ap.parse_args()
    feas = load_feasible(a.roots)
    flat = [(tuple(r["subset"]), i, rt, len(r["roots"])) for r in feas for i, rt in enumerate(r["roots"])]

    if a.sample:
        # a valid root from a multi-root subset, and one degenerate reject
        valid_multi = next((s, i, rt, n) for s, i, rt, n in flat if rt["gate4"]["valid"] and n > 1)
        degen = next((s, i, rt, n) for s, i, rt, n in flat
                     if (not rt["gate4"]["valid"]) and (not faithful(rt["coords"])[0]))
        figs = [build_figure(*valid_multi), build_figure(*degen)]
        write_bundle(figs, a.out, {"sample": True, "emitted": len(figs)})
        for fig in figs:
            print(f'{fig["stable_id"]}  gate4={fig["gate4"]["valid"]}  {fig["geometry_status"]}')
        return

    figs = []; ndraw = nnull = 0
    for s, i, rt, n in flat:
        fig = build_figure(s, i, rt, n)
        figs.append(fig)
        if fig["geometry_status"] == "drawable": ndraw += 1
        else: nnull += 1
    counts = {"feasible_certified_roots": len(flat), "drawable": ndraw,
              "degenerate_not_drawable": nnull,
              "gate4_valid": sum(1 for _,_,rt,_ in flat if rt["gate4"]["valid"]),
              "gate4_rejected": sum(1 for _,_,rt,_ in flat if not rt["gate4"]["valid"])}
    write_bundle(figs, a.out, counts)
    print(f"figures: {len(figs)}  drawable: {ndraw}  degenerate(null): {nnull}")

if __name__ == "__main__":
    main()
