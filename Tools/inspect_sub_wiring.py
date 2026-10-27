"""Trace the subgraph's own wiring: what feeds SampleTexture2D.UV and what feeds the
SubGraphOutput slot -- this decides whether the DIrection/OutlineThickness inputs are
actually used, or whether the graph samples the same texel 8 times."""
from sgload import load_multi

sub = load_multi("../Assets/Shader/OutlineSample.shadersubgraph")
byid = {d.get('m_ObjectId'): d for d in sub}
root = next(d for d in sub if d.get('m_Type', '').endswith('GraphData'))


def label(nid):
    n = byid.get(nid, {})
    t = str(n.get('m_Type', '')).split('.')[-1]
    extra = ''
    if t == 'PropertyNode':
        p = n.get('m_Property', {}).get('m_Id')
        extra = ' -> property ' + str(byid.get(p, {}).get('m_Name'))
    return f"{t}/{n.get('m_Name')}{extra}"


for e in root['m_Edges']:
    o, i = e['m_OutputSlot'], e['m_InputSlot']
    osd = byid[o['m_Node']['m_Id']]
    isd = byid[i['m_Node']['m_Id']]
    oslot = byid[[s['m_Id'] for s in osd['m_Slots']][0]] if False else None
    print(f"{label(o['m_Node']['m_Id']):55s} [slot {o['m_SlotId']}] --> {label(i['m_Node']['m_Id'])} [slot {i['m_SlotId']}]")

print("\noutput node slots:")
for n in sub:
    if str(n.get('m_Type', '')).endswith('SubGraphOutputNode'):
        for s in n['m_Slots']:
            sd = byid[s['m_Id']]
            print('   slot', sd['m_Id'], repr(sd['m_DisplayName']), sd['m_SlotType'])
