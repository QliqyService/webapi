import base64
import uuid
from uuid import UUID

from loguru import logger as LOGGER

from app.db.crud.user_forms import UserFormsDb
from app.dependencies.exceptions import PermissionDeniedException, RequestedDataNotFoundException
from app.dependencies.exceptions.http import QRCodeGenerationException
from app.schemas.qrcode import QRRPCRequest, QRRPCResponse
from app.schemas.user_forms import (
    UserFormCreateSchema,
    UserFormSchemaWithoutQrcode,
    UserFormSchemaWithQrcode,
    UserFormUpdateSchema,
)
from app.services import Services
from app.services.qrcode_client import qr_client
from app.settings import SETTINGS, ServiceName


class UserFormManager:
    """Business logic for user forms."""

    @staticmethod
    async def create_form(
            user_id: UUID,
            data: UserFormCreateSchema,
    ) -> UserFormSchemaWithoutQrcode:
        created_form = await UserFormsDb().create(user_id=user_id, form=data)

        public_url = f"{SETTINGS.FORMS_PUBLIC_DOMAIN_URL}/{created_form.id}"

        try:
            queue_name = f"{SETTINGS.APP_STAND}::{ServiceName.QR_CODE}::get_qrcode"
            request_message = QRRPCRequest(
                id=uuid.uuid4(),
                url=public_url,
            )

            rpc_response = await Services.rabbitmq.request(
                queue=queue_name,
                message=request_message.model_dump(mode="json"),
            )

            if rpc_response is None:
                LOGGER.error("Не удалось получить QRcode")
                return created_form

            response_data = QRRPCResponse.model_validate_json(rpc_response.body)
            qrcode_bytes = base64.b64decode(response_data.body)

            await UserFormsDb().set_qrcode(
                form_id=created_form.id,
                qrcode=qrcode_bytes,
            )

        except Exception as e:
            LOGGER.exception("QR-code generation via RabbitMQ failed")
            raise QRCodeGenerationException(meta=str(e)) from e

        return created_form

    @staticmethod
    async def get_form(form_id: UUID, user_id: UUID) -> UserFormSchemaWithoutQrcode:
        form = await UserFormsDb().get(form_id=form_id)
        if not form:
            raise RequestedDataNotFoundException("Form not found")

        if form.user_id != user_id:
            raise PermissionDeniedException("You have no access to this form")

        return form

    @staticmethod
    async def get_list(user_id: UUID) -> list[UserFormSchemaWithQrcode]:
        forms = await UserFormsDb().get_list(user_id=user_id)
        for f in forms:
            f.qrcode = base64.b64encode(f.qrcode or b"").decode("ascii")
        return forms

    # Gets all (even disabled) forms
    @staticmethod
    async def get_all_forms(user_id: UUID) -> list[UserFormSchemaWithQrcode]:
        forms = await UserFormsDb().get_all_user_forms(user_id=user_id)
        for f in forms:
            f.qrcode = base64.b64encode(f.qrcode or b"").decode("ascii")
        return forms

    @staticmethod
    async def update_form(form_id: UUID, user_id: UUID, data: UserFormUpdateSchema) -> UserFormSchemaWithoutQrcode:
        form = await UserFormsDb().get(form_id=form_id)
        if not form:
            raise RequestedDataNotFoundException("Form not found")

        if form.user_id != user_id:
            raise PermissionDeniedException("You have no access to this form")

        updated = await UserFormsDb().update(form_id=form_id, form_data=data)
        return updated

    @staticmethod
    async def delete_form(form_id: UUID, user_id: UUID) -> UserFormSchemaWithoutQrcode:
        form = await UserFormsDb().get(form_id=form_id)
        if not form:
            raise RequestedDataNotFoundException("Form not found")

        if form.user_id != user_id:
            raise PermissionDeniedException("You have no access to this form")

        deleted = await UserFormsDb().delete(form_id=form_id)
        return deleted

    @staticmethod
    async def get_public_form(form_id: UUID) -> UserFormSchemaWithoutQrcode:
        """
        Get public form by ID without access Token.
        """
        form = await UserFormsDb().get(form_id=form_id)
        if not form:
            raise RequestedDataNotFoundException("Form not found")

        return form

    @staticmethod
    async def get_qrcode(form_id: UUID) -> bytes:
        form = await UserFormsDb.get(form_id=form_id)
        if not form:
            raise RequestedDataNotFoundException("Form not found")

        qrcode = await UserFormsDb.get_qrcode(form_id=form_id)
        if not qrcode:
            raise RequestedDataNotFoundException("QR code not found")

        return qrcode
