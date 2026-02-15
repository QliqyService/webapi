from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from app.db import Database
from app.deployment import get_faststream_queue_name_by_app_name
from app.schemas.amqp_events.messages import AddMessageToSessionEventSchema
from app.schemas.project_triggers_amqp import AMQPMatchEventToTriggerSchema
from app.services import Services
from app.settings import ServiceName, get_settings


__all__ = ["BaseManager"]


if TYPE_CHECKING:
    from app.db.models import ProjectEventTrigger


class BaseManager:
    """Base manager for all manager."""

    settings = get_settings()

    @staticmethod
    async def is_autoassign_enabled(project_id: UUID) -> bool:
        """Use autoassign for the project"""

        return await Database.settings.chats.is_autoassign_enabled(project_id=project_id)

    @staticmethod
    async def get_session_response_time_to_client_message_info(project_id: UUID) -> tuple[bool, int]:
        """Get session response time to client message settings"""

        chats_settings_db = await Database.settings.chats.get(project_id=project_id)
        return (
            chats_settings_db.session_response_time_to_client_message_enabled,
            chats_settings_db.session_max_response_time_to_client_message_seconds,
        )

    @staticmethod
    async def use_working_schedule(project_id: UUID) -> bool:
        """Use working schedule for the project"""

        return await Database.projects.use_working_schedule(project_id=project_id)

    @classmethod
    async def async_match_event_to_triggers(
        cls,
        project_id: UUID,
        event_type: "ProjectEventTrigger.EventType",
        data: dict[str, Any],
    ) -> None:
        """Send event to triggers

        Args:
            project_id (UUID): Project ID
            event_type (ProjectEventTrigger.EventType): Event type
            data (dict[str, Any]): Event data
        """

        sent_at = datetime.now(tz=timezone.utc).replace(tzinfo=None)
        queue = get_faststream_queue_name_by_app_name(
            app_name=ServiceName.BACKEND_API,
            app_stand=cls.settings.APP_STAND,
            current_app_name=cls.settings.APP_NAME,
            value="match_event_to_triggers",
        )
        message = AMQPMatchEventToTriggerSchema(
            id=uuid4(),
            project_id=project_id,
            event_type=event_type,
            request_data=data,
            sent_at=sent_at,
        )

        await Services.broker.publish(
            queue=queue,
            message=message.model_dump(mode="json"),
        )

    @classmethod
    async def async_publish_message_to_create(
        cls,
        project_id: UUID,
        chat_id: UUID,
        text: str,
        session_id: UUID,
        is_notify: bool = True,
    ) -> None:
        """Publish message to the message queue to create.
        Args:
            project_id (UUID): The ID of the project
            chat_id (UUID): The ID of the chat
            text (str): The text of the message
            session_id (UUID): The ID of the session
            is_notify (bool): Whether to notify about the message
        Returns:
            None
        """

        queue = get_faststream_queue_name_by_app_name(
            app_name=ServiceName.BACKEND_API,
            app_stand=cls.settings.APP_STAND,
            current_app_name=cls.settings.APP_NAME,
            value="add_message_to_session",
        )

        message = AddMessageToSessionEventSchema(
            id=uuid4(),
            project_id=project_id,
            chat_id=chat_id,
            text=text,
            session_id=session_id,
            is_notify=is_notify,
        )

        await Services.broker.publish(
            queue=queue,
            message=message.model_dump(mode="json"),
        )

    @staticmethod
    async def push_session_to_que_smart(
        project_id: UUID, chat_id: UUID, session_id: UUID, is_transfer_to_group: bool = False
    ) -> None:
        """
        Push session to QueSmart service with associated tags.

        Args:
            project_id (UUID): The ID of the project
            chat_id (UUID): The ID of the chat
            session_id (UUID): The ID of the session to push
            is_transfer_to_group (bool): Flag - Is it the transfer to the whole group? By default - false.

        Returns:
            None

        This method:
        1. Retrieves chat and session tag IDs from the database
        2. Pushes the session information to QueSmart service with associated tags
        """
        (
            chat_tag_ids,
            session_tag_ids,
            operator_tag_ids,
        ) = await Database.que_smart_assignments.get_tags_info_for_chat_session(
            project_id=project_id,
            session_id=session_id,
            chat_id=chat_id,
        )

        await Services.que_smart_client.push(
            project_id=project_id,
            chat_id=chat_id,
            session_id=session_id,
            chat_tag_ids=chat_tag_ids,
            session_tag_ids=session_tag_ids,
            operator_tag_ids=operator_tag_ids,
            is_transfer_to_group=is_transfer_to_group,
        )

    @classmethod
    async def has_free_slot_at_operator(cls, operator_id: UUID, project_id: UUID) -> bool:
        """Проверяет, есть ли у оператора свободный слот для нового чата.

        Args:
            operator_id (UUID): ID оператора
            project_id (UUID): ID проекта

        Returns:
            bool: True если у оператора есть свободный слот, False в противном случае
        """
        chats_settings_db = await Database.settings.chats.get(project_id=project_id)
        active_sessions_count = await Database.operators.get_active_session_count_for_validate(
            project_id=project_id,
            operator_id=operator_id,
        )
        return active_sessions_count < chats_settings_db.operator_max_active_chats
