from typing import List, Optional, Union
from pydantic import BaseModel

class NotificationEmailBase(BaseModel):
    sender_email: str
    receiver_email: Union[str, List[str]]
    password: str
    subject: str
    text_message: str
    html_message: Optional[str] = None

class NotificationSMSBase(BaseModel):
    pass