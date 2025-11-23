from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .core import AuthCore
from .schemas import TokenData

security = HTTPBearer()

def create_get_current_user(auth_core: AuthCore):
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> TokenData:
        token_data = await auth_core.verify_token(credentials.credentials)
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return token_data
    return get_current_user

async def _legacy_get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="get_current_user must be created with create_get_current_user(auth_core)"
    )

get_current_user = _legacy_get_current_user

def create_get_current_active_user(auth_core: AuthCore, get_current_user_dep):
    async def get_current_active_user(
        current_user: TokenData = Depends(get_current_user_dep)
    ):
        user = await auth_core.user_service.get_user_by_id(current_user.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    return get_current_active_user

async def _legacy_get_current_active_user():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="get_current_active_user must be created with create_get_current_active_user(auth_core)"
    )

get_current_active_user = _legacy_get_current_active_user