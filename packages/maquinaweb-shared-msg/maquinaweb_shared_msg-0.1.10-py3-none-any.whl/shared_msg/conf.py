from django.conf import settings


def get_setting(name, default):
    """Retorna valor configurado no settings ou o padrão"""
    return getattr(settings, name, default)


def get_db_router():
    return get_setting("SHARED_MSG_DEFAULT_DB", "auth_db")


MESSAGE_TABLE = get_setting("SHARED_MSG_MESSAGE_TABLE", "message_message")
CONTACT_TABLE = get_setting("SHARED_MSG_CONTACT_TABLE", "message_contact")
EMAIL_TABLE = get_setting("SHARED_MSG_EMAIL_TABLE", "message_email")
PHONE_TABLE = get_setting("SHARED_MSG_PHONE_TABLE", "message_phone")
