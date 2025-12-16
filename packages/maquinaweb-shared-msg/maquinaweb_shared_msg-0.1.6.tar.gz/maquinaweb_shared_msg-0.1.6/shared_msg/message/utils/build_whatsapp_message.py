from typing import Mapping

from django.template.loader import render_to_string
from django.utils.html import strip_tags

from shared_msg.conf import get_setting


def _get_template_name(template: str) -> str:
    """Extrai o nome do template sem extensão para lookup de content SID."""
    return template.rsplit(".", 1)[0] if "." in template else template


def _resolve_content_sid(
    template: str, message_type: str, context: Mapping
) -> str | None:
    """
    Resolve o Twilio content SID para o template.

    Prioridade:
    1. Override via context["twilio_content_sid"]
    2. Configuração em TWILIO_CONTENT_SIDS no settings
    """
    override = context.get("twilio_content_sid")
    if isinstance(override, Mapping):
        sid = override.get(message_type)
        if sid:
            return str(sid)
    elif isinstance(override, str):
        return override

    template_name = _get_template_name(template)
    content_sids = get_setting("TWILIO_CONTENT_SIDS", {})
    return content_sids.get(template_name, {}).get(message_type)


def build_whatsapp_message(
    template: str, message_type: str, context: Mapping
) -> tuple[str | None, Mapping, str]:
    """
    Constrói mensagem WhatsApp usando template Django + Twilio content SID.

    Exemplo:
        build_whatsapp_message("whatsapp/welcome.html", "whatsapp", {"name": "João"})
    """
    content_sid = _resolve_content_sid(template, message_type, context)
    fallback_body = strip_tags(render_to_string(template, context)).strip()
    variables = context.get("twilio_variables", context)
    return content_sid, variables, fallback_body
