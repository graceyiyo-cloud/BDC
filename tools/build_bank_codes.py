"""從財金公司 twd.txt 產生 bank-codes.js。

用法：
    py tools/build_bank_codes.py <twd.txt 路徑> [輸出路徑，預設 bank-codes.js]

twd.txt 下載處：https://www.fisc.com.tw/tc/download/twd.txt （Big5 / cp950）
"""
import json
import sys
from datetime import date


def parse(path):
    raw = open(path, 'rb').read().decode('cp950', errors='replace')
    banks, order = {}, []
    for line in raw.splitlines():
        if not line.strip():
            continue
        code = line[:7].strip()
        rest = line[8:]
        name = rest[:20].replace('　', '').strip()
        short = rest[20:].replace('　', '').strip()
        if len(code) == 3:
            if code in banks:  # 同代碼重複出現時，沿用已收集的分行
                banks[code][1:3] = [name, short]
            else:
                banks[code] = [code, name, short, []]
                order.append(code)
        elif len(code) == 7 and code[:3] in banks:
            banks[code[:3]][3].append([code[3:], name])
    return [banks[c] for c in order]


def main():
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else 'bank-codes.js'
    data = parse(src)
    body = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(f'// 資料來源：財金資訊公司 twd.txt，產生日期 {date.today():%Y-%m-%d}\n')
        f.write('// 格式：[銀行代碼, 銀行名稱, 簡稱, [[分行代碼後4碼, 分行名稱], ...]]\n')
        f.write(f'window.BANK_CODES={body};\n')
    print('banks', len(data), 'branches', sum(len(b[3]) for b in data))


if __name__ == '__main__':
    main()
