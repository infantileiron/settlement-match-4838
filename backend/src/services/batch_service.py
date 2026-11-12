from uuid import uuid4
from sqlalchemy import select
from fastapi import HTTPException
from ..models.batch import StatementBatch
from ..models.item import SettlementItem
from .input_records import parse_csv

def create(db,body):
 if db.scalar(select(StatementBatch).where(StatementBatch.name==body.name)):raise HTTPException(409,"对账批次名称已存在")
 try:rows=parse_csv(body.csv_text)
 except ValueError as e:raise HTTPException(422,str(e))
 batch=StatementBatch(id=str(uuid4()),name=body.name,description=body.description);db.add(batch);db.flush()
 for row in rows:db.add(SettlementItem(id=str(uuid4()),batch_id=batch.id,**row))
 db.commit();return batch
