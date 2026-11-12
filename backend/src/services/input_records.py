import csv,io,re,unicodedata
from datetime import date
from ..constants.enums import MAX_ITEM_CENTS
FIELDS=["external_id","side","party","reference","amount_cents","currency","booking_date"]

def normalize(value):return " ".join(unicodedata.normalize("NFKC",value).strip().casefold().split())
def validate_date(value):
 try:
  if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}",value):raise ValueError()
  return date.fromisoformat(value).isoformat()
 except Exception:raise ValueError("日期须为有效YYYY-MM-DD")

def parse_csv(text):
 rows=list(csv.DictReader(io.StringIO(text)))
 if not rows or len(rows)>500 or not set(FIELDS).issubset(rows[0]):raise ValueError("CSV须含完整列，且为1至500条分录")
 result=[];ids=set()
 for index,row in enumerate(rows,2):
  ident=(row.get("external_id") or "").strip();side=(row.get("side") or "").strip();party=(row.get("party") or "").strip();reference=(row.get("reference") or "").strip()
  if not ident or len(ident)>80 or ident in ids:raise ValueError(f"第{index}行ID为空、过长或重复")
  ids.add(ident)
  if side not in ["milestone","receipt"] or not party or len(party)>160 or len(reference)>100:raise ValueError("分录方向/往来方/委托引用无效")
  if row.get("currency")!="CNY":raise ValueError("只接受CNY模拟凭证")
  raw=(row.get("amount_cents") or "").strip()
  if not re.fullmatch(r"[0-9]+",raw):raise ValueError("金额须为正整数分，不接受小数、负值或科学计数法")
  amount=int(raw)
  if not 0<amount<=MAX_ITEM_CENTS:raise ValueError("金额分超出允许范围")
  result.append({"external_id":ident,"side":side,"party":party,"reference":reference,"amount_cents":amount,"currency":"CNY","booking_date":validate_date(row.get("booking_date") or "")})
 return result
