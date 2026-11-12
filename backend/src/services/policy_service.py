from uuid import uuid4
from sqlalchemy import select
from fastapi import HTTPException
from ..models.batch import StatementBatch
from ..models.policy import MatchPolicy

def create(db,body):
 if not db.get(StatementBatch,body.batch_id):raise HTTPException(422,"对账批次不存在")
 if db.scalar(select(MatchPolicy).where(MatchPolicy.name==body.name)):raise HTTPException(409,"匹配口径名称已存在")
 row=MatchPolicy(id=str(uuid4()),**body.model_dump());db.add(row);db.commit();return row
