"""
Abstract models para Contact, Email, Phone e Message
"""

from django.db import models


class AbstractContact(models.Model):
    """
    Model abstrato READ-ONLY da tabela organization_contact
    Contato de uma organização

    Para customizar, configure:
    SHARED_AUTH_CONTACT_MODEL = 'seu_app.CustomContact'
    """

    name = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        abstract = True
        verbose_name = "Contato"
        verbose_name_plural = "Contatos"

    def __str__(self):
        return self.name


class AbstractEmail(models.Model):
    """
    Model abstrato READ-ONLY da tabela organization_email
    Email de um contato

    Para customizar, configure:
    SHARED_AUTH_EMAIL_MODEL = 'seu_app.CustomEmail'
    """

    email = models.CharField(max_length=200, db_index=True)
    contact = models.ForeignKey(
        AbstractContact, on_delete=models.CASCADE, related_name="emails"
    )

    class Meta:
        abstract = True
        verbose_name = "Email"
        verbose_name_plural = "Emails"

    def __str__(self):
        return self.email


class AbstractPhone(models.Model):
    """
    Model abstrato READ-ONLY da tabela organization_phone
    Telefone de um contato

    Para customizar, configure:
    SHARED_AUTH_PHONE_MODEL = 'seu_app.CustomPhone'
    """

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
    contact = models.ForeignKey(
        AbstractContact, on_delete=models.CASCADE, related_name="phones"
    )

    class Meta:
        abstract = True
        verbose_name = "Telefone"
        verbose_name_plural = "Telefones"

    def __str__(self):
        return f"{self.phone_type} - {self.number}"


class AbstractMessage(models.Model):
    """
    Model abstrato READ-ONLY da tabela organization_message
    Mensagem de uma organização

    Para customizar, configure:
    SHARED_AUTH_MESSAGE_MODEL = 'seu_app.CustomMessage'
    """

    class Types(models.TextChoices):
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        WHATSAPP = "whatsapp", "WhatsApp"

    class Status(models.TextChoices):
        PENDING = "pending", "Pendente"
        SENT = "sent", "Enviado"
        FAILED = "failed", "Falhou"

    contact = models.ForeignKey(
        AbstractContact,
        on_delete=models.CASCADE,
        related_name="messages",
        null=True,
        blank=True,
    )
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
        verbose_name = "Mensagem"
        verbose_name_plural = "Mensagens"
