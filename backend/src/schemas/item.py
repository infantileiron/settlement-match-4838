from pydantic import BaseModel,Field,field_validator
from ..constants.enums import ItemSide,MAX_ITEM_CENTS
from ..services.input_records import validate_date
class ItemCreate(BaseModel):
 batch_id:str
 external_id:str=Field(min_length=1,max_length=80)
 side:ItemSide
 party:str=Field(min_length=1,max_length=160)
 reference:str=Field(default="",max_length=100)
 amount_cents:int=Field(strict=True,gt=0,le=MAX_ITEM_CENTS)
 currency:str="CNY"
 booking_date:str
 @field_validator("external_id","party","reference",mode="before")
 @classmethod
 def trim_fields(cls,value):return value.strip() if isinstance(value,str) else value
 @field_validator("currency")
 @classmethod
 def currency_check(cls,value):
  if value!="CNY":raise ValueError("仅接受CNY模拟凭证")
  return value
 @field_validator("booking_date")
 @classmethod
 def date_check(cls,value):return validate_date(value)
