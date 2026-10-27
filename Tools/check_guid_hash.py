"""Decisive test of the guid-mismatch hypothesis.

Shader Graph derives a subgraph input's int slot id from the property's Guid via
Guid.GetHashCode(). If the guids recorded on the SubGraphNode hash to the slot ids that
are actually serialized, the binding is intact and the mismatch I saw is a red herring.
If instead the SUBGRAPH's own property guids hash to those ids, the node's recorded guids
are stale and the literal never binds.
"""
import struct
import uuid


def guid_hash(g: str) -> int:
    u = uuid.UUID(g)
    a, b, c = struct.unpack("<IHH", u.bytes_le[:8])
    d = u.bytes_le[8:]
    x = a ^ ((b << 16) | c)
    x ^= d[0] | (d[1] << 8) | (d[2] << 16) | (d[3] << 24)
    x ^= d[4] | (d[5] << 8) | (d[6] << 16) | (d[7] << 24)
    return struct.unpack("<i", struct.pack("<I", x & 0xFFFFFFFF))[0]


NODE_GUIDS = ["6232cf99-df99-4985-9e06-f075e0cc4999",
              "b473cf0b-856d-4ae5-ab7c-008d1d4960cb",
              "d0ed2793-0be3-469b-9284-168000227d98"]
SUBGRAPH_PROPS = {"Texture": "3cf98a81-b815-4852-9f1e-f300e691a48d",
                  "OutlineThickness": "9a99197a-19d3-4bdc-a6a2-7399143952d6",
                  "DIrection": "c7034e29-837f-4f81-a33c-253df507201e"}

ACTUAL_SLOT_IDS = {"Texture": -955327874, "OutlineThickness": -1191804976, "DIrection": -1910666526}

print("slot ids Unity actually serialized:", ACTUAL_SLOT_IDS)
print()
print("hash of the guids recorded ON THE NODE:")
for g in NODE_GUIDS:
    print(f"  {g}  ->  {guid_hash(g)}")
print()
print("hash of the SUBGRAPH's real property guids:")
for name, g in SUBGRAPH_PROPS.items():
    h = guid_hash(g)
    print(f"  {name:17} {g}  ->  {h}   matches serialized id: {ACTUAL_SLOT_IDS[name] == h}")
