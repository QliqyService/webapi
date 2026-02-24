import uuid
from uuid import UUID

from loguru import logger as LOGGER

from app.db import UserFormsDb, UsersDb
from app.db.crud.comments import CommentsDb
from app.dependencies.exceptions import RequestedDataNotFoundException
from app.schemas.comments.comments import CommentsCreateSchema, CommentsSchema, CommentsUpdateSchema
from app.services import Services
from app.settings import SETTINGS, ServiceName


class CommentsManager:
    @staticmethod
    async def create(user_form_id: UUID, comment_data: CommentsCreateSchema) -> CommentsSchema:
        created = await CommentsDb.create(user_form_id=user_form_id, comment=comment_data)

        try:
            form = await UserFormsDb().get(form_id=user_form_id)
        except Exception:
            LOGGER.exception("Failed to load form for notifications")
            return created

        try:
            owner = await UsersDb().get(user_id=form.user_id)
        except Exception:
            LOGGER.exception("Failed to load owner for notifications")
            return created

        base = SETTINGS.FORMS_PUBLIC_DOMAIN_URL
        form_public_url = f"{base}/{form.id}" if base else None

        created_at = getattr(created, "created_at", None)

        common_event = {
            "event_id": str(uuid.uuid4()),
            "event_type": "comment_created",
            "created_at": created_at,
            "form_id": str(user_form_id),
            "form_title": getattr(form, "title", None),
            "form_public_url": form_public_url,
            "comment_id": str(created.id),
            "comment_title": getattr(comment_data, "title", None),
            "comment_text": getattr(comment_data, "description", None),
            "comment_author_first_name": getattr(comment_data, "first_name", None),
            "comment_author_last_name": getattr(comment_data, "last_name", None),
            "comment_author_phone": (
                str(getattr(comment_data, "phone", None)) if getattr(comment_data, "phone", None) else None
            ),
        }

        try:
            queue_name = f"{SETTINGS.APP_STAND}::{ServiceName.TELEGRAM}::comment_created"

            if not owner.tg_account:
                LOGGER.info("Telegram was not assigned. Skipping notification. Comment created.")
            else:
                tg_event = {**common_event, "tg_account": owner.tg_account}
                ok = await Services.rabbitmq.publish(queue=queue_name, message=tg_event)
                if not ok:
                    LOGGER.warning("Telegram notify publish failed (comment still created)")

        except Exception:
            LOGGER.exception("Telegram notify publish exception (comment still created)")

        try:
            if getattr(owner, "notify_email_enabled", False):
                recipient = getattr(owner, "notify_email", None) or owner.email
                mail_queue = f"{SETTINGS.APP_STAND}::{ServiceName.MAIL}::comment_created"

                mail_event = {**common_event, "recipient_email": recipient}
                ok = await Services.rabbitmq.publish(queue=mail_queue, message=mail_event)
                if not ok:
                    LOGGER.warning("Mail notify publish failed (comment still created)")

        except Exception:
            LOGGER.exception("Mail notify publish exception (comment still created)")

        return created

    @staticmethod
    async def get_comment(comment_id: UUID) -> CommentsSchema:
        comment = await CommentsDb.get(comment_id=comment_id)
        if not comment:
            raise RequestedDataNotFoundException("Comment not found")
        return comment

    @staticmethod
    async def get_list(user_form_id: UUID) -> list[CommentsSchema]:
        return await CommentsDb.get_list(user_form_id=user_form_id)

    @staticmethod
    async def update(comment_id: UUID, comment_data: CommentsUpdateSchema) -> CommentsSchema:
        comment = await CommentsDb.update(comment_id=comment_id, comment_data=comment_data)
        if not comment:
            raise RequestedDataNotFoundException("Comment not found")
        return comment

    @staticmethod
    async def delete(comment_id: UUID) -> CommentsSchema:
        comment = await CommentsDb.delete(comment_id=comment_id)
        if not comment:
            raise RequestedDataNotFoundException("Comment not found")
        return comment
