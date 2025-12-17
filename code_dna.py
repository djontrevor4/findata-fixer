#!/usr/bin/env python3
"""CodeDNA - export 70K fixes for HuggingFace fine-tune"""
import json, os, sqlite3

FD = os.path.expanduser("~/findata")

def load_all_fixes():
    fixes = {}
    # 1. fix_memory.json
    try:
        fm = json.load(open(FD + "/fix_memory.json"))
        for typo, fix in fm.items():
            if typo != fix:
                fixes[typo] = {"fix": fix, "src": "typo"}
        print("[1] fix_memory: " + str(len(fm)))
    except Exception as e:
        print("[1] fix_memory err: " + str(e))
    
    # 2. knowledge.db
    try:
        db = sqlite3.connect(FD + "/knowledge.db")
        rows = db.execute("SELECT error_type, error_msg, fixed_code FROM error_fixes WHERE success=1 AND fixed_code IS NOT NULL").fetchall()
        for r in rows:
            key = r[0] + ":" + r[1][:50]
            fixes[key] = {"fix": r[2], "src": "kb"}
        print("[2] knowledge.db: " + str(len(rows)))
        db.close()
    except Exception as e:
        print("[2] knowledge err: " + str(e))
    
    # 3. patterns
    try:
        db = sqlite3.connect(FD + "/episodes.db")
        rows = db.execute("SELECT pattern, success_rate FROM patterns WHERE success_rate > 0.7").fetchall()
        for r in rows:
            if "::" in r[0]:
                parts = r[0].split("::")
                if len(parts) >= 2:
                    fixes[parts[0]] = {"fix": parts[-1], "src": "pattern", "rate": r[1]}
        print("[3] patterns: " + str(len(rows)))
        db.close()
    except Exception as e:
        print("[3] patterns err: " + str(e))
    
    return fixes

def export_jsonl(fixes):
    out = FD + "/training_data.jsonl"
    count = 0
    with open(out, "w") as f:
        for err, info in fixes.items():
            if len(err) > 3 and len(info["fix"]) > 1:
                item = {"instruction": "Fix: " + err, "output": info["fix"], "source": info.get("src", "unknown")}
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
                count += 1
    print("Exported: " + str(count) + " -> " + out)
    return count

def stats():
    try:
        lines = open(FD + "/training_data.jsonl").readlines()
        srcs = {}
        for l in lines:
            d = json.loads(l)
            s = d.get("source", "?")
            srcs[s] = srcs.get(s, 0) + 1
        print("Dataset: " + str(len(lines)) + " samples")
        for s, c in sorted(srcs.items(), key=lambda x: -x[1]):
            print("   " + s + ": " + str(c))
    except Exception as e:
        print("No dataset: " + str(e))

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        stats()
    else:
        fixes = load_all_fixes()
        export_jsonl(fixes)
        print("CodeDNA ready!")
        stats()