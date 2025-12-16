from django.conf import settings


def get_setting(name, default):
    """Retorna valor configurado no settings ou o padrão"""
    return getattr(settings, name, default)
