"""
Models concretos para Contact, Email, Phone e Message
"""

from shared_auth.abstract_models.contact import (
    AbstractContact,
    AbstractEmail,
    AbstractMessage,
    AbstractPhone,
)
from shared_auth.conf import CONTACT_TABLE, EMAIL_TABLE, MESSAGE_TABLE, PHONE_TABLE


class Contact(AbstractContact):
    """
    Model READ-ONLY padrão da tabela organization_contact
    Contato de uma organização

    Para customizar, crie seu próprio model herdando de AbstractContact
    """

    class Meta(AbstractContact.Meta):
        db_table = CONTACT_TABLE


class Email(AbstractEmail):
    """
    Model READ-ONLY padrão da tabela organization_email
    Email de um contato

    Para customizar, crie seu próprio model herdando de AbstractEmail
    """

    class Meta(AbstractEmail.Meta):
        db_table = EMAIL_TABLE


class Phone(AbstractPhone):
    """
    Model READ-ONLY padrão da tabela organization_phone
    Telefone de um contato

    Para customizar, crie seu próprio model herdando de AbstractPhone
    """

    class Meta(AbstractPhone.Meta):
        db_table = PHONE_TABLE


class Message(AbstractMessage):
    """
    Model READ-ONLY padrão da tabela organization_message
    Mensagem de uma organização

    Para customizar, crie seu próprio model herdando de AbstractMessage
    """

    class Meta(AbstractMessage.Meta):
        db_table = MESSAGE_TABLE
