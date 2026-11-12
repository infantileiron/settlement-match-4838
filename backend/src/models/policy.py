from sqlalchemy import String,Text,JSON,ForeignKey,Double,BigInteger,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from .common import RecordMixin
from ..config.database import Base
class MatchPolicy(RecordMixin,Base):
 __tablename__="policies"
 name:Mapped[str]=mapped_column(String(180),unique=True)
 batch_id:Mapped[str]=mapped_column(ForeignKey("batches.id"))
 amount_tolerance:Mapped[int]=mapped_column(BigInteger)
 max_days:Mapped[int]
 require_reference:Mapped[bool]
 date_weight:Mapped[float]=mapped_column(Double)
 reference_weight:Mapped[float]=mapped_column(Double)
 reject_cost:Mapped[float]=mapped_column(Double)
 max_candidates:Mapped[int]
 max_group_size:Mapped[int]
 max_group_amount:Mapped[int]=mapped_column(BigInteger)
