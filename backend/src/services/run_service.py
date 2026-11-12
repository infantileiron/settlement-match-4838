from uuid import uuid4
from sqlalchemy import select
from fastapi import HTTPException
from ..models.run import MatchRun
from ..models.policy import MatchPolicy
from ..models.batch import StatementBatch
from ..models.item import SettlementItem
from ..utils.queue import enqueue
from .reconcile import reconcile,POLICY_FIELDS

def create(db,body):
 if not db.get(MatchPolicy,body.policy_id):raise HTTPException(422,"匹配口径不存在")
 row=MatchRun(id=str(uuid4()),policy_id=body.policy_id,status="queued",result={},error="");db.add(row);db.commit()
 try:enqueue(row.id)
 except Exception:
  row.status="failed";row.error="Redis队列不可用，请稍后重试";db.commit();raise HTTPException(503,row.error)
 return row

def compute(db,run_id):
 row=db.get(MatchRun,run_id)
 if row is None or row.status not in ["queued","running"]:return
 row.status="running";db.commit()
 try:
  policy=db.get(MatchPolicy,row.policy_id);batch=db.get(StatementBatch,policy.batch_id);rows=db.scalars(select(SettlementItem).where(SettlementItem.batch_id==batch.id).order_by(SettlementItem.external_id)).all()
  fields=["external_id","side","party","reference","amount_cents","currency","booking_date"]
  result=reconcile([{k:getattr(item,k) for k in fields} for item in rows],{k:getattr(policy,k) for k in POLICY_FIELDS})
  row.result={**result,"batch_name":batch.name,"policy_name":policy.name};row.status="completed"
 except Exception as e:row.status="failed";row.error=str(e)[:1000]
 db.commit()
