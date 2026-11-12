from datetime import date
from .input_records import normalize

def compatible(milestone,receipt,policy,amount_check=True):
 if milestone["currency"]!=receipt["currency"] or normalize(milestone["party"])!=normalize(receipt["party"]):return False
 if abs((date.fromisoformat(milestone["booking_date"])-date.fromisoformat(receipt["booking_date"])).days)>policy["max_days"]:return False
 a,b=normalize(milestone["reference"]),normalize(receipt["reference"])
 if policy["require_reference"] and (not a or a!=b):return False
 if amount_check and abs(milestone["amount_cents"]-receipt["amount_cents"])>policy["amount_tolerance"]:return False
 return True

def cost(milestone,receipt,policy):
 days=abs((date.fromisoformat(milestone["booking_date"])-date.fromisoformat(receipt["booking_date"])).days)
 return days*policy["date_weight"]+(0 if normalize(milestone["reference"])==normalize(receipt["reference"]) else policy["reference_weight"])+abs(milestone["amount_cents"]-receipt["amount_cents"])/(policy["amount_tolerance"]+1)
