from sgload import load_multi

docs = load_multi("../Backup/PixelOutline.patched.shadergraph")
byid = {d.get('m_ObjectId'): d for d in docs}
root = next(d for d in docs if d.get('m_Type', '').endswith('GraphData'))


def label(nid):
    n = byid.get(nid) or {}
    return n.get('m_Type', '?').split('.')[-1] + ':' + str(n.get('m_Name'))


focus = ['b5e1a600fb204152950b9e7eedf6c33e', '94e7ddf686c64db3bf73c6fc3a10d08a',
         '45b926e5', '30ce3c65', '380348ca', 'f7fe5192afdd45c79a5d7c02ca4d4ffe']

for nid in focus:
    n = next((d for d in docs if d.get('m_ObjectId', '').startswith(nid[:8])), None)
    if not n:
        print(nid, 'MISSING')
        continue
    print('==', n['m_ObjectId'][:8], n['m_Type'].split('.')[-1], n.get('m_Name'))
    for k in ('m_ComparisonType', 'm_KeywordType', 'm_DefaultType', 'm_OverrideReferenceName', 'm_SamplerState'):
        if k in n:
            print('   ', k, '=', n[k])
    for s in n.get('m_Slots', []):
        sd = byid[s['m_Id']]
        extra = {k: v for k, v in sd.items() if k not in ('m_ObjectId', 'm_Id', 'm_DisplayName', 'm_SlotType') and v not in (None, [])}
        print('    slot', sd['m_Id'], sd['m_DisplayName'], 'inslot=' if sd['m_SlotType'] == 0 else 'out', '->', extra)

print('--- edges (selected)')
for e in root['m_Edges']:
    o = e['m_OutputSlot']['m_Node']['m_Id']
    i = e['m_InputSlot']['m_Node']['m_Id']
    if o[:8] in ('b5e1a600', '94e7ddf6', '45b926e5', '30ce3c65', '380348ca', 'f7fe5192') \
       or i[:8] in ('b5e1a600', '94e7ddf6', '45b926e5', '94e7ddf6', '30ce3c65'):
        print('   ', label(o), e['m_OutputSlot']['m_SlotId'], '->', label(i), e['m_InputSlot']['m_SlotId'])
