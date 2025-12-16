from django.conf import settings


def get_setting(name, default):
    """Retorna valor configurado no settings ou o padrão"""
    return getattr(settings, name, default)


def get_db_router():
    return get_setting("SHARED_AUTH_DB_ROUTER", "default")
