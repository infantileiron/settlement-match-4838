from sqlalchemy import String,Text,JSON,ForeignKey,Double,BigInteger,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from .common import RecordMixin
from ..config.database import Base
class SettlementItem(RecordMixin,Base):
 __tablename__="items"
 __table_args__=(UniqueConstraint("batch_id","external_id",name="uq_batch_external"),)
 batch_id:Mapped[str]=mapped_column(ForeignKey("batches.id"))
 external_id:Mapped[str]=mapped_column(String(80,collation="utf8mb4_bin"))
 side:Mapped[str]=mapped_column(String(20))
 party:Mapped[str]=mapped_column(String(160))
 reference:Mapped[str]=mapped_column(String(100))
 amount_cents:Mapped[int]=mapped_column(BigInteger)
 currency:Mapped[str]=mapped_column(String(3))
 booking_date:Mapped[str]=mapped_column(String(10))
