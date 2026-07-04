#!/usr/bin/env python3
"""
build_viewer_bundle.py — the bridge between the frozen engine and the viewer.
================================================================================
Walks the certified census, regenerates every distinct figure through the FROZEN
constructor, gates each one against the engine at 1e-15, and emits a static
JSON + SVG bundle. The client renders this bundle directly and does NO geometry:
the engine is the single source of truth, and the build re-certifies every vertex
before it is allowed into the bundle — it refuses to emit anything it cannot
certify, exactly like render_overdetermined_figure.py refuses to draw.

INPUT   : campaign census (roots.jsonl) — the 134 feasible certified roots.
OUTPUT  : bundle/
            manifest.json          provenance + gallery index + counts
            figures/<id>.json      root, all points, nine triangles, gate report
            figures/<id>.svg       precomputed line art (upright, styleable)
            SHA256SUMS             sha256 of every other file (verify: sha256sum -c)

PROVENANCE: every artifact is stamped with the pinned engine commit and the
dataset DOI, so the viewer's data lineage is engine -> census -> bundle, closed.
The bundle is byte-reproducible: re-running under the same engine commit yields
identical files and identical hashes (no timestamps anywhere in the output).

Run under the pinned/frozen engine, not a working copy, so the certificate is
your pipeline's:  python3 build_viewer_bundle.py --roots campaign_results/roots.jsonl
"""
import argparse
import hashlib
import json
import math
import os
import sys

# --- pinned provenance (the viewer cites these; do not edit casually) ---
ENGINE_COMMIT = "75aed90"
DATASET_DOI = "10.5281/zenodo.20708335"
GATE_TOL = 1e-15
DEDUP_TOL = 1e-9  # two roots are the same figure iff all five params agree to this
TAU_NOTE = (
    "Count is 128 distinct ROOTS (the finest, unambiguous enumeration: each root "
    "maps deterministically to one figure). Figure-equivalence under the Section 7 "
    "metric is tolerance-dependent and only approaches 128 as tau -> 0; do not "
    "label this 'the number of distinct Sri Yantras'."
)

# --- make engine + constructors importable from any checkout ---
_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra_plane.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

import sriyantra_plane as SP
from figure_coords import figure_coordinates as FC, iy
from figure_coords_inner import inner_points, validate_inner

# Rao's nine transverse arcs (apex_label, corner_label, kind).
# Five Sakti (apex below, opens up) + four Siva (apex above, opens down).
# Corners are the endpoints of the transverse sides PRODUCED to their base lines
# (Rao eqs 2.22, 2.24, 2.33, 2.43): P1->18 (base P8), P4->16 (base P9),
# P9->19 (base P2), P7->17 (base P1). Points 4,6,3,5 are interior construction
# crossings of those sides, not corners (docs/PLANE_TOPOLOGY_AUDIT.md).
TRIANGLES = [
    ("P0", "2", "sakti"), ("P1", "18", "sakti"), ("P2", "13", "sakti"),
    ("P3", "14", "sakti"), ("P4", "16", "sakti"),
    ("P10", "1", "siva"), ("P9", "19", "siva"), ("P8", "10", "siva"),
    ("P7", "17", "siva"),
]
INTERSECTION_LABELS = [str(i) for i in range(1, 15)] + ["16", "17", "18", "19"]
APEX_EXACT = ("P0", "P1", "P3", "P4", "P7", "P9", "P10")


def build_points(root):
    """FROZEN constructor output for one root, with point 14 placed as Rao defines."""
    b, c, d, e, g = root
    s = SP.chain(*root)
    P = FC(*root)
    P["14"] = tuple(iy(P["P8"], P["10"], d - s["U7"]))  # P3 arc endpoint, P8->10 at P5
    return P, s


def gate(root):
    """Certify every vertex against the frozen engine. Returns (ok, worst, rows)."""
    b, c, d, e, g = root
    P, s = build_points(root)
    rows, worst = [], 0.0
    for k in INTERSECTION_LABELS:                       # (a) 1-14,16-19 vs chain x
        r = abs(abs(P[k][0]) - abs(s["x" + k]))
        rows.append(("pt" + k, r)); worst = max(worst, r)
    vi = validate_inner(*root)                          # (b) 20,21 vs U20,U21
    for k in ("20", "21"):
        rows.append(("pt" + k, vi[k])); worst = max(worst, vi[k])
    exact = {"P0": -1.0, "P1": -(b + c), "P3": -c, "P4": -g,
             "P7": d, "P9": d + e, "P10": 1.0}           # (c) apex heights
    for k in APEX_EXACT:
        r = abs(P[k][1] - exact[k]); rows.append((k + ".y", r)); worst = max(worst, r)
    return worst <= GATE_TOL, worst, rows


def assemble_figure(fig_id, root, source_subsets, census_residual):
    """Build the JSON payload for one certified figure (math frame, y up)."""
    ok, worst, rows = gate(root)
    if not ok:
        raise RuntimeError("gate failed (worst %.2e)" % worst)
    P, _ = build_points(root)
    ip = inner_points(*root)
    mir = lambda p: [-p[0], p[1]]
    xy = lambda p: [float(p[0]), float(p[1])]

    triangles = []
    for apex, cor, kind in TRIANGLES:
        A, C = P[apex], P[cor]
        triangles.append({
            "name": "%s-%s" % (apex, cor), "kind": kind,
            "apex": apex, "corner": cor,
            "polygon": [xy(A), xy(C), mir(C)],   # apex, corner, mirror(corner)
        })
    return {
        "id": fig_id,
        "root": dict(zip("bcdeg", [float(v) for v in root])),
        "points": {k: xy(v) for k, v in P.items()},
        "triangles": triangles,
        "inner_feet": {k: xy(ip[k]) for k in ("20", "21", "P20", "P21")},
        "circumcircle": {"cx": 0.0, "cy": 0.0, "r": 1.0},
        "bindu": [0.0, 0.0],
        "gate": {"tol": GATE_TOL, "worst_residual": worst, "pass": True},
        "provenance": {
            "engine_commit": ENGINE_COMMIT, "dataset_doi": DATASET_DOI,
            "source_subsets": source_subsets, "census_residual": census_residual,
        },
    }


def to_svg(fig):
    """Precomputed, styleable SVG. Upright (screen y down => negate math y).
    No geometry in the client: every coordinate is baked in here."""
    f = lambda v: ("%.7f" % v).rstrip("0").rstrip(".")
    sx = lambda p: f(p[0]); sy = lambda p: f(-p[1])     # flip for screen
    el = []
    el.append('<circle class="circumcircle" cx="0" cy="0" r="1"/>')
    el.append('<line class="axis" x1="0" y1="-1" x2="0" y2="1"/>')
    for t in fig["triangles"]:
        pts = " ".join("%s,%s" % (sx(p), sy(p)) for p in t["polygon"])
        el.append('<polygon class="triangle %s" data-name="%s" points="%s"/>'
                   % (t["kind"], t["name"], pts))
    for k in ("20", "21"):
        p = fig["inner_feet"][k]
        el.append('<circle class="foot" data-pt="%s" cx="%s" cy="%s" r="0.012"/>'
                   % (k, sx(p), sy(p)))
        el.append('<circle class="foot" data-pt="%s" cx="%s" cy="%s" r="0.012"/>'
                   % (k, f(-p[0]), sy(p)))
    el.append('<circle class="bindu" cx="0" cy="0" r="0.016"/>')
    style = (
        "<style>"
        ".circumcircle{fill:none;stroke:var(--circle,#999);stroke-width:.006}"
        ".axis{stroke:var(--axis,#ccc);stroke-width:.004;stroke-dasharray:.03 .03}"
        ".triangle{fill:none;stroke-width:.008;stroke-linejoin:round}"
        ".triangle.sakti{stroke:var(--sakti,#1b1b1b)}"
        ".triangle.siva{stroke:var(--siva,#1b1b1b)}"
        ".foot{fill:var(--foot,crimson)}.bindu{fill:var(--bindu,#000)}"
        "</style>"
    )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1.08 -1.08 2.16 2.16" '
        'data-figure-id="%s" data-engine-commit="%s">%s%s</svg>'
        % (fig["id"], ENGINE_COMMIT, style, "".join(el))
    )


REF_OPT = [0.482391, 0.261039, 0.287454, 0.467384, 0.108463]  # Rao Table 3, plane optimum

def emit_reference_figure(outdir):
    """Rao's plane optimum (Fig. 6d) as the atlas REFERENCE figure. It satisfies
    F1 = F2 = 0 with F8, F9 > 0 (Rao eq 5.3) and is NOT a census root: no
    5-constraint subset selects it. Emitted under reference/ so the viewer can
    show it as the canonical visual reference without blurring the census."""
    fig = assemble_figure("reference-plane-optimum", REF_OPT, [], None)
    fig["provenance"]["note"] = ("Rao (1998) Table 3 'Plane optimum' (Fig. 6d): the reference "
                                 "plane Sri Yantra. F1 = F2 = 0, F8 > 0, F9 > 0. NOT a census "
                                 "root; reference for visual comparison only.")
    fig["reference"] = True
    refdir = os.path.join(outdir, "reference"); os.makedirs(refdir, exist_ok=True)
    with open(os.path.join(refdir, "plane_optimum.json"), "w") as fh:
        json.dump(fig, fh, separators=(",", ":"), sort_keys=True)
    with open(os.path.join(refdir, "plane_optimum.svg"), "w") as fh:
        fh.write(to_svg(fig))
    return fig

def load_distinct_roots(roots_path):
    """Read the census, gather feasible roots, collapse to distinct roots.
    Returns ordered list of (root, source_subsets, min_census_residual)."""
    feasible = []  # (coords, subset, residual)
    with open(roots_path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            for r in rec.get("roots", []):
                feasible.append((r["coords"], rec["subset"], r.get("engine_residual")))
    groups = {}  # rounded-key -> {coords, subsets, resid}
    for coords, subset, resid in feasible:
        key = tuple(round(float(v) / DEDUP_TOL) for v in coords)
        gobj = groups.setdefault(key, {"coords": coords, "subsets": [], "resid": []})
        gobj["subsets"].append(subset)
        if resid is not None:
            gobj["resid"].append(resid)
    distinct = []
    for gobj in groups.values():
        subsets = sorted(gobj["subsets"])
        resid = min(gobj["resid"]) if gobj["resid"] else None
        distinct.append((gobj["coords"], subsets, resid))
    # stable order: by the smallest source subset
    distinct.sort(key=lambda t: t[1][0])
    return len(feasible), distinct


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roots", default="roots.jsonl")
    ap.add_argument("--out", default="bundle")
    args = ap.parse_args()

    n_feasible, distinct = load_distinct_roots(args.roots)
    figdir = os.path.join(args.out, "figures")
    os.makedirs(figdir, exist_ok=True)

    index, failures = [], []
    for i, (root, subsets, resid) in enumerate(distinct):
        fig_id = "%03d" % i
        try:
            fig = assemble_figure(fig_id, root, subsets, resid)
        except Exception as exc:                         # refuse to emit ungated figure
            failures.append((fig_id, subsets[0], str(exc)))
            continue
        with open(os.path.join(figdir, fig_id + ".json"), "w") as fh:
            json.dump(fig, fh, separators=(",", ":"))
        with open(os.path.join(figdir, fig_id + ".svg"), "w") as fh:
            fh.write(to_svg(fig))
        index.append({
            "id": fig_id, "root": fig["root"], "source_subsets": subsets,
            "n_subsets": len(subsets), "census_residual": resid,
            "gate_residual": fig["gate"]["worst_residual"],
        })

    ref = emit_reference_figure(args.out)
    manifest = {
        "reference_figure": {
            "id": "reference-plane-optimum", "path": "reference/plane_optimum.json",
            "svg": "reference/plane_optimum.svg",
            "note": ref["provenance"]["note"]},
        "title": "Plane Sri Yantra — certified figure bundle",
        "provenance": {
            "engine_commit": ENGINE_COMMIT, "dataset_doi": DATASET_DOI,
            "gate_tolerance": GATE_TOL, "dedup_tolerance": DEDUP_TOL,
            "note": "Bundle regenerated from the frozen engine; every figure gated "
                    "at the tolerance before emission. The viewer renders this "
                    "bundle and performs no geometry of its own. No timestamps: the "
                    "output is byte-reproducible at this engine commit.",
        },
        "counts": {
            "feasible_certified_roots": n_feasible,
            "distinct_roots": len(distinct),
            "emitted": len(index), "gate_failures": len(failures),
        },
        "tau_metric_note": TAU_NOTE,
        "figures": index,
    }
    with open(os.path.join(args.out, "manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)

    print("feasible certified roots : %d" % n_feasible)
    print("distinct roots           : %d" % len(distinct))
    print("figures emitted          : %d" % len(index))
    print("gate failures            : %d" % len(failures))
    if failures:
        for fid, sub0, msg in failures[:10]:
            print("  FAIL %s (subset starts %s): %s" % (fid, sub0, msg))
        raise SystemExit("gate failures present; bundle is incomplete.")
    worst = max((row["gate_residual"] for row in index), default=0.0)
    print("worst gate residual      : %.2e  (tol %.0e)  ->  %s"
          % (worst, GATE_TOL, "ALL PASS" if worst <= GATE_TOL else "FAIL"))

    # Reproducible checksum manifest: sha256 of every file except itself, sorted by
    # path, LF endings, forward slashes -> `cd bundle && sha256sum -c SHA256SUMS`.
    sums = []
    for root_dir, _dirs, files in os.walk(args.out):
        for name in files:
            rel = os.path.relpath(os.path.join(root_dir, name), args.out).replace(os.sep, "/")
            if rel == "SHA256SUMS":
                continue
            h = hashlib.sha256()
            with open(os.path.join(root_dir, name), "rb") as fb:
                for chunk in iter(lambda: fb.read(65536), b""):
                    h.update(chunk)
            sums.append((rel, h.hexdigest()))
    sums.sort()
    sumpath = os.path.join(args.out, "SHA256SUMS")
    with open(sumpath, "w", newline="\n") as fh:
        for rel, hexd in sums:
            fh.write("%s  %s\n" % (hexd, rel))
    root = hashlib.sha256(open(sumpath, "rb").read()).hexdigest()
    print("checksummed files        : %d  ->  bundle/SHA256SUMS" % len(sums))
    print("bundle digest            : %s" % root)
    print("  (sha256 of SHA256SUMS; cite this in the release / commit)")


if __name__ == "__main__":
    main()
