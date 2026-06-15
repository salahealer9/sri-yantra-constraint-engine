"""
Study A — random-sample landscape estimate (EXPLORATORY, off the confirmatory
track; planning only). Estimates the box-count distribution and feasible fraction
across the 815 well-posed plane subsets.

Discipline:
  * Frozen seed -> deterministic shuffle of ALL 815 subsets -> the draw is the
    prefix order[:N]. Emitted to study_a/draw.txt BEFORE any run. Extensible
    without bias: a larger sample is a longer prefix of the SAME order.
  * Purely random. No targeted/hazard subsets (that is Study B).
  * Float AA: box count is float==rounded (calibration width ratio 1.0000), so
    float box counts transfer to the rigorous campaign; float is ~1.6x faster.
  * Per-subset budget caps the search; a budget-exhausted subset is recorded as
    right-censored (done=False) and is a Study-B follow-up target, not discarded.

Usage:  python3 study_a.py <start> <end>     # runs draw[start:end], appends CSV
        python3 study_a.py summary           # prints distribution from the CSV
"""
import os, sys, csv, time, random, itertools, statistics
sys.path.insert(0, '/opt/sri-yantra-constraint-engine')
sys.path.insert(0, '.')
import numpy as np
from calib import enum, AA, Dual              # float enumerator (guarded import)

SEED=20260614
N_DEFAULT=40
RCERT=3e-3; MAXBOXES=1000000; TLIM=600

POOL=list(range(3,21))                        # 18 non-essential constraints F3..F20
DEGEN=(1,2,8,9,16)                            # the one rank-deficient plane subset
def population():
    out=[]
    for c in itertools.combinations(POOL,3):
        S=tuple(sorted((1,2)+c))
        if S!=DEGEN: out.append(S)
    return out                                # 815

def draw(n=N_DEFAULT):
    pop=population(); rng=random.Random(SEED); order=pop[:]; rng.shuffle(order)
    return order[:n], len(pop)

HERE=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.join(HERE,"study_a"); os.makedirs(OUT,exist_ok=True)
CSVP=os.path.join(OUT,"results.csv")
DRAWP=os.path.join(OUT,"draw.txt")
COLS=["idx","subset","feasible","cert","boxes","peak_queue","max_depth","secs","done"]

def emit_draw(n=N_DEFAULT):
    d,npop=draw(n)
    with open(DRAWP,"w") as f:
        f.write(f"# Study A draw — EXPLORATORY landscape sample\n")
        f.write(f"# seed={SEED}  population={npop} well-posed plane subsets  N={n}\n")
        f.write(f"# r_cert={RCERT} max_boxes={MAXBOXES} tlim={TLIM}s  box=illustrative (route3_panel.BOX)\n")
        for i,S in enumerate(d): f.write(f"{i}\t{S}\n")
    return d,npop

def run_one(args):
    i,S=args
    r=enum(list(S),AA,Dual,r_cert=RCERT,max_boxes=MAXBOXES,tlim=TLIM)
    return [i,str(S),int(r['cert']>0),r['cert'],r['boxes'],r['maxq'],r['maxd'],
            f"{r['secs']:.1f}",r['done']]

def run_range(start,end):
    d,_=emit_draw(max(end,N_DEFAULT))
    tasks=[(i,d[i]) for i in range(start,min(end,len(d)))]
    new=not os.path.exists(CSVP)
    f=open(CSVP,"a",newline=""); w=csv.writer(f)
    if new: w.writerow(COLS)
    nproc=os.cpu_count() or 1
    print(f"Study A: draw[{start}:{end}] on {nproc} core(s)  (seed={SEED})")
    if nproc>1:
        from multiprocessing import Pool
        with Pool(nproc) as p:
            for row in p.imap_unordered(run_one,tasks):
                w.writerow(row); f.flush()
                print(f"  idx={row[0]:>3} {row[1]:16s} feas={row[2]} boxes={row[4]:>7} "
                      f"q={row[5]:>4} d={row[6]:>3} {row[7]:>6}s done={row[8]}")
    else:
        for t in tasks:
            row=run_one(t); w.writerow(row); f.flush()
            print(f"  idx={row[0]:>3} {row[1]:16s} feas={row[2]} boxes={row[4]:>7} "
                  f"q={row[5]:>4} d={row[6]:>3} {row[7]:>6}s done={row[8]}")
    f.close()

def summary():
    rows=list(csv.DictReader(open(CSVP)))
    n=len(rows); boxes=sorted(int(r["boxes"]) for r in rows)
    done=[r for r in rows if r["done"]=="True"]
    cens=[r for r in rows if r["done"]!="True"]
    cfeas=[r for r in done if r["feasible"]=="1"]
    cinf =[r for r in done if r["feasible"]=="0"]
    q=[int(r["peak_queue"]) for r in rows]; dep=[int(r["max_depth"]) for r in rows]
    print(f"Study A — {n} of 815 well-posed subsets (seed {SEED}); EXPLORATORY\n")
    print(f"complete & feasible (>=1 certified figure): {len(cfeas)}/{n}")
    print(f"complete & infeasible (certified absence):  {len(cinf)}/{n}")
    print(f"right-censored (budget-exhausted):          {len(cens)}/{n}"
          + (f"  -> Study-B / re-run targets: {[r['subset'] for r in cens]}" if cens else ""))
    print(f"  (censored box counts are LOWER BOUNDS; upper tail not yet characterized)")
    print(f"\nbox count — order statistics (transfers to rigorous campaign):")
    print(f"  min {boxes[0]:>8}   median {int(statistics.median(boxes)):>8}   max {boxes[-1]:>8}")
    print(f"  five largest: {boxes[-5:][::-1]}")
    print(f"  mean {int(statistics.mean(boxes)):>8}   (CI wide at this n; order stats preferred)")
    print(f"\nmemory: peak queue max {max(q)}   max depth max {max(dep)}  (DFS-bounded)")
    tot=815*statistics.mean(boxes)
    print(f"\nextrapolation (rough, completers only): mean*815 ~ {tot/1e6:.1f}M boxes")
    print(f"  rigorous ~800 box/s -> ~{tot/800/3600:.1f} h single-core, "
          f"~{tot/800/3600/4:.1f} h on 4 cores; Julia faster.")

if __name__=="__main__":
    if not sys.argv[1:] or sys.argv[1]=="summary":
        if os.path.exists(CSVP): summary()
        else: print("no results yet; run a range first")
    else:
        run_range(int(sys.argv[1]), int(sys.argv[2]))
