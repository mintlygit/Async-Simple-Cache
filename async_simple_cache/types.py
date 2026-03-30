from typing import TypeVar, Generic, Optional, Any, Dict
from dataclasses import dataclass
from datetime import datetime

T = TypeVar('T')

@dataclass
class CacheEntry(Generic[T]):
    value: T
    expires_at: Optional[datetime] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.now() >= self.expires_at