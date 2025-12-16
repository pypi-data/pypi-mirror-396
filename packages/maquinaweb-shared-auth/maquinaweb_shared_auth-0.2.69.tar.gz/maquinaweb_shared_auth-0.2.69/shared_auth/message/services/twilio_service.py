import json
import logging
from typing import Mapping

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from shared_auth.conf import get_setting
from shared_auth.message.utils import MessageTypes
from shared_auth.message.utils.build_sms_message import build_sms_message
from shared_auth.message.utils.build_whatsapp_message import build_whatsapp_message

logger = logging.getLogger(__name__)


def _normalize_number(number: str, *, whatsapp: bool = False) -> str:
    value = str(number or "").strip()
    if not value:
        raise ValueError("Phone number is required")
    value = value.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not value.startswith("+"):
        value = f"+55{value}"
    if whatsapp and not value.startswith("whatsapp:"):
        value = f"whatsapp:{value}"
    return value


def _stringify_variables(variables: Mapping | None) -> str | None:
    if not variables:
        return None

    def _normalize_value(value):
        if value is None:
            return ""
        if isinstance(value, (dict, list, tuple, set)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)

    payload = {str(key): _normalize_value(val) for key, val in variables.items()}
    return json.dumps(payload, ensure_ascii=False)


class TwilioService:
    def __init__(self) -> None:
        if not get_setting("TWILIO_ACCOUNT_SID") or not get_setting(
            "TWILIO_AUTH_TOKEN"
        ):
            raise RuntimeError("Twilio credentials are not configured")

        self.client = Client(
            get_setting("TWILIO_ACCOUNT_SID"),
            get_setting("TWILIO_AUTH_TOKEN"),
        )

    def send_sms_text(self, *, phone: str, body: str) -> None:
        from_number = get_setting("TWILIO_SMS_FROM")
        if not from_number:
            raise RuntimeError("Twilio SMS sender number is not configured")

        payload = {
            "to": _normalize_number(phone),
            "from_": _normalize_number(from_number),
            "body": body,
        }

        self._dispatch(payload)

    def send_whatsapp_template(
        self,
        *,
        phone: str,
        content_sid: str,
        variables: Mapping | None = None,
        body: str | None = None,
    ) -> None:
        from_number = get_setting("TWILIO_WHATSAPP_FROM")
        if not from_number:
            raise RuntimeError("Twilio WhatsApp sender number is not configured")
        if not content_sid:
            raise ValueError("Twilio WhatsApp content SID is required")

        payload = {
            "to": _normalize_number(phone, whatsapp=True),
            "from_": _normalize_number(from_number, whatsapp=True),
            "content_sid": content_sid,
        }

        content_variables = _stringify_variables(variables)
        if content_variables:
            payload["content_variables"] = content_variables
        if body:
            payload["body"] = str(body)

        self._dispatch(payload)

    def _dispatch(self, payload: dict) -> None:
        try:
            self.client.messages.create(**payload)
        except TwilioRestException:
            logger.exception("Error sending Twilio message to %s", payload["to"])
            raise


def _normalize_phone_numbers(phone_field) -> list[str]:
    if not phone_field:
        return []
    if isinstance(phone_field, (list, tuple, set)):
        numbers = phone_field
    else:
        numbers = [phone_field]
    return [str(number).strip() for number in numbers if number]


def _send_twilio_message(
    contacts: list[str] | str, message_type: str, template: str, context: Mapping
) -> None:
    phones = _normalize_phone_numbers(contacts)

    if not phones:
        raise ValueError("Phone number is required for SMS/WhatsApp messages")

    service = TwilioService()

    if message_type == MessageTypes.SMS:
        body = build_sms_message(template, context)
        for phone in phones:
            service.send_sms_text(phone=phone, body=body)
        return

    if message_type == MessageTypes.WHATSAPP:
        content_sid, variables, fallback_body = build_whatsapp_message(
            template, message_type, context
        )
        if not content_sid:
            raise RuntimeError(
                f"Twilio content SID not configured for template {template} and type {message_type}"
            )

        for phone in phones:
            service.send_whatsapp_template(
                phone=phone,
                content_sid=content_sid,
                variables=variables,
                body=fallback_body,
            )
        return

    raise ValueError(f"Unsupported message type: {message_type}")
