from dataclasses import asdict, is_dataclass
from dacite import from_dict as fromdict
from typing import Dict

class DBObjectBase:
    def to_dict(self) -> Dict:
        if not is_dataclass(self):
            return self.__dict__
        
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        assert is_dataclass(cls)
        return fromdict(cls, data)
