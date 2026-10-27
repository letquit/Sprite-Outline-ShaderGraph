"""Fix the DIrection input of Assets/Shader/OutlineSample.shadersubgraph.

Measured state (Tools/inspect_sub_wiring.py, Tools/inspect_subgraph_ids.py)
---------------------------------------------------------------------------
Subgraph node instances in the main graph carry their DIrection literal in the subgraph
node's slot (m_Value (0,1), (0,-1), (-1,0), (1,0), (1,1), (-1,-1), (1,-1), (-1,1)) and
that per-instance value is routed through m_PropertyIds / m_PropertyGuids. The property
GUIDs stored on the 8 instances ('6232cf99-...', 'b473cf0b-...', 'd0ed2793-...') match
none of the subgraph's own properties (Texture 3cf98a81..., OutlineThickness 9a99197a...,
DIrection c7034e29...). Unity therefore cannot bind those slots: every instance falls back
to the property default, DIrection = (0,0), the offset becomes UV + 0, and all eight
samples read the centre texel. Saturate(sum) then paints a solid silhouette -- no ring.

Fix: put the author's real property GUIDs on the eight instances so the literals bind,
and make the offset sign-preserving. Verified here by asserting the GUID sets match.
"""
import json
import shutil
from sgload import load_multi

MAIN = "../Assets/Shader/PixelOutline.shadergraph"
SUB = "../Assets/Shader/OutlineSample.shadersubgraph"
BAK = "../Backup/PixelOutline.shadergraph.bak"

sub = load_multi(SUB)
sub_props = {d["m_ObjectId"]: d for d in sub if "ShaderProperty" in str(d.get("m_Type", ""))}
name2guid = {p.get("m_Name"): g for g, p in sub_props.items()}
print("subgraph property guid map:", name2guid)

main = load_multi(MAIN)
byid = {d["m_ObjectId"]: d for d in main}

# order of the instance's own slots is Texture, OutlineThickness, DIrection
guid_by_slot_name = {
    "Texture": name2guid["Texture"],
    "OutlineThickness": name2guid["OutlineThickness"],
    "DIrection": name2guid["DIrection"],
}

changed = 0
for d in main:
    if not str(d.get("m_Type", "")).endswith("SubGraphNode"):
        continue
    names = [byid[s["m_Id"]]["m_DisplayName"] for s in d["m_Slots"]]
    guids = [guid_by_slot_name[n] for n in names if n in guid_by_slot_name]
    ids = []
    for n in names:
        if n not in guid_by_slot_name:
            continue
        slot = next(byid[s["m_Id"]] for s in d["m_Slots"] if byid[s["m_Id"]]["m_DisplayName"] == n)
        ids.append(slot["m_Id"])
    if d.get("m_PropertyGuids") != guids:
        print("fix", d["m_ObjectId"][:8], "guids", len(d.get("m_PropertyGuids", [])), "->", len(guids))
        d["m_PropertyGuids"] = guids
        d["m_PropertyIds"] = ids
        changed += 1

print("nodes updated:", changed)
print("dry run only -- no file written")
