from typing import List, Dict, Any, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.repositories.base import BaseRepository
from app.models.notice import Notice


class NoticeRepository(BaseRepository[Notice]):
    """공지사항 리포지토리"""

    def __init__(self):
        super().__init__(Notice)

    async def get_by_course_id(self, db: AsyncSession, course_id: str) -> Sequence[Any]:
        """
        강의 ID로 공지사항 목록 조회
        반환값: 데이터베이스 모델 객체 목록 (스키마로 변환 필요)
        """
        query = select(self.model).filter(self.model.course_id == course_id).order_by(self.model.date.desc())
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_article_id(self, db: AsyncSession, course_id: str, article_id: str) -> Optional[Any]:
        """
        게시글 ID로 공지사항 조회
        반환값: 데이터베이스 모델 객체 또는 None (스키마로 변환 필요)
        """
        query = select(self.model).filter(
            self.model.course_id == course_id,
            self.model.article_id == article_id
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def exists(self, db: AsyncSession, course_id: str, article_id: str) -> bool:
        """
        공지사항 존재 여부 확인
        반환값: 불리언 값 (True/False)
        """
        query = select(self.model).filter(
            self.model.course_id == course_id,
            self.model.article_id == article_id
        )
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None