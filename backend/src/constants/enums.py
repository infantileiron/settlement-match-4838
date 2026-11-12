from enum import StrEnum
class Role(StrEnum):
 ADMIN="admin"
 ANALYST="analyst"
 VIEWER="viewer"
class RunStatus(StrEnum):
 QUEUED="queued"
 RUNNING="running"
 COMPLETED="completed"
 FAILED="failed"
class ItemSide(StrEnum):
 MILESTONE="milestone"
 RECEIPT="receipt"
MAX_ITEM_CENTS=100000000
MAX_DP_STATES=50000
