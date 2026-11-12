from sqlalchemy import String,Text,JSON,ForeignKey,Double,BigInteger,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from .common import RecordMixin
from ..config.database import Base
class StatementBatch(RecordMixin,Base):
 __tablename__="batches"
 name:Mapped[str]=mapped_column(String(180),unique=True)
 description:Mapped[str]=mapped_column(Text,default="")
