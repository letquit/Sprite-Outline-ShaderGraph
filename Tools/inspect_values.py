from sgload import load_multi

sub = load_multi("../Assets/Shader/OutlineSample.shadersubgraph")
byid = {d.get('m_ObjectId'): d for d in sub}

for d in sub:
    t = str(d.get('m_Type', '')).split('.')[-1]
    if t in ('Vector2Node', 'ReciprocalNode', 'Texture2DPropertiesNode'):
        print('==', t, d['m_ObjectId'][:8], 'name=', d.get('m_Name'))
        print('   extra:', {k: v for k, v in d.items() if k in ('m_Value', 'm_ReciprocalMethod')})
        for s in d['m_Slots']:
            sd = byid[s['m_Id']]
            print('   slot', sd['m_Id'], repr(sd['m_DisplayName']), 'in' if sd['m_SlotType'] == 0 else 'out',
                  'val=', sd.get('m_Value'))
