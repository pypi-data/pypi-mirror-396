from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import gettext as _

from lacrei_models.utils.models import BaseModel, HashedAutoField

NOTIFICATION_STATUS = [
    ("pending", _("Envio pendente")),
    ("success", _("Sucesso")),
    ("error", _("Erro ao enviar")),
]


class Notification(BaseModel):
    id = HashedAutoField(primary_key=True)
    template_prefix = models.CharField(max_length=250)
    send_to = ArrayField(
        models.EmailField(),
        help_text=_("Lista de destinatários (email)"),
        verbose_name=_("Destinatários"),
    )
    subject = models.CharField(max_length=500, verbose_name=_("Assunto"))
    pickled_context = models.BinaryField(
        verbose_name=_("Contexto da mensagem"), null=True
    )
    json_context = models.JSONField(
        default=dict,
        encoder=DjangoJSONEncoder,
        verbose_name=_("Contexto da mensagem como JSON"),
    )
    status = models.CharField(
        choices=NOTIFICATION_STATUS, default="PENDING", max_length=30
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        help_text=_("Pessoa usuária que recebeu o email"),
        on_delete=models.deletion.CASCADE,
        verbose_name="Pessoa usuária",
        related_name="emails_received",
        null=True,
        blank=True,
    )
    error_message = models.TextField(
        null=True, blank=True, verbose_name=_("Mensagem de erro")
    )

    class Meta:
        app_label = "notification"
