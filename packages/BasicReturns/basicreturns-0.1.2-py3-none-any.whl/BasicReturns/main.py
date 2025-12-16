"""
All functions ever return the same models with particulars properties
"""

from typing import Any, Optional
from pydantic import BaseModel

class BasicReturn(BaseModel):
    """Have a basic return model, contains `ok` and `error` properties.

    Attributes
        `ok: bool`: Similar to HTTP response, this means if something execution was successfully or no
        `error: Any`: When `ok` is `False`, this contains the error, like an exception or other
    
    Methods
        **to_dict()**"""
    ok: Optional[bool] = True
    error: Optional[Any] = None

    def __str__(self) -> str:
        return f'OK: {self.ok}\nError: {self.error}'
    
    def to_dict(self) -> dict:
        """Get a self representation as dictionary"""
        return{"ok": self.ok, "error": self.error}

class DataAndMsgReturn(BasicReturn):
    """Get a object return with basic properties (`ok`, `error`) and `msg` and `data` properties
    
    Attrubutes:
        `msg: str`: A message to provide information about an operation executed
        `data: Any`: A object that contains any data type, means that method was executed successfully
    
    Methods
        **to_dict()**"""
    msg: Optional[str] = None
    data: Optional[Any] = None

    def __str__(self) -> str:
        return f'{super().__str__()}\nMessage: {self.msg}\nData: {self.data}\nError: {self.error}'
    
    def to_dict(self) -> dict:
        return{**super().to_dict(), "msg": self.msg, "data": self.data if self.data else {}}