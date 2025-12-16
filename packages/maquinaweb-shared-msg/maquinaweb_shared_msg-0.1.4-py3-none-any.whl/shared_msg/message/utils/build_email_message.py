import logging
from typing import Mapping, Sequence

from django.core.mail import EmailMessage
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def build_email_message(
    emails: Sequence[str] | None,
    from_email: str,
    subject: str,
    context: Mapping,
    template: str,
):
    if not emails:
        raise ValueError("Emails are required in context")

    html_message = render_to_string(template, context)

    email_message = EmailMessage(
        subject,
        body=None,
        from_email=from_email,
        to=list(emails),
    )
    email_message.content_subtype = "html"
    email_message.body = html_message

    return email_message
