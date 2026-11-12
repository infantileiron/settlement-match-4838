from ..services import run_service
from ..models.run import MatchRun
from ..models.common import serialize
from .common import listing,require
def list_all(db):return listing(db,MatchRun)
def detail(db,ident):return serialize(require(db,MatchRun,ident))
def create(db,body):return serialize(run_service.create(db,body))
