
import re, json, pathlib
# 載入你個 46客資料庫嘅簡化版
DB = json.loads(pathlib.Path(__file__).parent.joinpath("clients_database_sample.json").read_text(encoding="utf-8"))

CJK_NUM = {'千':1000, '萬':10000}
def parse_cjk_amount(text):
    # 識別 "四千蚊" "4000蚊" "4千"
    m = re.search(r'([0-9]+\.?[0-9]*|[一二三四五六七八九十兩]+)\s*([千萬])?\s*蚊?', text)
    if not m: return None
    raw = m.group(1)
    # 中文數字簡單轉
    cn_map = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10,'兩':2}
    try:
        num = float(raw) if raw[0].isdigit() else cn_map.get(raw,0)
    except: num = 0
    mult = CJK_NUM.get(m.group(2),1) if m.group(2) else 1
    return int(num*mult)

def parse_intent(text: str):
    text_low = text.lower()
    client_found = None
    for name, info in DB.items():
        for alias in [name.lower()] + [a.lower() for a in info.get('aliases',[])]:
            if alias in text_low:
                client_found = name
                break
        if client_found: break

    amount = parse_cjk_amount(text) or 0
    # 項目: 攞客名以外嘅字
    project = text
    if client_found:
        for alias in DB[client_found]['aliases']+[client_found]:
            project = project.replace(alias, '')
    project = re.sub(r'[0-9千萬蚊\s]+', '', project).strip() or "General Service"

    return {
        "client": client_found or "Unknown",
        "attention": DB.get(client_found, {}).get("default_attention",""),
        "email": DB.get(client_found, {}).get("emails",[""])[0],
        "project": project,
        "total": amount,
        "raw": text
    }

if __name__ == "__main__":
    for t in ["金城 南丫島 四千蚊", "中水 隧道 12000", "CRCC 現場視察 8000蚊"]:
        print(t, "->", parse_intent(t))
