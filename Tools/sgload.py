import json, sys

def load_multi(path):
    txt = open(path, encoding='utf-8-sig').read()
    dec = json.JSONDecoder()
    i, out = 0, []
    while i < len(txt):
        while i < len(txt) and txt[i] in ' \r\n\t':
            i += 1
        if i >= len(txt):
            break
        obj, j = dec.raw_decode(txt, i)
        out.append(obj)
        i = j
    return out

if __name__ == '__main__':
    docs = load_multi(sys.argv[1])
    print(len(docs), "documents")
    for d in docs:
        print(d.get('m_Type'), d.get('m_ObjectId'))
