from ..services import item_service
from ..models.item import SettlementItem
from ..models.common import serialize
from .common import listing,require
def list_all(db,batch_id=None,side=None):
 from sqlalchemy import select
 statement=select(SettlementItem).order_by(SettlementItem.created_at.desc(),SettlementItem.external_id)
 if batch_id:statement=statement.where(SettlementItem.batch_id==batch_id)
 if side:statement=statement.where(SettlementItem.side==side)
 return [serialize(row) for row in db.scalars(statement.limit(1000))]
def detail(db,ident):return serialize(require(db,SettlementItem,ident))
def create(db,body):return serialize(item_service.create(db,body))
