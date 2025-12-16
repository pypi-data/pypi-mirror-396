from .notification_write_dto import (
    NotificationEmailControllerWriteDto,
    NotificationSMSControllerWriteDto
)
from .notification_read_dto import (
    NotificationEmailControllerReadDto,
    NotificationSMSControllerReadDto
)
from .notification_service import NotificationService
from ..entities.sh_response import Respons
from fastapi import APIRouter

notification_router = APIRouter(tags=["Notification"])

@notification_router.post("/send_email", response_model=Respons[NotificationEmailControllerReadDto])
async def send_email(data: NotificationEmailControllerWriteDto):
    return NotificationService.send_email(data=data)

@notification_router.post("/send_sms", response_model=Respons[NotificationSMSControllerReadDto])
async def send_sms(data: NotificationSMSControllerWriteDto):
    return NotificationService.send_sms(data=data)