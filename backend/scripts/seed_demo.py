import json
from datetime import date,timedelta
from sqlalchemy import select,func
from src.config.database import initialize,Session
from src.models import StatementBatch,SettlementItem,MatchPolicy,MatchRun,MatchReview,Report,User
from src.utils.security import hash_password
from src.services.run_service import compute

def make_items():
 rows=[];base=date(2026,11,1)
 for i in range(1,81):
  party=f"模拟译稿客户{i%6+1}";reference=f"JOB-{i:03}";amount=5000+(i%10)*1000;day=base+timedelta(days=i%5)
  if 51<=i<=70:
   group=(i-51)//2+1;party=f"合并委托客户{group}";reference=f"BUNDLE-{group:02}";amount=8000+group*100+(4000 if i%2==0 else 0);day=base
  if i in [74,75]:party="同额待辨客户";reference="SAME-AMOUNT";amount=18000;day=base+timedelta(days=0 if i==74 else 2)
  rows.append({"external_id":f"M{i:03}","side":"milestone","party":party,"reference":reference,"amount_cents":amount,"currency":"CNY","booking_date":day.isoformat()})
 for i in range(1,51):
  row=rows[i-1];rows.append({**row,"external_id":f"R{i:03}","side":"receipt","booking_date":(date.fromisoformat(row["booking_date"])+timedelta(days=1)).isoformat()})
 for group in range(1,11):
  a,b=rows[50+(group-1)*2:52+(group-1)*2];rows.append({**a,"external_id":f"R{50+group:03}","side":"receipt","amount_cents":a["amount_cents"]+b["amount_cents"],"booking_date":(base+timedelta(days=1)).isoformat()})
 for i,index in [(61,70),(62,71),(63,72)]:
  row=rows[index].copy();row.update(external_id=f"R{i:03}",side="receipt")
  if i==61:row["party"]="不兼容往来方"
  if i==62:row["reference"]="WRONG-REFERENCE"
  if i==63:row["booking_date"]=(date.fromisoformat(row["booking_date"])+timedelta(days=30)).isoformat()
  rows.append(row)
 rows.append({"external_id":"R064","side":"receipt","party":"无委托来源","reference":"UNKNOWN","amount_cents":9999,"currency":"CNY","booking_date":base.isoformat()})
 rows.append({**rows[73],"external_id":"R065","side":"receipt","booking_date":(base+timedelta(days=1)).isoformat()})
 return rows

def seed():
 initialize()
 with Session() as db:
  for role in ["admin","analyst","viewer"]:
   email=role+"@settlement.demo"
   if not db.scalar(select(User).where(User.email==email)):db.add(User(id="user-"+role,email=email,role=role,password_hash=hash_password("MatchDemo2026!")))
  if not db.get(StatementBatch,"demo-batch"):db.add(StatementBatch(id="demo-batch",name="长川十一月译务结算模拟",description="80委托/65凭证；文件changchuan_settlement_202611.csv；不连接银行"))
  db.commit()
  for row in make_items():
   ident="demo-"+row["external_id"]
   if not db.get(SettlementItem,ident):db.add(SettlementItem(id=ident,batch_id="demo-batch",**row))
  db.commit()
  if not db.get(MatchPolicy,"demo-policy"):db.add(MatchPolicy(id="demo-policy",name="同币同方同引用 · 七日口径",batch_id="demo-batch",amount_tolerance=0,max_days=7,require_reference=True,date_weight=1.,reference_weight=20.,reject_cost=40.,max_candidates=16,max_group_size=4,max_group_amount=2000000))
  db.commit()
  if not db.get(MatchRun,"demo-run"):db.add(MatchRun(id="demo-run",policy_id="demo-policy",status="queued",result={},error=""));db.commit();compute(db,"demo-run")
  if not db.get(MatchReview,"demo-review"):db.add(MatchReview(id="demo-review",run_id="demo-run",action="逐项核查一对一及合并组，未配项保留原因。两阶段不保证联合全局最优，批准仅留档，不写银行或自动核销。",state="approved",reviewer="admin@settlement.demo"))
  db.commit()
  if not db.get(Report,"demo-report"):db.add(Report(id="demo-report",review_id="demo-review",title="长川译务结算勾稽底稿",snapshot={"result":db.get(MatchRun,"demo-run").result,"action":db.get(MatchReview,"demo-review").action,"reviewer":"admin@settlement.demo"}))
  db.commit()
  return {cls.__tablename__:db.scalar(select(func.count()).select_from(cls)) for cls in [User,StatementBatch,SettlementItem,MatchPolicy,MatchRun,MatchReview,Report]}
if __name__=="__main__":print(json.dumps(seed(),ensure_ascii=False))
