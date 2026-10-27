import json, sys, os, uuid, shutil
from sgload import load_multi

SRC = os.path.join('..', 'Assets', 'Shader', 'PixelOutline.shadergraph')
STAGED = os.path.join('..', 'Backup', 'PixelOutline.patched.shadergraph')

txt = open(SRC, encoding='utf-8-sig').read()
dec = json.JSONDecoder()
docs, i = [], 0
while i < len(txt):
    while i < len(txt) and txt[i] in ' \r\n\t':
        i += 1
    if i >= len(txt):
        break
    obj, i = dec.raw_decode(txt, i)
    docs.append(obj)

byid = {d.get('m_ObjectId'): d for d in docs}
root = next(d for d in docs if d.get('m_Type') == 'UnityEditor.ShaderGraph.GraphData')

ALPHA_BLOCK = '3dbc47f8fef0412f9eb6791f18171f4f'   # SurfaceDescription.Alpha
SAMPLE_A    = 'f7fe5192afdd45c79a5d7c02ca4d4ffe'   # Sample Texture 2D (Main Texture)
SATURATE    = '30ce3c6521cd456c8eeb396d0b82b1db'   # Saturate(mask)
CLONE_ADD   = '198776ae7d6b4390894203710ec1b1b6'   # Add node used as schema template

for nid in (ALPHA_BLOCK, SAMPLE_A, SATURATE, CLONE_ADD):
    assert nid in byid, nid

if any(e['m_InputSlot']['m_Node']['m_Id'] == ALPHA_BLOCK for e in root['m_Edges']):
    print("Alpha block already connected — nothing to do.")
    sys.exit(0)

tpl = byid[CLONE_ADD]
tpl_slots = [byid[s['m_Id']] for s in tpl['m_Slots']]
print("template slots:", [(s['m_Id'], s['m_DisplayName'], s['m_SlotType']) for s in tpl_slots])
assert [(s['m_Id'], s['m_DisplayName']) for s in tpl_slots] == [(0, 'A'), (1, 'B'), (2, 'Out')], "unexpected Add slot layout"

new_node_id = uuid.uuid4().hex
slot_ids = [uuid.uuid4().hex for _ in range(3)]

node = json.loads(json.dumps(tpl))
node['m_ObjectId'] = new_node_id
node['m_Type'] = 'UnityEditor.ShaderGraph.MaximumNode'
node['m_Name'] = 'Maximum'
node['m_DrawState']['m_Position']['x'] = -1050.0
node['m_DrawState']['m_Position']['y'] = 1080.0
node['synonyms'] = ['largest', 'max']
node['m_Slots'] = [{'m_Id': s} for s in slot_ids]

slot_docs = []
for k, sid in enumerate(slot_ids):
    sd = json.loads(json.dumps(tpl_slots[k]))
    sd['m_ObjectId'] = sid
    slot_docs.append(sd)

def edge(from_node, from_slot, to_node, to_slot):
    return {'m_OutputSlot': {'m_Node': {'m_Id': from_node}, 'm_SlotId': from_slot},
            'm_InputSlot':  {'m_Node': {'m_Id': to_node},   'm_SlotId': to_slot}}

root['m_Edges'].extend([
    edge(SAMPLE_A, 7, new_node_id, 0),      # sampled texture alpha -> A
    edge(SATURATE, 1, new_node_id, 1),      # outline mask         -> B
    edge(new_node_id, 2, ALPHA_BLOCK, 0),   # max(a, mask)         -> SurfaceDescription.Alpha
])
root['m_Nodes'].append({'m_Id': new_node_id})
docs.extend(slot_docs)
docs.append(node)

for d in docs:
    if d.get('m_Type') == 'UnityEditor.ShaderGraph.Internal.Vector1ShaderProperty' \
       and d.get('m_Name') == 'Outline Thickness':
        d['m_Value'] = 1.0

# ---- validate: every edge endpoint must resolve to a real node + slot
nodes = {d['m_ObjectId']: d for d in docs}
for e in root['m_Edges']:
    for side in ('m_OutputSlot', 'm_InputSlot'):
        nid, sid = e[side]['m_Node']['m_Id'], e[side]['m_SlotId']
        assert nid in nodes, f"dangling node {nid}"
        have = [nodes[s['m_Id']].get('m_Id') for s in nodes[nid]['m_Slots']]
        assert sid in have, f"slot {sid} missing on {nodes[nid]['m_Type']} ({have})"

body = "\n\n".join(json.dumps(d, indent=4, ensure_ascii=False) for d in docs) + "\n"
open(STAGED, 'w', encoding='utf-8', newline='\n').write(body)
print(f"staged {len(docs)} documents, {len(body)} bytes -> {os.path.normpath(STAGED)}")
print(f"new MaximumNode id = {new_node_id}")
