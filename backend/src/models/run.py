from sqlalchemy import String,Text,JSON,ForeignKey,Double,BigInteger,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from .common import RecordMixin
from ..config.database import Base
class MatchRun(RecordMixin,Base):
 __tablename__="runs"
 policy_id:Mapped[str]=mapped_column(ForeignKey("policies.id"))
 status:Mapped[str]=mapped_column(String(20),default="queued")
 result:Mapped[dict]=mapped_column(JSON,default=dict)
 error:Mapped[str]=mapped_column(Text,default="")
