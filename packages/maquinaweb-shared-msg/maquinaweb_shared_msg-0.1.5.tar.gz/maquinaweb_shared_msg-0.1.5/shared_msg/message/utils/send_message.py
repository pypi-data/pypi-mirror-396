import logging

from zappa.asynchronous import task

from shared_msg.conf import get_setting
from shared_msg.message.services.twilio_service import _send_twilio_message
from shared_msg.message.utils import MessageTypes
from shared_msg.message.utils.build_email_message import build_email_message
from shared_msg.models import Contact, Email, Phone

logger = logging.getLogger(__name__)


@task
def send_message(
    contacts: list[Contact] | Contact,
    type: MessageTypes,
    template: str,
    context,
    message_pk: str | None = None,
):
    from shared_msg.utils import get_message_model

    Message = get_message_model()

    message = Message.objects.filter(pk=message_pk).first()

    try:
        if type == MessageTypes.EMAIL:
            emails = Email.objects.filter(contact__in=contacts)
            email_message = build_email_message(
                emails=emails,
                from_email=context.get("from_email", get_setting("DEFAULT_FROM_EMAIL")),
                subject=context.get("subject", ""),
                context=context,
                template=template,
            )
            email_message.send()
        elif type in (MessageTypes.SMS, MessageTypes.WHATSAPP):
            phones = Phone.objects.filter(contact__in=contacts, type=type)
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
