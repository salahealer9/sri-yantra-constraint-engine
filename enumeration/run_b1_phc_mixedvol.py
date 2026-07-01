#!/usr/bin/env python3
"""
run_b1_phc_mixedvol.py — Route B1 via the standalone `phc` binary (no phcpy/pip needed).

Builds a PHCpack input system on the committed supports (generic integer coeffs; mixed volume
depends only on the Newton polytopes), runs `phc -m` (MixedVol/DEMiCs mixed-volume mode) in a
separate process under a wall-clock timeout, parses the mixed volume from phc's output, and
writes docs/b1_mixed_volume_result.json with full provenance. Never raises: every outcome ->
recorded status (integer | BACKEND_OVERFLOW | BACKEND_FAIL | TIMEOUT | PHC_NOT_FOUND | INPUT_MISSING).

Usage (from repo root), after placing the `phc` binary somewhere on PATH or in lift/:
    python3 enumeration/run_b1_phc_mixedvol.py
Env: PHC=/path/to/phc  (else searches PATH, lift/phc, ./phc)   B1_TIMEOUT=7200
NO infeasibility claim; measures the full-lift path count only.
"""
import os, sys, json, hashlib, time, platform, datetime, subprocess, shutil, re, random

_here=os.path.dirname(os.path.abspath(__file__)); _root=_here
while _root!=os.path.dirname(_root):
    if os.path.isdir(os.path.join(_root,'lift')) or os.path.exists(os.path.join(_root,'sriyantra.py')): break
    _root=os.path.dirname(_root)
INPUTS=[os.path.join(_root,'lift','lift_123467_supports.json'),
        os.path.join(_root,'docs','lift_123467_supports.json'),
        os.path.join(_root,'lift_123467_supports.json')]
OUT_DIR=os.path.join(_root,'docs'); os.makedirs(OUT_DIR, exist_ok=True)
OUT=os.path.join(OUT_DIR,'b1_mixed_volume_result.json')
TIMEOUT=int(os.environ.get('B1_TIMEOUT','7200'))

def find_phc():
    p=os.environ.get('PHC')
    if p and os.path.exists(p): return p
    for c in [shutil.which('phc'), os.path.join(_root,'lift','phc'), os.path.join(_root,'phc'), './phc']:
        if c and os.path.exists(c): return c
    return None

def find_input():
    for p in INPUTS:
        if os.path.exists(p): return p
    return None

def build_phc_system(supports, n_vars, seed=20260630):
    """PHCpack format: first line = #equations; each poly ends with ';'. Generic int coeffs."""
    random.seed(seed)
    vars=['x%d'%i for i in range(n_vars)]
    lines=[str(len(supports))]
    for sup in supports:
        terms=[]
        for mon in sup:
            c=random.randint(2,97)
            fac=[ (vars[i]+('^%d'%e if e>1 else '')) for i,e in enumerate(mon) if e>0 ]
            terms.append(('+%d'%c)+('*'+'*'.join(fac) if fac else ''))
        poly=''.join(terms).lstrip('+')
        lines.append(poly+';')
    return '\n'.join(lines)+'\n'

# phc -m mixed-volume reported lines vary by version; match the common phrasings.
MV_PATTERNS=[
    re.compile(r'mixed volume\s*(?:of the system)?\s*[:=]?\s*([0-9]+)', re.I),
    re.compile(r'the mixed volume\s*(?:equals|is)?\s*[:=]?\s*([0-9]+)', re.I),
    re.compile(r'\bmixed[-\s]?volume\b[^0-9]{0,40}([0-9]+)', re.I),
]
ERROR_MARKERS=['unhandled exception','io_exceptions','end_error','invalid alternative',
               'raised ','constraint_error','data_error','program_error','storage_error']
def parse_mv(text):
    low=text.lower()
    # HARD FAIL: if phc reported any error/menu-rejection, no number is trustworthy
    if any(mk in low for mk in ERROR_MARKERS):
        return None
    cand=[]
    for pat in MV_PATTERNS:
        for m in pat.finditer(text): cand.append(int(m.group(1)))
    return cand[-1] if cand else None

def run():
    rec=dict(schema_version='b1_mixed_volume_v1', route='B1_full_support_exact_mixed_volume',
             subset=[1,2,3,4,6,7], ROUTE_B1_FULL_SUPPORT_EXACT_MV=None,
             backend='PHCpack phc -m (MixedVol/DEMiCs)', backend_version=None,
             input_path=None, input_supports_sha256=None, n_vars=None, n_eqs=None, total_monomials=None,
             wall_time_seconds=None, workers=1, timeout_seconds=TIMEOUT, memory_peak_kb=None,
             python_version=platform.python_version(), platform=platform.platform(),
             timestamp_start=datetime.datetime.now(datetime.timezone.utc).isoformat(),
             timestamp_end=None, command=' '.join(sys.argv),
             phc_path=None, phc_stdout_tail=None,
             notes='', claim='NONE (no infeasibility); B1 measures the full-lift path count only')
    def finish(status, **kw):
        rec['ROUTE_B1_FULL_SUPPORT_EXACT_MV']=status; rec.update(kw)
        rec['timestamp_end']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        json.dump(rec, open(OUT,'w'), indent=2)
        print('ROUTE_B1_FULL_SUPPORT_EXACT_MV = %s'%status); print('result -> %s'%OUT); return rec

    ip=find_input()
    if ip is None: return finish('INPUT_MISSING', notes='supports json not found: '+str(INPUTS))
    rec['input_path']=ip; rec['input_supports_sha256']=hashlib.sha256(open(ip,'rb').read()).hexdigest()
    d=json.load(open(ip)); rec['n_vars']=d['n_vars']; rec['n_eqs']=d['n_eqs']; rec['total_monomials']=d.get('total_monomials')

    phc=find_phc()
    if phc is None:
        return finish('PHC_NOT_FOUND', notes='set PHC=/path/to/phc or place binary at lift/phc. '
                      'Download Linux x86_64phc from github.com/janverschelde/PHCpack releases.')
    rec['phc_path']=phc
    try:
        v=subprocess.run([phc,'--version'],capture_output=True,text=True,timeout=30)
        rec['backend_version']=(v.stdout or v.stderr).strip()[:120]
    except Exception: pass

    sysfile=os.path.join(OUT_DIR,'b1_phc_input.txt'); outfile=os.path.join(OUT_DIR,'b1_phc_output.txt')
    open(sysfile,'w').write(build_phc_system(d['supports'], d['n_vars']))
    for f in (outfile,):
        if os.path.exists(f): os.remove(f)
    # phc -m is interactive: feed system file + output file, then menu choices via stdin.
    # Common driver: `phc -m infile outfile` with stdin answering the mixed-volume menu.
    # We try the non-interactive form first; if the menu still prompts, stdin newlines accept defaults.
    t0=time.time(); status=None; mv=None; tail=''
    try:
        proc=subprocess.run([phc,'-m',sysfile,outfile], input='5\nn\nn\nn\nn\nn\n'+'\n'*20,
                            capture_output=True, text=True, timeout=TIMEOUT)
        combined=(open(outfile).read() if os.path.exists(outfile) else '')+'\n'+proc.stdout+'\n'+proc.stderr
        tail=combined[-1500:]
        low=combined.lower()
        if 'overflow' in low or 'int32' in low or 'inexact' in low or 'range_error' in low:
            status='BACKEND_OVERFLOW'
        elif any(mk in low for mk in ERROR_MARKERS):
            status='BACKEND_FAIL'   # menu not driven correctly / phc raised -- NOT a number
        else:
            mv=parse_mv(combined)
            if mv is not None:
                status=mv
            elif 'dynamic enumeration for all mixed cells' in low and 'mixed volume' not in low:
                status='NONTERMINATING_OR_INTERRUPTED'  # DEMiCs started, no MV written
            else:
                status='BACKEND_FAIL'
    except subprocess.TimeoutExpired:
        status='TIMEOUT'; tail='exceeded %ds (set B1_TIMEOUT to extend)'%TIMEOUT
    except Exception as e:
        status='BACKEND_FAIL'; tail=repr(e)
    rec['wall_time_seconds']=round(time.time()-t0,2); rec['phc_stdout_tail']=tail; rec['phc_menu_sequence']='5,n,n,n,n,n (DEMiCs; ordinary MV; no monitor; no homotopy solve)'
    try:
        import resource; rec['memory_peak_kb']=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    except Exception: pass
    note = ('mixed volume parsed' if isinstance(status,int)
            else 'see phc_stdout_tail; if a menu prompt is shown, run `%s -m %s %s` interactively '
                 'and choose the mixed-volume (MixedVol/DEMiCs) option'%(phc,sysfile,outfile))
    return finish(status, notes=note)

if __name__=='__main__':
    run()
