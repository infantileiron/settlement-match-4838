from ..constants.enums import MAX_GROUPS_PER_RECEIPT,MAX_SEARCH_NODES

def enumerate_groups(indices,amounts,target,tolerance,max_group_size,max_total,cap=MAX_GROUPS_PER_RECEIPT):
 """枚举单张凭证在候选与金额限制内的全部可行合并组。
 组大小2至max_group_size，整数分和落在target±tolerance且不超过max_total；
 组合数超过cap时按(绝对差额,索引路径)保留最优cap组并记录omitted。"""
 if not isinstance(target,int) or isinstance(target,bool) or target<=0 or not isinstance(tolerance,int) or isinstance(tolerance,bool) or tolerance<0 or any(not isinstance(a,int) or isinstance(a,bool) or a<=0 for a in amounts):raise ValueError("合并组枚举只接受正整数分和非负整数容差")
 if not 2<=max_group_size<=6 or len(amounts)>20 or len(indices)!=len(amounts):raise ValueError("合并候选/组大小超出限制")
 upper=min(target+tolerance,max_total);lower=target-tolerance;found=[]
 def visit(start,total,chosen):
  if len(chosen)>=2 and lower<=total:found.append((abs(total-target),tuple(chosen),total))
  if len(chosen)>=max_group_size:return
  for pos in range(start,len(amounts)):
   if total+amounts[pos]<=upper:visit(pos+1,total+amounts[pos],chosen+[pos])
 for first in range(len(amounts)):
  if amounts[first]<=upper:visit(first+1,amounts[first],[first])
 found.sort()
 omitted=max(0,len(found)-cap)
 return {"groups":[{"delta":delta,"sum":total,"members":tuple(indices[p] for p in path)} for delta,path,total in found[:cap]],"omitted":omitted}

def joint_assign(contexts,node_budget=MAX_SEARCH_NODES):
 """在候选与金额限制内联合分配剩余委托与凭证：先最大化配对凭证数，再最小化各组绝对差额之和；同一委托不重复使用。
 贪心种子加分支限界，遍历顺序与平局保留确定；节点预算耗尽时返回当前最优可行组合并标记stopped。"""
 n=len(contexts)
 for ctx in contexts:
  for group in ctx["groups"]:group["mask"]=sum(1<<p for p in group["members"])
 suffix_count=[0]*(n+1);suffix_min=[[] for _ in range(n+1)]
 for i in range(n-1,-1,-1):
  groups=contexts[i]["groups"]
  suffix_count[i]=suffix_count[i+1]+(1 if groups else 0)
  suffix_min[i]=sorted(suffix_min[i+1]+([groups[0]["delta"]] if groups else []))
 suffix_cum=[]
 for row in suffix_min:
  cum=[0]
  for value in row:cum.append(cum[-1]+value)
  suffix_cum.append(cum)
 best={"count":0,"delta":0,"assign":{}}
 used=0
 for i,ctx in enumerate(contexts):
  for group in ctx["groups"]:
   if not group["mask"]&used:
    used|=group["mask"];best["assign"][i]=group;break
 best["count"]=len(best["assign"]);best["delta"]=sum(group["delta"] for group in best["assign"].values())
 state={"nodes":0,"stopped":False};chosen={}
 def dfs(i,used,count,delta):
  if state["stopped"]:return
  state["nodes"]+=1
  if state["nodes"]>node_budget:state["stopped"]=True;return
  if count+suffix_count[i]<best["count"]:return
  if count+suffix_count[i]==best["count"] and delta+suffix_cum[i][best["count"]-count]>=best["delta"]:return
  if i==n:
   if count>best["count"] or (count==best["count"] and delta<best["delta"]):best.update(count=count,delta=delta,assign=dict(chosen))
   return
  for group in contexts[i]["groups"]:
   if group["mask"]&used:continue
   chosen[i]=group
   dfs(i+1,used|group["mask"],count+1,delta+group["delta"])
   del chosen[i]
   if state["stopped"]:return
  dfs(i+1,used,count,delta)
 dfs(0,0,0,0)
 return {"assign":best["assign"],"matched":best["count"],"total_delta":best["delta"],"stopped":state["stopped"],"explored_nodes":state["nodes"],"node_budget":node_budget}
