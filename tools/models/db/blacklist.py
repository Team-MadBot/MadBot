from typing import Optional

class BlackList:
    def __init__(
        self, 
        user_id: int, 
        blocked_at: int,
        reason: Optional[str],
        blocked_until: Optional[int]
    ):
        self.user_id = user_id
        self.reason = reason
        self.blocked_at = blocked_at
        self.blocked_until = blocked_until