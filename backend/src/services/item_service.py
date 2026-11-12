from uuid import uuid4
from sqlalchemy import select
from fastapi import HTTPException
from ..models.batch import StatementBatch
from ..models.item import SettlementItem
from .input_records import normalize

def create(db,body):
 if not db.get(StatementBatch,body.batch_id):raise HTTPException(422,"对账批次不存在")
 if not normalize(body.party) or not body.external_id.strip():raise HTTPException(422,"往来方或ID为空")
 if db.scalar(select(SettlementItem).where(SettlementItem.batch_id==body.batch_id,SettlementItem.external_id==body.external_id)):raise HTTPException(409,"同批次分录ID已存在")
 row=SettlementItem(id=str(uuid4()),**body.model_dump());db.add(row);db.commit();return row
