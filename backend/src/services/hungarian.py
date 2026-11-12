import math
import numpy as np
from scipy.optimize import linear_sum_assignment

def assign_with_reject(costs,reject_cost):
 m=len(costs);n=len(costs[0]) if m else 0
 if not m or not n:return {"matches":[],"unmatched_left":list(range(m)),"unmatched_right":list(range(n)),"objective":(m+n)*reject_cost}
 if any(len(row)!=n for row in costs) or not math.isfinite(reject_cost) or reject_cost<=0:raise ValueError("匹配矩阵或拒配分数无效")
 finite=[v for row in costs for v in row if v is not None]
 if any(not math.isfinite(v) or v<0 for v in finite):raise ValueError("匹配成本须为非负有限分数")
 size=m+n;forbidden=(size+1)*(2*reject_cost+max(finite,default=0)+1)
 matrix=np.full((size,size),forbidden,dtype=float)
 for i,row in enumerate(costs):
  for j,value in enumerate(row):
   if value is not None:matrix[i,j]=value
  matrix[i,n+i]=reject_cost
 for j in range(n):matrix[m+j,j]=reject_cost
 matrix[m:,n:]=0
 rr,cc=linear_sum_assignment(matrix);matches=[]
 for i,j in zip(rr,cc):
  if i<m and j<n:
   if costs[i][j] is None:raise ValueError("求解器选中禁配边")
   matches.append({"left":int(i),"right":int(j),"cost":float(costs[i][j])})
 used_left={x["left"] for x in matches};used_right={x["right"] for x in matches}
 return {"matches":matches,"unmatched_left":[i for i in range(m) if i not in used_left],"unmatched_right":[j for j in range(n) if j not in used_right],"objective":float(matrix[rr,cc].sum()),"reject_cost_per_item":reject_cost,"forbidden_bound":forbidden}
