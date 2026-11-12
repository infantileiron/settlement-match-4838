from ..constants.enums import MAX_DP_STATES

def bounded_subset_sum(amounts,target,tolerance,max_group_size,max_states=MAX_DP_STATES,max_total=None):
 if not isinstance(target,int) or isinstance(target,bool) or target<=0 or not isinstance(tolerance,int) or isinstance(tolerance,bool) or tolerance<0 or any(not isinstance(a,int) or isinstance(a,bool) or a<=0 for a in amounts):raise ValueError("子集和只接受正整数分和非负整数容差")
 if not 2<=max_group_size<=6 or len(amounts)>20:raise ValueError("子集候选/组大小超出限制")
 states={(0,0):()};upper=min(target+tolerance,max_total) if max_total is not None else target+tolerance
 for index,amount in enumerate(amounts):
  for (total,k),path in list(states.items()):
   if k>=max_group_size or total+amount>upper:continue
   key=(total+amount,k+1);candidate=path+(index,)
   if key not in states or candidate<states[key]:states[key]=candidate
   if len(states)>max_states:return {"found":False,"indices":[],"reason":"state_limit","state_count":len(states)}
 choices=[(abs(total-target),k,path,total) for (total,k),path in states.items() if k>=2 and abs(total-target)<=tolerance]
 if not choices:return {"found":False,"indices":[],"reason":"no_subset","state_count":len(states)}
 _,_,path,total=min(choices)
 return {"found":True,"indices":list(path),"sum_cents":total,"delta_cents":total-target,"reason":"","state_count":len(states)}
