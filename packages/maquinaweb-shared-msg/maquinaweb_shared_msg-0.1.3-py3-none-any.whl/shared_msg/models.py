from django.db import models


class Contact(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        abstract = True
        managed = False


class Email(models.Model):
    email = models.CharField(max_length=200, db_index=True)
    contact_id = models.IntegerField()

    class Meta:
        abstract = True
        managed = False


class Phone(models.Model):
    class PhoneType(models.TextChoices):
        WHATSAPP = "whatsapp"
        SMS = "sms"

    phone_type = models.CharField(
        max_length=20,
        db_index=True,
        choices=PhoneType.choices,
        default=PhoneType.WHATSAPP,
    )
    number = models.CharField(max_length=20, db_index=True)
    contact_id = models.IntegerField()

    class Meta:
        abstract = True
        managed = False


class Message(models.Model):
    class Types(models.TextChoices):
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        WHATSAPP = "whatsapp", "WhatsApp"

    class Status(models.TextChoices):
        PENDING = "pending", "Pendente"
        SENT = "sent", "Enviado"
        FAILED = "failed", "Falhou"

    contact_id = models.IntegerField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    type = models.CharField(max_length=20, choices=Types.choices, default=Types.EMAIL)
    template = models.CharField(
        max_length=32,
        null=True,
        blank=True,
    )
    related_to = models.PositiveIntegerField(null=True, blank=True, db_index=True)

    class Meta:
        abstract = True
        managed = False
