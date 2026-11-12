from ..services import policy_service
from ..models.policy import MatchPolicy
from ..models.common import serialize
from .common import listing,require
def list_all(db):return listing(db,MatchPolicy)
def detail(db,ident):return serialize(require(db,MatchPolicy,ident))
def create(db,body):return serialize(policy_service.create(db,body))
