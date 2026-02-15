from uuid import UUID

from sqlalchemy import delete, select, update

from app.db.crud.base import BaseDatabase
from app.db.models import Comment
from app.schemas.comments.comments import CommentsCreateSchema, CommentsSchema, CommentsUpdateSchema
from app.services import Services


class CommentsDb(BaseDatabase):
    """CRUD operations for comments."""

    @staticmethod
    async def create(user_form_id: UUID, comment: CommentsCreateSchema) -> CommentsSchema:
        """
        Create comment.

        Args:
            user_form_id (UUID): user form ID
            comment (CommentsCreateSchema): created comment

        Returns:
            CommentsSchema: comment data
        """
        data = comment.model_dump()
        data["user_form_id"] = user_form_id

        async with Services.database.session() as session:
            comment_db = Comment(**data)
            session.add(comment_db)
            await session.commit()
            await session.refresh(comment_db)

        return CommentsSchema.model_validate(comment_db, from_attributes=True)

    @staticmethod
    async def get(
        comment_id: UUID,
    ) -> CommentsSchema | None:
        """
        Get comment by comment ID.

        Args:
            comment_id (UUID): comment ID

        Returns:
            CommentsSchema: comment data
        """

        query = select(Comment).where(Comment.id == comment_id)
        async with Services.database.session() as session:
            result = await session.execute(query)
            comment_db = result.scalar_one_or_none()
        if not comment_db:
            return None
        return CommentsSchema.model_validate(comment_db, from_attributes=True)

    @staticmethod
    async def get_list(user_form_id: UUID) -> list[CommentsSchema]:
        """Get list of all comments for given form_id.

        Args:
            user_form_id (UUID): comment ID

        Returns:
            list[CommentsSchema]: list of comments
        """
        query = select(Comment).where(Comment.user_form_id == user_form_id).order_by(Comment.created_at.desc())
        async with Services.database.session() as session:
            result = await session.execute(query)
            comments_db = result.scalars().all()

        return [CommentsSchema.model_validate(comment_db, from_attributes=True) for comment_db in comments_db]

    @staticmethod
    async def update(comment_id: UUID, comment_data: CommentsUpdateSchema) -> CommentsSchema | None:
        """
        Update comment.

        Args:
            comment_id (UUID): ID of the comment
            comment_data (CommentsUpdateSchema): data of the comment to update

        Returns:
            CommentsSchema | None: updated comment if found, None otherwise
        """

        data = comment_data.model_dump(exclude_unset=True)

        async with Services.database.session() as session:
            result = await session.execute(
                update(Comment).where(Comment.id == comment_id).values(**data).returning(Comment)
            )
            await session.commit()
            comment_db = result.scalar_one_or_none()
        if not comment_db:
            return None

        return CommentsSchema.model_validate(comment_db, from_attributes=True)

    @staticmethod
    async def delete(comment_id: UUID) -> CommentsSchema | None:
        """Delete comment by its ID.

        Args:
            comment_id (UUID): comment ID

        Returns:
            CommentsSchema | None: disabled comment if found, None otherwise
        """
        async with Services.database.session() as session:
            result = await session.execute(delete(Comment).where(Comment.id == comment_id).returning(Comment))
            await session.commit()
            comment_db = result.scalar_one_or_none()
            if not comment_db:
                return None

        return CommentsSchema.model_validate(comment_db, from_attributes=True)
