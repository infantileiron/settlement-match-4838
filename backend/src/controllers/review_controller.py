from ..services import review_service
from ..models.review import MatchReview
from ..models.common import serialize
from .common import listing,require
def list_all(db):return listing(db,MatchReview)
def detail(db,ident):return serialize(require(db,MatchReview,ident))
def create(db,body):return serialize(review_service.create(db,body))
