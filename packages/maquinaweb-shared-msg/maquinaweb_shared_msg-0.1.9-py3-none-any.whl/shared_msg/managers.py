from django.db import models

from shared_msg.conf import get_setting
from shared_msg.message.utils import MessageTypes
from shared_msg.message.utils.send_message import send_message


class ContactManager(models.Manager):
    def send_all_message(
        self,
        type: MessageTypes,
        template: str,
        context: dict = {},
        from_email: str = get_setting("DEFAULT_FROM_EMAIL", ""),
        subject: str = "",
        message_pk: str | None = None,
    ):
        if type is MessageTypes.EMAIL:
            emails = self.get_queryset().values_list("email", flat=True)
            send_message(
                list(emails), type, template, context, from_email, subject, message_pk
            )
        if type in (MessageTypes.SMS, MessageTypes.WHATSAPP):
            phones = self.get_queryset().values_list("phone", flat=True)
            send_message(
                list(phones), type, template, context, from_email, subject, message_pk
            )
