from ..services import batch_service
from ..models.batch import StatementBatch
from ..models.common import serialize
from .common import listing,require
def list_all(db):return listing(db,StatementBatch)
def detail(db,ident):return serialize(require(db,StatementBatch,ident))
def create(db,body):return serialize(batch_service.create(db,body))
