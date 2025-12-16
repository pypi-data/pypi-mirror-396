from .notification_base import (
    NotificationEmailBase,
    NotificationSMSBase
)
from pydantic import BaseModel

# EMAIL Notification

class NotificationEmailControllerReadDto(NotificationEmailBase):
    pass

class NotificationEmailServiceReadDto(BaseModel):
    pass

# SMS Notification

class NotificationSMSControllerReadDto(NotificationSMSBase):
    pass

class NotificationSMSServiceReadDto(BaseModel):
    pass
