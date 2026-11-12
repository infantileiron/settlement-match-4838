from fastapi import APIRouter,Depends
from ..config.database import get_db
from ..utils.auth import current,write_user,admin
from ..schemas.item import ItemCreate
from ..controllers import item_controller as controller,common
from ..models.item import SettlementItem
from ..models.common import serialize
from ..constants.enums import ItemSide
router=APIRouter(prefix="/items",tags=["items"])
@router.get("")
def listing(batch_id:str|None=None,side:ItemSide|None=None,db=Depends(get_db),user=Depends(current)):return controller.list_all(db,batch_id,side)
@router.get("/{ident}")
def detail(ident:str,db=Depends(get_db),user=Depends(current)):return controller.detail(db,ident)
@router.post("",status_code=201)
def create(body:ItemCreate,db=Depends(get_db),user=Depends(write_user)):return controller.create(db,body)
