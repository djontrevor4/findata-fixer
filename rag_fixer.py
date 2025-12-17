import json, os

FD = os.path.expanduser("~/findata")

def find_similar(error, top_k=3):
    lines = open(FD + "/training_data.jsonl").readlines()
    matches = []
    err_low = error.lower()
    for l in lines:
        d = json.loads(l)
        inst = d["instruction"].lower()
        score = sum(1 for w in err_low.split() if w in inst)
        if score > 0:
            matches.append((score, d))
    matches.sort(key=lambda x: -x[0])
    return [{'typo': m[1]['instruction'][5:], 'fix': m[1]['output']} for m in matches[:top_k]]

# Test
print(find_similar("print hello"))
print(find_similar("import request"))