import json, sys
from sgload import load_multi

path = sys.argv[1]
docs = load_multi(path)
byid = {}
for d in docs:
    byid[d.get('m_ObjectId')] = d

root = next(d for d in docs if d.get('m_Type') == 'UnityEditor.ShaderGraph.GraphData')
print("GRAPH keys:", list(root.keys()))
print()
print("NODES listed:", [n.get('m_Id') for n in root.get('m_Nodes', [])])
print("EDGES raw:", json.dumps(root.get('m_Edges'))[:2000])
print("PROPS listed:", [n.get('m_Id') for n in root.get('m_Properties', [])])
print()

def short(t):
    return t.replace('UnityEditor.ShaderGraph.', '').replace('Internal.', '')

print("=== PROPERTIES")
for p in root.get('m_Properties', []):
    d = byid.get(p['m_Id'], {})
    print(f"  {p['m_Id']}  {short(d.get('m_Type','?'))}  name={d.get('m_Name')}  display={d.get('m_DisplayName')}  default={d.get('m_DefaultReferenceName')} overrideRef={d.get('m_OverrideReferenceName')}")
    for k in ('m_Value','m_DefaultValue','m_GeneratePropertyBlock','m_Exposed','m_FloatType'):
        if k in d: print(f"      {k}={d[k]}")
print()

print("=== NODES")
for n in root.get('m_Nodes', []):
    d = byid.get(n['m_Id'], {})
    pos = d.get('m_DrawState', {}) or {}
    gp = pos.get('m_Position', {}) or {}
    print(f"[{n['m_Id']}] {short(d.get('m_Type','?'))}  name={d.get('m_Name')}  pos=({gp.get('x')},{gp.get('y')})")
    if d.get('m_FunctionName'):
        print(f"    functionName={d.get('m_FunctionName')} src={d.get('m_FunctionSource')} subgraphId={d.get('m_SubGraphGuid')}")
    for sk in ('m_PropertyGuidSerialized','m_SourceType','m_TextureType','m_PreviewExpanded'):
        if sk in d and d[sk] not in (None, False, ''):
            print(f"    {sk}={d[sk]}")
    for s in d.get('m_SerializableSlots', []) or []:
        sid = s.get('m_Id')
        sd = byid.get(sid, {})
        val = sd.get('m_Value')
        print(f"    slot id={sd.get('m_Id')} disp={sd.get('m_DisplayName')!r} type={short(sd.get('m_Type','?'))} def={sd.get('m_DefaultValue')} value={val}")
print()

print("=== EDGES (full)")
for e in root.get('m_Edges', []):
    print(json.dumps(e))
