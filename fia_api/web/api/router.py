from fastapi.routing import APIRouter

from fia_api.web.api import dummy, echo, monitoring, redis, teacher, user

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(dummy.router, prefix="/dummy", tags=["dummy"])
api_router.include_router(redis.router, prefix="/redis", tags=["redis"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(teacher.router, prefix="/teacher", tags=["teacher"])
