import json, sys
from sgload import load_multi

path = sys.argv[1]
docs = load_multi(path)
byid = {d.get('m_ObjectId'): d for d in docs}
root = next(d for d in docs if d.get('m_Type') == 'UnityEditor.ShaderGraph.GraphData')

def short(t):
    return (t or '?').replace('UnityEditor.ShaderGraph.', '').replace('Internal.', '')

print("PROPERTIES")
for p in root.get('m_Properties', []):
    d = byid.get(p['m_Id'], {})
    print(f"  {p['m_Id'][:8]} {short(d.get('m_Type')):26s} name={d.get('m_Name')!r} ref={d.get('m_DefaultReferenceName')} value={d.get('m_Value')}")
for k in root.get('m_Keywords', []):
    d = byid.get(k['m_Id'], {})
    print(f"  KEYWORD {k['m_Id'][:8]} {short(d.get('m_Type'))} name={d.get('m_Name')!r} display={d.get('m_DisplayName')} entries={d.get('m_Entries')} default={d.get('m_DefaultValue')}")
print()

nodes = {}
for n in root.get('m_Nodes', []):
    d = byid.get(n['m_Id'], {})
    nodes[n['m_Id']] = d

def slot(nid, sid):
    d = nodes.get(nid, {})
    for s in d.get('m_Slots', []) or []:
        sd = byid.get(s.get('m_Id'), {})
        if sd.get('m_Id') == sid:
            return sd
    return {}

def slotname(nid, sid):
    s = slot(nid, sid)
    return f"{sid}:{s.get('m_DisplayName')}"

ids = {nid: short(nodes[nid].get('m_Type')) + '/' + str(nodes[nid].get('m_Name')) for nid in nodes}

print("NODES + SLOTS")
for nid, d in nodes.items():
    extra = ''
    if d.get('m_PropertyGuidSerialized'):
        pd = byid.get(d['m_PropertyGuidSerialized'], {})
        extra = f"  PROPERTY={pd.get('m_Name')}"
    print(f"\n[{nid[:8]}] {short(d.get('m_Type'))} '{d.get('m_Name')}'{extra}")
    for k in ('m_ComparisonType', 'm_KeywordGuid', 'm_SubGraphGuid', 'm_TextureType', 'm_SourceType'):
        if k in d:
            print(f"     {k} = {d[k]}")
    if d.get('m_Keyword'):
        kd = byid.get(d['m_Keyword'].get('m_Id'), {})
        print(f"     keyword = {kd.get('m_Name')} display={kd.get('m_DisplayName')} entries={kd.get('m_Entries')}")
    for s in d.get('m_Slots', []) or []:
        sd = byid.get(s.get('m_Id'), {})
        t = sd.get('m_SlotType')
        arrow = 'IN ' if t == 0 else 'OUT'
        val = sd.get('m_Value')
        print(f"     {arrow} {sd.get('m_Id'):>12} {str(sd.get('m_DisplayName')):22s} {short(sd.get('m_Type')):24s} val={val}")

print("\nEDGES")
for e in root.get('m_Edges', []):
    on = e['m_OutputSlot']['m_Node']['m_Id']
    o = e['m_OutputSlot']['m_SlotId']
    i_ = e['m_InputSlot']['m_Node']['m_Id']
    s = e['m_InputSlot']['m_SlotId']
    print(f"  {ids.get(on)} [{slotname(on,o)}]  ==>  {ids.get(i_)} [{slotname(i_,s)}]")
