from pydantic import BaseModel,Field,model_validator
class PolicyCreate(BaseModel):
 name:str=Field(min_length=2,max_length=180)
 batch_id:str
 amount_tolerance:int=Field(default=0,strict=True,ge=0,le=10000)
 max_days:int=Field(default=7,strict=True,ge=0,le=90)
 require_reference:bool=True
 date_weight:float=Field(default=1,ge=0,le=1000,allow_inf_nan=False)
 reference_weight:float=Field(default=20,ge=0,le=10000,allow_inf_nan=False)
 reject_cost:float=Field(default=40,gt=0,le=10000,allow_inf_nan=False)
 max_candidates:int=Field(default=16,strict=True,ge=2,le=20)
 max_group_size:int=Field(default=4,strict=True,ge=2,le=6)
 max_group_amount:int=Field(default=2000000,strict=True,ge=1,le=10000000)
 @model_validator(mode="after")
 def group_limit(self):
  if self.max_group_size>self.max_candidates:raise ValueError("合并组大小不能高于候选数量")
  return self
