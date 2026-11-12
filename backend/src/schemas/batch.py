from pydantic import BaseModel,Field
class BatchCreate(BaseModel):
 name:str=Field(min_length=2,max_length=180)
 csv_text:str=Field(min_length=30,max_length=1500000)
 description:str=Field(default="",max_length=2000)
class BatchEdit(BaseModel):
 description:str=Field(max_length=2000)
