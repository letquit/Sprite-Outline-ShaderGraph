import json, sys, itertools

path = sys.argv[1]
data = json.load(open(path, encoding='utf-8'))

nodes = data.get('m_SerializableNodes', [])
edges = data.get('m_SerializableEdges', [])

print("=== GRAPH:", path)
print("nodes:", len(nodes), "edges:", len(edges))
for k in data:
    if k not in ('m_SerializableNodes', 'm_SerializableEdges'):
        v = data[k]
        if not isinstance(v, (dict, list)):
            print("  ", k, "=", v)

# map node id -> index
id2idx = {}
for i, n in enumerate(nodes):
    id2idx[n.get('m_GuidSerialized')] = i

def node_label(n):
    # custom function name
    fn = n.get('m_FunctionName')
    typ = n.get('m_Type')
    name = n.get('m_Name')
    return f"{typ} | {name} | {fn}"

print("\n=== NODES")
for i, n in enumerate(nodes):
    print(f"[{i}] {n.get('m_GuidSerialized')}")
    print(f"     type={n.get('m_Type')}  name={n.get('m_Name')}")
    if n.get('m_FunctionName'):
        print(f"     funcName={n.get('m_FunctionName')}  source={n.get('m_FunctionSource')}")
    print(f"     pos=({n.get('m_DrawState',{}).get('m_Position',{}).get('x')},{n.get('m_DrawState',{}).get('m_Position',{}).get('y')})")
    if n.get('m_SerializableSlots'):
        for s in n['m_SerializableSlots']:
            print(f"       slot {s.get('m_Id')} {s.get('m_DisplayName')} dir={s.get('m_ValueType')} eid={s.get('m_GuidSerialized')}")

print("\n=== EDGES")
for e in edges:
    oi = id2idx.get(e.get('m_OutputSlot', {}).get('m_NodeGUIDSerialized'))
    ii = id2idx.get(e.get('m_InputSlot', {}).get('m_NodeGUIDSerialized'))
    oslot = e.get('m_OutputSlot', {}).get('m_SlotId')
    islot = e.get('m_InputSlot', {}).get('m_SlotId')
    print(f"{oi}:{oslot} -> {ii}:{islot}")
