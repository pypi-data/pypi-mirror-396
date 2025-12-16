from typing import Optional
from pydantic import BaseModel


class AuthControllerWriteDto(BaseModel):
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None

class AuthServiceWriteDto(AuthControllerWriteDto):
    pass

