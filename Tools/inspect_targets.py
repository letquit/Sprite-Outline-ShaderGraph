from sgload import load_multi

docs = load_multi("../Assets/Shader/OutlineSample.shadersubgraph")
byid = {d.get("m_ObjectId"): d for d in docs}
root = next(d for d in docs if str(d.get("m_Type", "")).endswith("GraphData"))
edges = root["m_Edges"]


def rel(o_node, o_slot, i_node, i_slot):
    """does an edge exist, and is it redundant (input already driven)?"""
    hit = [e for e in edges if e["m_OutputSlot"]["m_Node"]["m_Id"] == o_node
           and e["m_OutputSlot"]["m_SlotId"] == o_slot
           and e["m_InputSlot"]["m_Node"]["m_Id"] == i_node
           and e["m_InputSlot"]["m_SlotId"] == i_slot]
    others = [e for e in edges if e["m_InputSlot"]["m_Node"]["m_Id"] == i_node
              and e["m_InputSlot"]["m_SlotId"] == i_slot]
    return len(hit), len(others)


N = lambda s: next(k for k in byid if k.startswith(s))
name = lambda s: f"{str(byid[N(s)].get('m_Type','')).split('.')[-1]}[{s}]"

targets = [
    ("69692f47", 2, "c355746b", 2),   # Add.Out  <- Multiply(c355746b).Out
    ("69692f47", 1, "c355746b", 2),
    ("69692f47", 0, "60228e79", 0),   # Add.A <- UV
    ("e3731a09", 0, "d96eb003", 1),   # Multiply.A <- Reciprocal.Out
    ("e3731a09", 1, "efa2aa84", 0),
    ("c355746b", 0, "e3731a09", 2),
    ("c355746b", 1, "efa2aa84", 0),
    ("48bcab84", 2, "69692f47", 2),
    ("e07d4d1e", 2, "48bcab84", 7),
]
for i_n, i_s, o_n, o_s in targets:
    have, others = rel(N(o_n), o_s, N(i_n), i_s)
    print(f"{name(o_n)}.{o_s}  ->  {name(i_n)}.{i_s}   edge={bool(have)}  inputs_on_target={others}")
