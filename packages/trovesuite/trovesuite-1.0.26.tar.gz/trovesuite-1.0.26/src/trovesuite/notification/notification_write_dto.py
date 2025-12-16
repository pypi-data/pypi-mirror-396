from pydantic import BaseModel
from .notification_base import (
    NotificationEmailBase,
    NotificationSMSBase
)

# Email Notification

class NotificationEmailControllerWriteDto(NotificationEmailBase):
    pass

class NotificationEmailServiceWriteDto(NotificationEmailControllerWriteDto):
    pass

# SMS Notification

class NotificationSMSControllerWriteDto(NotificationSMSBase):
    pass

class NotificationSMSServiceWriteDto(BaseModel):
    pass