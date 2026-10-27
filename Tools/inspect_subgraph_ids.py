"""Compare the AssetDatabase serialization of the subgraph against the main graph's
m_PropertyGuids / m_PropertyIds mapping (subgraph node slot ids are ints derived from
property GUIDs -- if they disagree the subgraph inputs read their defaults instead)."""
from sgload import load_multi
import uuid

main = load_multi("../Assets/Shader/PixelOutline.shadergraph")
sub = load_multi("../Assets/Shader/OutlineSample.shadersubgraph")
subbyid = {d.get('m_ObjectId'): d for d in sub}
subprops = {d['m_ObjectId']: d for d in sub
            if 'ShaderProperty' in str(d.get('m_Type', '')) or 'ShaderKeyword' in str(d.get('m_Type', ''))}
subslots = {d['m_ObjectId']: d for d in sub if 'SubGraphOutput' in str(d.get('m_Schema', '')) or 'SubGraphOutputNode' in str(d.get('m_Type', ''))}
print("subgraph properties:")
for gid, p in subprops.items():
    print("  ", p.get('m_Name'), gid, p.get('m_DefaultReferenceName'))

print("\nsubgraph outputs:")
for gid, n in subslots.items():
    print("  ", n.get('m_Type'), n.get('m_Name'))


def guid_to_int(g):
    b = uuid.UUID(g).bytes
    return int.from_bytes(b[:4], 'little', signed=True)


for d in main:
    if not str(d.get('m_Type', '')).endswith('SubGraphNode'):
        continue
    print("\nnode", d['m_ObjectId'][:8], d.get('m_Name'))
    print("  m_PropertyGuids:", d.get('m_PropertyGuids'))
    print("  m_PropertyIds:  ", d.get('m_PropertyIds'))
    for g in d.get('m_PropertyGuids', []):
        print("   guid", g, "-> int32(big-endian first 4 bytes) =", guid_to_int(g))
    break
