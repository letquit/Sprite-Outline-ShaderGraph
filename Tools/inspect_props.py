from sgload import load_multi
from collections import Counter

docs = load_multi("../Backup/PixelOutline.patched.shadergraph")
byid = {d.get('m_ObjectId'): d for d in docs}
root = next(d for d in docs if d.get('m_Type', '').endswith('GraphData'))

print(Counter(d.get('m_Type') for d in docs if 'ShaderProperty' in str(d.get('m_Type')) or 'Keyword' in str(d.get('m_Type'))))
for d in docs:
    t = d.get('m_Type', '')
    if 'Property' in t or 'Keyword' in t:
        print(t.split('.')[-1], '| name=', d.get('m_Name'), '| ref=', d.get('m_OverrideReferenceName'),
              '| defref=', d.get('m_DefaultReferenceName'), '| type=', d.get('m_KeywordType'),
              '| val=', d.get('m_Value'), '| default=', d.get('m_DefaultValue'))

print('\n== PropertyNodes and their targets')
pnodes = {d['m_ObjectId']: d for d in docs if d.get('m_Type', '').endswith('PropertyNode')}
for nid, pn in pnodes.items():
    prop = pn.get('m_Property', {}).get('m_Id') if isinstance(pn.get('m_Property'), dict) else pn.get('m_Property')
    pname = byid.get(prop, {}).get('m_Name') if prop in byid else prop
    outs = [s['m_Id'] for s in pn['m_Slots'] if byid[s['m_Id']]['m_SlotType'] == 1]
    for e in root['m_Edges']:
        if e['m_OutputSlot']['m_Node']['m_Id'] == nid:
            tgt = byid.get(e['m_InputSlot']['m_Node']['m_Id'], {})
            print(f"  {pname!r:22} slot{e['m_OutputSlot']['m_SlotId']} -> {tgt.get('m_Type','?').split('.')[-1]} "
                  f"'{tgt.get('m_Name')}' slot{e['m_InputSlot']['m_SlotId']}")

print('\n== SubGraphNodes (instances) and DIrection literals')
for nid, n in [(d['m_ObjectId'], d) for d in docs if d.get('m_Type', '').endswith('SubGraphNode')]:
    ins = []
    for s in n['m_Slots']:
        sd = byid[s['m_Id']]
        if sd['m_SlotType'] == 0:
            ins.append((sd['m_Id'], sd['m_DisplayName'], sd.get('m_Value')))
    print('  ', nid[:8], n.get('m_SubGraphName') or n.get('m_SubGraphGuid', '')[:8], ins)
