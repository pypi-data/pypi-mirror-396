import logging

from zappa.asynchronous import task

from shared_msg.conf import get_setting
from shared_msg.message.services.twilio_service import _send_twilio_message
from shared_msg.message.utils import MessageTypes
from shared_msg.message.utils.build_email_message import build_email_message
from shared_msg.models import Contact, Email, Message, Phone

logger = logging.getLogger(__name__)


@task
def send_message(
    contacts_ids: list[int] | int,
    type: MessageTypes,
    template: str,
    context,
    message_pk: str | None = None,
):
    message = Message.objects.filter(pk=message_pk).first()
    contacts = Contact.objects.filter(id__in=contacts_ids)

    try:
        if type == MessageTypes.EMAIL:
            emails = Email.objects.filter(contact__in=contacts).values_list(
                "email", flat=True
            )
            email_message = build_email_message(
                emails=emails,
                from_email=context.get("from_email", get_setting("DEFAULT_FROM_EMAIL")),
                subject=context.get("subject", ""),
                context=context,
                template=template,
            )
            email_message.send()
        elif type in (MessageTypes.SMS, MessageTypes.WHATSAPP):
            phones = Phone.objects.filter(contact__in=contacts, type=type).values_list(
                "number", flat=True
            )
            _send_twilio_message(phones, type, template, context)
        else:
            raise ValueError(f"Unsupported message type: {type}")

        if message:
            message.status = Message.Status.SENT
            message.save(update_fields=["status"])
    except Exception:
        logger.exception("Error sending %s message", type)
        if message:
            message.status = Message.Status.FAILED
            message.save(update_fields=["status"])
        raise

    return True
