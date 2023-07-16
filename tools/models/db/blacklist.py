from typing import Optional
from .abc import DBObjectBase
from dataclasses import dataclass

@dataclass
class BlackList(DBObjectBase):
    user_id: int
    blocked_at: int
    reason: Optional[str]
    blocked_until: Optional[int]
