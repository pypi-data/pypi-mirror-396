from django.db import models
from django.utils.translation import gettext as _

from lacrei_models.utils.models import BaseModel, HashedAutoField

NULLABLE = {"null": True, "blank": True}


class GoogleAccount(BaseModel):

    id = HashedAutoField(primary_key=True, verbose_name=_("ID"))
    user = models.ForeignKey(
        "client.User",
        on_delete=models.CASCADE,
        related_name="google_accounts",
        verbose_name=_("Usuário"),
    )
    access_token = models.TextField(verbose_name=_("Token de Acesso"))
    refresh_token = models.TextField(verbose_name=_("Token de Atualização"))
    expires_at = models.DateTimeField(verbose_name=_("Expira em"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Criado em"))

    class Meta:
        db_table = "lacreiid_google_account"
        verbose_name = _("Conta Google")
        verbose_name_plural = _("Contas Google")
        app_label = "sync"

    def __str__(self):
        return f"Google Account ({self.user.email})"


class GoogleCalendarEvent(BaseModel):
    id = HashedAutoField(primary_key=True)
    user = models.ForeignKey(
        "client.User",
        on_delete=models.CASCADE,
        verbose_name=_("Usuário"),
    )
    event_id = models.CharField(max_length=255, verbose_name=_("ID do Evento Google"))
    summary = models.CharField(max_length=255, verbose_name=_("Titulo"))
    description = models.TextField(**NULLABLE, verbose_name=_("Descrição"))
    start_time = models.DateTimeField(verbose_name=_("Início dop Evento"))
    end_time = models.DateTimeField(verbose_name=_("Fim do Evento"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Criado em"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atualizado em"))

    class Meta:
        db_table = "lacreiid_google_calendar_event"
        verbose_name = _("Evento do Google Calendar")
        verbose_name_plural = _("Eventos do Google Calendar")
        app_label = "sync"

    def __str__(self):
        return f"{self.summary} ({self.start_time})"
