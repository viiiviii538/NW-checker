import re, pathlib, sys

p = pathlib.Path("coverage/lcov.info")
if not p.exists():
    print("lcov not found:", p)
    sys.exit(1)
txt = p.read_text()
lf = sum(int(m) for m in re.findall(r"^LF:(\d+)$", txt, re.M))
lh = sum(int(m) for m in re.findall(r"^LH:(\d+)$", txt, re.M))
rate = (lh / lf * 100) if lf else 0.0
print(f"line-rate={rate:.1f}%")
sys.exit(0 if rate >= 70 else 1)
