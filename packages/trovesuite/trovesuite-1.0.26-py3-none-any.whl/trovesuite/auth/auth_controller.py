from fastapi import APIRouter
from .auth_write_dto import AuthControllerWriteDto
from .auth_read_dto import AuthControllerReadDto
from .auth_service import AuthService
from ..entities.sh_response import Respons

auth_router = APIRouter(tags=["Auth"])

@auth_router.post("/auth", response_model=Respons[AuthControllerReadDto])
async def authorize(data: AuthControllerWriteDto):
    return AuthService.authorize(data=data)