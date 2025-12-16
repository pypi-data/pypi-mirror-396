from django.db import models

from shared_msg.conf import get_setting
from shared_msg.message.utils import MessageTypes
from shared_msg.models import Contact


class ContactMixin(models.Model):
    contact_id = models.IntegerField(null=True, blank=True, db_index=True)

    class Meta:
        abstract = True

    @property
    def contact(self):
        return Contact.objects.get(id=self.contact_id)

    def send_message(
        self,
        type: MessageTypes,
        template: str,
        context: dict = {},
        from_email: str = get_setting("DEFAULT_FROM_EMAIL", ""),
        subject: str = "",
        message_pk: str | None = None,
    ):
        from shared_msg.message.utils.send_message import (
            send_message as send_message_utils,
        )

        send_message_utils(
            self.contact_id,
            type,
            template,
            context,
            from_email,
            subject,
            message_pk,
        )
