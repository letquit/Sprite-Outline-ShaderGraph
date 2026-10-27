import json, sys
from sgload import load_multi

path = sys.argv[1]
want = sys.argv[2].split(',')
docs = load_multi(path)
byid = {d.get('m_ObjectId'): d for d in docs}

for w in want:
    matches = [d for d in docs if d.get('m_ObjectId', '').startswith(w)]
    for d in matches:
        print("="*70)
        print(json.dumps(d, indent=1, ensure_ascii=False))
