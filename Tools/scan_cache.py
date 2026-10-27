import glob, os, re, zlib

hits = []
for path in glob.glob("../Library/ShaderCache/**/*.bin", recursive=True):
    try:
        data = open(path, "rb").read()
    except OSError:
        continue
    if b"_OutlineThickness" not in data:
        continue
    # dump any printable runs, look for HLSL-ish fragments
    txt = re.findall(rb"[\x20-\x7e\r\n\t]{40,}", data)
    joined = b"\n".join(txt).decode("utf-8", "replace")
    if "surfaceDescription" in joined or "_OutlineThickness" in joined:
        hits.append((len(joined), path, joined))
print("cached files mentioning _OutlineThickness:", len(hits))
hits.sort(reverse=True)
for n, path, joined in hits[:2]:
    print("=" * 70)
    print(path, "text chars:", n)
    idx = joined.find("_OutlineThickness")
    print(joined[max(0, idx - 500):idx + 500])
