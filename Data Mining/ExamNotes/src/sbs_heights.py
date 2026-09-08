import io, os, re, subprocess, sys

# Map every @SBS height typeout back to the \sbs / \sbsr call that produced it.
# The Nth @SBS line is the Nth pair set in the document, and the document sets
# them in \input order, so walk the master's inputs and count calls.
#
#   python sbs_heights.py <master-stem> [threshold-fraction-of-textheight]
#
# A pair over ~0.45 textheight is worth splitting at a \lead boundary; one over
# \sbsmax (0.78) is a hard bug and tectonic already shouts @SBS-TOO-TALL.

SRC = os.path.dirname(os.path.abspath(__file__))
stem = sys.argv[1]
cut = float(sys.argv[2]) if len(sys.argv) > 2 else 0.45

run = subprocess.run([os.environ.get('TECTONIC','./tectonic.exe'), '-X', 'compile', '--keep-logs', stem + '.tex'],
                     capture_output=True, text=True, errors='replace')
logf = stem + '.log'
blob = (run.stdout + run.stderr)
if os.path.exists(logf):
    blob += io.open(logf, encoding='utf-8', errors='replace').read()
lines = [l for l in blob.splitlines() if '@SBS ' in l]
heights = []
th = None
for l in lines:
    m = re.search(r'@SBS ([\d.]+)pt of ([\d.]+)pt', l)
    if m:
        heights.append(float(m.group(1)))
        th = float(m.group(2))
if not heights:
    print('no @SBS output -- is this the ported preamble?'); sys.exit(1)

# order of \input in the master
master = io.open(stem + '.tex', encoding='utf-8').read()
inputs = re.findall(r'\\input\{([^}]+)\}', master)
calls = []
for name in inputs:
    fn = name if name.endswith('.tex') else name + '.tex'
    if not os.path.exists(fn) or 'preamble' in fn:
        continue
    for i, line in enumerate(io.open(fn, encoding='utf-8').read().split('\n'), 1):
        for _ in re.finditer(r'\\sbsr?\{', line):
            calls.append((fn, i, line.strip()[:60]))

print('%d @SBS heights, %d \\sbs calls found, textheight %.1fpt'
      % (len(heights), len(calls), th))
if len(heights) != len(calls):
    print('COUNT MISMATCH -- report is positional, treat line numbers as approximate')

rows = []
for h, c in zip(heights, calls):
    rows.append((h / th, h, c))
rows.sort(reverse=True)
print('\npairs over %.0f%% of textheight:' % (cut * 100))
for frac, h, (fn, ln, txt) in rows:
    if frac < cut:
        break
    print('  %5.1f%%  %-12s :%-5d %s' % (frac * 100, fn, ln, txt))
