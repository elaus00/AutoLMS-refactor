from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.auth_service import AuthService
from app.services.eclass_service import EclassService
from app.services.eclass_session import EclassSession
from app.services.eclass_parser import EclassParser
from app.services.file_handler import FileHandler
from app.core.supabase_client import get_supabase_client

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def get_auth_service() -> AuthService:
    """인증 서비스 제공"""
    return AuthService(get_supabase_client())

# 각 컴포넌트 의존성
def get_eclass_session() -> EclassSession:
    """EclassSession 제공"""
    return EclassSession()

def get_eclass_parser() -> EclassParser:
    """EclassParser 제공"""
    return EclassParser()

def get_file_handler() -> FileHandler:
    """FileHandler 제공"""
    return FileHandler()

# 통합 서비스 의존성
def get_eclass_service(
    session: EclassSession = Depends(get_eclass_session),
    parser: EclassParser = Depends(get_eclass_parser),
    file_handler: FileHandler = Depends(get_file_handler)
) -> EclassService:
    """EclassService 제공"""
    return EclassService(session=session, parser=parser, file_handler=file_handler)

# 사용자 인증 의존성
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
):
    """현재 로그인한 사용자 확인"""
    return await auth_service.get_current_user(token)

# 데이터베이스 세션 의존성
async def get_db_session() -> Generator[AsyncSession, None, None]:
    """데이터베이스 세션 제공"""
    async with get_db() as session:
        yield session
