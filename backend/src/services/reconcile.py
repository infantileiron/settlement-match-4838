import hashlib,json
from datetime import date
from .compatibility import compatible,cost
from .hungarian import assign_with_reject
from .joint_merge import enumerate_groups,joint_assign
from ..constants.enums import MAX_GROUPS_PER_RECEIPT

POLICY_FIELDS=["amount_tolerance","max_days","require_reference","date_weight","reference_weight","reject_cost","max_candidates","max_group_size","max_group_amount"]

def reconcile(items,policy):
 milestones=sorted([x for x in items if x["side"]=="milestone"],key=lambda x:x["external_id"]);receipts=sorted([x for x in items if x["side"]=="receipt"],key=lambda x:(x["booking_date"],x["external_id"]))
 if not milestones or not receipts:raise ValueError("批次需同时存在委托里程碑和入账凭证")
 matrix=[[cost(m,r,policy) if compatible(m,r,policy) else None for r in receipts] for m in milestones]
 first=assign_with_reject(matrix,policy["reject_cost"]);pairs=[];used_m=set();used_r=set()
 for edge in first["matches"]:
  m=milestones[edge["left"]];r=receipts[edge["right"]];used_m.add(m["external_id"]);used_r.add(r["external_id"])
  pairs.append({"stage":"one_to_one","milestone_ids":[m["external_id"]],"receipt_id":r["external_id"],"milestone_sum_cents":m["amount_cents"],"receipt_amount_cents":r["amount_cents"],"delta_cents":m["amount_cents"]-r["amount_cents"],"currency":"CNY","party":r["party"],"score":edge["cost"]})
 pool=[m for m in milestones if m["external_id"] not in used_m];position={m["external_id"]:i for i,m in enumerate(pool)}
 contexts=[];searches=[]
 for r in receipts:
  if r["external_id"] in used_r:continue
  if r["amount_cents"]>policy["max_group_amount"]:
   searches.append({"receipt_id":r["external_id"],"reason":"target_above_limit","found":False,"candidates":0,"truncated":0,"groups":0,"omitted":0});continue
  eligible=[m for m in pool if m["amount_cents"]<=r["amount_cents"]+policy["amount_tolerance"] and compatible(m,r,policy,amount_check=False)]
  eligible.sort(key=lambda m:(abs((date.fromisoformat(m["booking_date"])-date.fromisoformat(r["booking_date"])).days),m["external_id"]))
  truncated=max(0,len(eligible)-policy["max_candidates"]);candidates=eligible[:policy["max_candidates"]]
  enum=enumerate_groups([position[m["external_id"]] for m in candidates],[m["amount_cents"] for m in candidates],r["amount_cents"],policy["amount_tolerance"],policy["max_group_size"],policy["max_group_amount"])
  search={"receipt_id":r["external_id"],"candidates":len(candidates),"truncated":truncated,"groups":len(enum["groups"]),"omitted":enum["omitted"],"found":False,"reason":"no_subset"}
  searches.append(search);contexts.append({"receipt":r,"groups":enum["groups"],"search":search})
 joint=joint_assign(contexts);groups=[]
 for pos,group in sorted(joint["assign"].items()):
  ctx=contexts[pos];r=ctx["receipt"];ids=[pool[p]["external_id"] for p in group["members"]]
  if used_m.intersection(ids):raise ValueError("合并候选重复消耗委托")
  used_m.update(ids);used_r.add(r["external_id"]);ctx["search"].update(found=True,reason="")
  groups.append({"stage":"merged","milestone_ids":ids,"receipt_id":r["external_id"],"milestone_sum_cents":group["sum"],"receipt_amount_cents":r["amount_cents"],"delta_cents":group["sum"]-r["amount_cents"],"currency":"CNY","party":r["party"],"score":None})
 for ctx in contexts:
  if ctx["groups"] and not ctx["search"]["found"]:ctx["search"]["reason"]="unassigned"
 capped=any(s["omitted"] for s in searches);proven=not joint["stopped"] and not capped;limits=[]
 if joint["stopped"]:limits.append(f"达到搜索节点上限{joint['node_budget']}")
 if capped:limits.append(f"单凭证可行组合超过上限{MAX_GROUPS_PER_RECEIPT}")
 objective=f"合并凭证{len(groups)}张，总金额差{joint['total_delta']}分"
 note=f"联合分配已在候选与金额限制内证明最优：{objective}。" if proven else f"联合分配未证最优（{'；'.join(limits)}），已给出可行组合：{objective}，可人工复核边界。"
 unmatched_m=[m for m in milestones if m["external_id"] not in used_m];unmatched_r=[r for r in receipts if r["external_id"] not in used_r]
 all_m=[i for match in pairs+groups for i in match["milestone_ids"]];all_r=[match["receipt_id"] for match in pairs+groups]
 assert len(all_m)==len(set(all_m)) and len(all_r)==len(set(all_r))
 fingerprint=hashlib.sha256(json.dumps(sorted(items,key=lambda x:x["external_id"]),sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
 return {"phase_one":{"matches":pairs,"objective_with_rejections":first["objective"],"compatible_edges":sum(v is not None for row in matrix for v in row)},"phase_two":{"groups":groups,"searches":searches,"objective":{"matched_receipts":len(groups),"total_delta_cents":joint["total_delta"]},"proven_optimal":proven,"explored_nodes":joint["explored_nodes"],"node_budget":joint["node_budget"],"group_cap":MAX_GROUPS_PER_RECEIPT,"note":note},"unmatched":{"milestones":unmatched_m,"receipts":unmatched_r},"counts":{"milestones":len(milestones),"receipts":len(receipts),"one_to_one":len(pairs),"merged":len(groups),"consumed_milestones":len(used_m),"consumed_receipts":len(used_r),"unmatched_milestones":len(unmatched_m),"unmatched_receipts":len(unmatched_r)},"policy":policy,"items":items,"input_sha256":fingerprint,"assumption":"第一阶段含双侧拒配dummy的一对一全局最小成本；第二阶段在候选与金额限制内对剩余委托和凭证联合分配，依次优先多配凭证、再最小化总金额差，同一委托不重复使用；触及搜索节点或组合枚举上限时降级为可行组合并标记未证最优。所有消耗仅在本次试验内，不写银行或自动核销。"}
