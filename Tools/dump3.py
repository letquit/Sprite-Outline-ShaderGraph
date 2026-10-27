import json, sys
from sgload import load_multi

path = sys.argv[1]
docs = load_multi(path)
byid = {d.get('m_ObjectId'): d for d in docs}
root = next(d for d in docs if d.get('m_Type') == 'UnityEditor.ShaderGraph.GraphData')

def short(t):
    return (t or '?').replace('UnityEditor.ShaderGraph.', '').replace('Internal.', '')

for p in root.get('m_Properties', []):
    d = byid.get(p['m_Id'], {})
    print(f"PROP {p['m_Id']} {short(d.get('m_Type'))} name={d.get('m_Name')} ref={d.get('m_DefaultReferenceName')}")
print()

nodes = {}
for n in root.get('m_Nodes', []):
    d = byid.get(n['m_Id'], {})
    nodes[n['m_Id']] = d
    slots = d.get('m_SerializableSlots', []) or []
    print(f"NODE [{n['m_Id']}] {short(d.get('m_Type'))} name={d.get('m_Name')}")
    for s in slots:
        sd = byid.get(s.get('m_Id'), {})
        print(f"   slot id={s.get('m_Id')} disp={sd.get('m_DisplayName')!r} type={short(sd.get('m_Type'))} val={sd.get('m_Value')}")
    if d.get('m_PropertyGuidSerialized'):
        print(f"   -> property {d['m_PropertyGuidSerialized']} = {byid.get(d['m_PropertyGuidSerialized'],{}).get('m_Name')}")
print()

def slotmap(nid):
    d = nodes.get(nid, {})
    out = {}
    for s in d.get('m_SerializableSlots', []) or []:
        sd = byid.get(s.get('m_Id'), {})
        out[s.get('m_Id')] = (sd.get('m_DisplayName'), short(sd.get('m_Type')))
    return out

print("EDGES:")
for e in root.get('m_Edges', []):
    on = e['m_OutputSlot']['m_Node']['m_Id']
    os_ = e['m_OutputSlot']['m_SlotId']
    in_ = e['m_InputSlot']['m_Node']['m_Id']
    is_ = e['m_InputSlot']['m_SlotId']
    om = slotmap(on)
    im = slotmap(in_)
    print(f"  {short(nodes.get(on,{}).get('m_Type'))}[{os_}:{om.get(os_)}] -> {short(nodes.get(in_,{}).get('m_Type'))}[{is_}:{im.get(is_)}]   ({on[:6]} -> {in_[:6]})")
