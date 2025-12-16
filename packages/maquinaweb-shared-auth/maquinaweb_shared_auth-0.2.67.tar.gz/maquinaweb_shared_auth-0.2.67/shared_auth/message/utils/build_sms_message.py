from typing import Mapping

from django.template.loader import render_to_string
from django.utils.html import strip_tags


def build_sms_message(template: str, context: Mapping) -> str:
    """
    Renderiza template SMS usando o sistema de templates do Django.

    Exemplo:
        build_sms_message("sms/verification_code.txt", {"code": "123456"})
    """
    rendered = render_to_string(template, context)
    return strip_tags(rendered).strip()
