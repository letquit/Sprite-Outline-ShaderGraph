import json, shutil, uuid
from sgload import load_multi

MAIN = "../Assets/Shader/PixelOutline.shadergraph"
SUB  = "../Assets/Shader/OutlineSample.shadersubgraph"
MAT  = "../Assets/Shader/Shader Graphs_PixelOutline.mat"
THICKNESS = 3.0
DIR_SLOT = -1910666526

def save(path, docs):
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(json.dumps(d, indent=4, ensure_ascii=False) for d in docs) + "\n")

main = load_multi(MAIN)
sub  = load_multi(SUB)
subdocs = {d['m_ObjectId']: d for d in sub}
mb = {d['m_ObjectId']: d for d in main}

v2_tpl = next(d for d in sub if str(d.get('m_Type','')).endswith('Vector2Node'))
tpl_slots = [subdocs[s['m_Id']] for s in v2_tpl['m_Slots']]
assert [(s['m_Id'], s['m_DisplayName'], s['m_SlotType']) for s in tpl_slots] == [(1,'X',0),(2,'Y',0),(0,'Out',1)]

added = []
for doc in main:
    if not str(doc.get('m_Type','')).endswith('SubGraphNode'):
        continue
    sg_id = doc['m_ObjectId']
    slots = {mb[s['m_Id']]['m_Id']: mb[s['m_Id']] for s in doc['m_Slots']}
    dslot = slots[DIR_SLOT]
    v = dslot.get('m_Value') or {}
    dx, dy = float(v.get('x', 0.0)), float(v.get('y', 0.0))

    if any(e['m_InputSlot']['m_Node']['m_Id'] == sg_id and e['m_InputSlot']['m_SlotId'] == DIR_SLOT
           for e in main[0]['m_Edges']):
        print('already wired:', sg_id[:8]); continue

    nid = uuid.uuid4().hex
    pos = doc['m_DrawState']['m_Position']
    node = {
        "m_SGVersion": v2_tpl.get('m_SGVersion'),
        "m_Type": v2_tpl['m_Type'],
        "m_ObjectId": nid,
        "m_Group": {"m_Id": doc.get('m_Group', {}).get('m_Id', '')},
        "m_Name": "",
        "m_DrawState": {"m_Expanded": True,
                        "m_Position": {"serializedVersion": "2", "x": pos['x'] - 300.0,
                                       "y": pos['y'], "width": 128.0, "height": 100.99996948242188}},
        "m_Slots": [],
        "synonyms": list(v2_tpl.get('synonyms', [])),
        "m_Precision": v2_tpl.get('m_Precision', 0),
        "m_PreviewExpanded": False,
        "m_DismissedVersion": v2_tpl.get('m_DismissedVersion', 0),
        "m_PreviewMode": v2_tpl.get('m_PreviewMode', 0),
        "m_CustomColors": {"m_SerializableColors": []},
        "m_Value": {"x": dx, "y": dy},
    }
    new_slots = []
    for t in tpl_slots:
        s = json.loads(json.dumps(t))
        s['m_ObjectId'] = uuid.uuid4().hex
        if s['m_DisplayName'] == 'X':   s['m_Value'] = dx
        if s['m_DisplayName'] == 'Y':   s['m_Value'] = dy
        if s['m_DisplayName'] == 'Out': s['m_Value'] = {"x": dx, "y": dy}
        main.append(s); new_slots.append({"m_Id": s['m_ObjectId']})
        if s['m_SlotType'] == 1: out_slot_id = s['m_Id']
    node['m_Slots'] = new_slots
    main.append(node)
    main[0]['m_Nodes'].append({"m_Id": nid})

    main[0]['m_Edges'].append({
        "m_OutputSlot": {"m_Node": {"m_Id": nid}, "m_SlotId": out_slot_id},
        "m_InputSlot":  {"m_Node": {"m_Id": sg_id}, "m_SlotId": DIR_SLOT},
    })
    added.append((sg_id[:8], dx, dy))

print("wired directions:", len(added))
for a in added: print("   ", a)

for d in main:
    if d.get('m_Name') == 'Outline Thickness' and 'm_Value' in d:
        print('thickness default', d['m_Value'], '->', THICKNESS)
        d['m_Value'] = THICKNESS

shutil.copyfile(MAIN, "../Backup/PixelOutline.shadergraph.bak2")
save(MAIN, main)

mat = open(MAT, encoding='utf-8').read()
if '_OutlineThickness: 1' in mat:
    open(MAT, 'w', encoding='utf-8', newline='').write(mat.replace('_OutlineThickness: 1', '_OutlineThickness: 3'))
    print('material _OutlineThickness -> 3')

print('nodes', len(main[0]['m_Nodes']), 'edges', len(main[0]['m_Edges']), 'docs', len(main))
