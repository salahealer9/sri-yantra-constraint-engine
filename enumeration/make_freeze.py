#!/usr/bin/env python3
"""
make_freeze.py — emit the Tier-2 confirmatory tooling freeze manifest (Amendment-02 §B8).

Deterministic record of the exact tree the official Gate M and the campaign run
against: SHA-256 of each frozen file, the git commit, the environment, and the
frozen parameters. RUN ON THE SERVER where the campaign will execute (it records
*that* machine's Python/package versions), after all frozen files are committed.

Output: prereg/tier2-freeze.sha256   (header comments + sha256sum-format lines).
Then GPG-sign + OpenTimestamps-stamp + commit + tag, predating any confirmatory run.

Verify the file hashes any time with:
    grep -v '^#' prereg/tier2-freeze.sha256 | sha256sum -c -      # run from repo root
"""
import os, sys, hashlib, subprocess, platform, datetime

FROZEN = [
    "enumeration/generate_B.py",
    "enumeration/B.json",
    "enumeration/campaign.py",
    "enumeration/admissibility.py",
    "enumeration/aar.py",
    "enumeration/plane_chain.py",
    "enumeration/gate_m.py",
    "sriyantra_plane.py",            # engine under test (v0.1.0); adjust if at another path
]

def repo_root():
    try:
        return subprocess.check_output(["git", "rev-parse", "--show-toplevel"],
                                       text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def git(root, *args):
    try:
        return subprocess.check_output(["git", "-C", root, *args],
                                       text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unknown"

def pkgver(name):
    try:
        return getattr(__import__(name), "__version__", "unknown")
    except Exception:
        return "absent"

def main():
    root = repo_root()
    # refuse to freeze a dirty tree or untracked frozen files
    status = git(root, "status", "--porcelain")
    head   = git(root, "rev-parse", "HEAD")
    branch = git(root, "rev-parse", "--abbrev-ref", "HEAD")
    tracked = set(git(root, "ls-files").splitlines())
    missing = [f for f in FROZEN if not os.path.exists(os.path.join(root, f))]
    untracked = [f for f in FROZEN if f not in tracked]
    if missing:
        sys.exit(f"ABORT: frozen file(s) absent: {missing}")
    if untracked:
        sys.exit(f"ABORT: frozen file(s) not committed: {untracked}")
    if status:
        sys.exit("ABORT: working tree not clean — commit or stash before freezing:\n" + status)

    # frozen parameters, read from the frozen tool itself
    sys.path.insert(0, os.path.join(root, "enumeration")); sys.path.insert(0, root)
    import campaign, admissibility
    params = (f"R_CERT={campaign.R_CERT} MAX_DEPTH={campaign.MAX_DEPTH} "
              f"MAX_BOXES={campaign.MAX_BOXES} TLIM={campaign.TLIM} RMAX={admissibility.RMAX} "
              f"GATE2_TOL={campaign.GATE2_TOL} DEDUP_TOL={campaign.DEDUP_TOL} "
              f"BISECTION={campaign.BISECTION} POLISH={campaign.POLISH}")

    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    header = [
        "# Tier-2 confirmatory tooling freeze — Amendment-02 §B8 (pre-registration v1.4)",
        f"# frozen (UTC):     {ts}",
        f"# git branch/HEAD:  {branch} / {head}",
        f"# python:           {platform.python_version()} ({platform.platform()})",
        f"# numpy {pkgver('numpy')}  scipy {pkgver('scipy')}  mpmath {pkgver('mpmath')}",
        f"# frozen params:    {params}",
        "# box:              enumeration/B.json (B_plane; generate_B.py from Rao Table 3)",
        "# verify:           grep -v '^#' prereg/tier2-freeze.sha256 | sha256sum -c -   (from repo root)",
        "#",
    ]
    hashes = [f"{sha256(os.path.join(root, f))}  {f}" for f in FROZEN]

    out = os.path.join(root, "prereg", "tier2-freeze.sha256")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as fh:
        fh.write("\n".join(header) + "\n" + "\n".join(hashes) + "\n")
    print("wrote", out, "\n")
    print("\n".join(header)); print("\n".join(hashes))

if __name__ == "__main__":
    main()
