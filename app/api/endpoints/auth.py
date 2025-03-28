import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Any

from app.schemas.auth import UserCreate, Token, UserOut
from app.services.auth_service import AuthService
from app.services.session.auth_session_service import AuthSessionService
from app.services.session.eclass_session_manager import EclassSessionManager
from app.api.deps import get_auth_service, get_auth_session_service, get_eclass_session_manager, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


@router.post("/register", response_model=UserOut)
async def register(
        user_in: UserCreate,
        auth_service: AuthService = Depends(get_auth_service)
) -> Any:
    """새 사용자 등록"""
    # 이클래스 계정 검증
    is_valid = await auth_service.validate_eclass_credentials(user_in.eclass_username, user_in.eclass_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이클래스 계정 정보가 유효하지 않습니다."
        )

    # 사용자 등록
    result = await auth_service.register(
        email=user_in.email,
        password=user_in.password,
        eclass_username=user_in.eclass_username,
        eclass_password=user_in.eclass_password
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="회원가입 중 오류가 발생했습니다."
        )

    return result.get("user", {})


@router.post("/login", response_model=Token)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        auth_service: AuthService = Depends(get_auth_service),
        auth_session_service: AuthSessionService = Depends(get_auth_session_service)
) -> Any:
    """로그인 및 토큰 발급"""
    result = await auth_service.login(email=form_data.username, password=form_data.password)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 내부 세션 생성
    user_id = result.get("user", {}).get("id")
    user_email = result.get("user", {}).get("email")
    session_result = await auth_session_service.create_session(user_id, user_email)

    return {
        "access_token": session_result["access_token"],
        "token_type": "bearer",
        "user": result.get("user", {})
    }


@router.post("/logout")
async def logout(
        token: str = Depends(oauth2_scheme),
        auth_session_service: AuthSessionService = Depends(get_auth_session_service),
        eclass_session_manager: EclassSessionManager = Depends(get_eclass_session_manager),
        current_user: dict = Depends(get_current_user)
) -> Any:
    """로그아웃"""
    try:
        # 인증 세션 종료
        auth_result = await auth_session_service.end_session(token)

        # 이클래스 세션도 함께 종료
        user_id = current_user.get("id")
        if user_id:
            await eclass_session_manager.invalidate_session(user_id)

        # 이미 로그아웃된 상태 처리
        if not auth_result:
            return {"message": "이미 로그아웃된 상태입니다.", "status": "already_logged_out"}

        return {"message": "로그아웃 성공", "status": "success"}
    except Exception as e:
        # 오류 발생 시 처리
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/verify", response_model=UserOut)
async def verify_token(
        token: str = Depends(oauth2_scheme),
        session_service: AuthSessionService = Depends(get_auth_session_service)
) -> Any:
    """토큰 검증"""
    try:
        logger.info(f"토큰 검증 API 호출: {token[:10]}...")
        user = await session_service.verify_token(token)
        logger.debug(f"verify_token 결과: {user}")

        if not user:
            logger.warning("verify_token이 None 반환")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.info(f"토큰 검증 성공: {user}")
        return user

    except Exception as e:
        logger.error(f"토큰 검증 중 예외: {str(e)}")
        import traceback
        logger.error(f"상세 예외 정보: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )