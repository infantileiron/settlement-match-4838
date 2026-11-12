import csv,io
from uuid import uuid4
from sqlalchemy import select
from fastapi import HTTPException
from ..models.review import MatchReview
from ..models.run import MatchRun
from ..models.report import Report

def create(db,body):
 review=db.get(MatchReview,body.review_id)
 if review is None or review.state!="approved":raise HTTPException(409,"报告须关联已批准匹配复核")
 existing=db.scalar(select(Report).where(Report.review_id==body.review_id))
 if existing:return existing
 run=db.get(MatchRun,review.run_id);row=Report(id=str(uuid4()),review_id=review.id,title=body.title,snapshot={"result":run.result,"action":review.action,"reviewer":review.reviewer});db.add(row);db.commit();return row

def export(row):
 result=row.snapshot["result"];out=io.StringIO();writer=csv.writer(out);writer.writerow(["stage","receipt_id","milestone_ids","receipt_amount_cents","milestone_sum_cents","delta_cents","currency","party","amount_tolerance_cents","max_days","input_sha256"])
 for match in result["phase_one"]["matches"]+result["phase_two"]["groups"]:writer.writerow([match["stage"],match["receipt_id"],"|".join(match["milestone_ids"]),match["receipt_amount_cents"],match["milestone_sum_cents"],match["delta_cents"],"CNY",match["party"],result["policy"]["amount_tolerance"],result["policy"]["max_days"],result["input_sha256"]])
 for side in ["receipts","milestones"]:
  for item in result["unmatched"][side]:writer.writerow(["unmatched_"+side[:-1],item["external_id"] if side=="receipts" else "",item["external_id"] if side=="milestones" else "",item["amount_cents"] if side=="receipts" else "",item["amount_cents"] if side=="milestones" else "","","CNY",item["party"],result["policy"]["amount_tolerance"],result["policy"]["max_days"],result["input_sha256"]])
 return "\ufeff"+out.getvalue()
