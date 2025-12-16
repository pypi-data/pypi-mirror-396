from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext as _

from lacrei_models.utils.models import BaseModel, HashedAutoField
from lacrei_models.utils.validators import (
    BRCPFValidator,
    OnlyUpperCaseAndNumbersValidator,
)

NULLABLE = {"null": True, "blank": True}


class Agreement(BaseModel):
    id = HashedAutoField(primary_key=True)
    user = models.ForeignKey(
        "client.User",
        on_delete=models.CASCADE,
        related_name="agreements",
        verbose_name=_("Usuário"),
    )
    name = models.CharField(
        max_length=100, verbose_name=_("Nome do Convênio e/ou plano")
    )
    user_name = models.CharField(
        max_length=100, verbose_name=_("Nome da pessoa beneficiária")
    )
    registration_number = models.CharField(
        max_length=50, verbose_name=_("Matrícula da pessoa beneficiária")
    )
    expiration_date = models.DateField(
        verbose_name=_("Validade (opcional)"), null=True, blank=True
    )
    user_cpf = models.CharField(
        max_length=50,
        verbose_name=_("CPF da pessoa beneficiária"),
        validators=[BRCPFValidator()],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "registration_number"],
                name="unique_name_registration_number",
            )
        ]
        ordering = ["-created_at"]
        app_label = "appointments"


class Appointment(BaseModel):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELED = "canceled"
    COMPLETED = "completed"
    SCHEDULE_STATUS = [
        (PENDING, _("Agendamento Pendente")),
        (CONFIRMED, _("Confirmado")),
        (CANCELED, _("Cancelado")),
        (COMPLETED, _("Realizada")),
    ]
    IN_PERSON = "in_person"
    ONLINE = "online"
    APPOINTMENT_TYPE = [
        (IN_PERSON, _("Presencial")),
        (ONLINE, _("Online")),
    ]
    id = HashedAutoField(primary_key=True)
    professional = models.ForeignKey(
        "professional.Professional",
        on_delete=models.CASCADE,
        related_name="appointments",
        verbose_name=_("Profissional"),
    )
    user = models.ForeignKey(
        "client.User",
        on_delete=models.CASCADE,
        related_name="appointments",
        verbose_name=_("Usuário"),
    )
    date = models.DateTimeField(verbose_name=_("Data da Consulta"))
    status = models.CharField(
        choices=SCHEDULE_STATUS,
        default=PENDING,
        verbose_name=_("Status da Consulta"),
    )
    type = models.CharField(
        max_length=10,
        choices=APPOINTMENT_TYPE,
        default=IN_PERSON,
        verbose_name=_("Tipo da Consulta"),
    )
    rescheduled = models.BooleanField(
        default=False, verbose_name=("verificação de reagendamento da consulta")
    )
    google_calendar_event_id = models.CharField(
        max_length=50,
        verbose_name=_("ID de integração com o google calendar"),
        null=True,
    )
    external_reference = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("Referência Externa (Asaas)"),
    )
    agreement = models.ForeignKey(
        Agreement,
        on_delete=models.PROTECT,
        verbose_name=_("Convênio"),
        null=True,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("professional", "date"),
                condition=~Q(status="canceled"),
                name="unique_professional_appointment_non_canceled",
            ),
            models.UniqueConstraint(
                fields=("user", "date"),
                condition=~Q(status="canceled"),
                name="unique_user_appointment_non_canceled",
            ),
        ]
        app_label = "appointments"
        db_table = "lacreiid_appointment"


class Report(BaseModel):
    id = HashedAutoField(primary_key=True)
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="reports",
        verbose_name=_("Consulta"),
    )

    created_by_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        limit_choices_to={"model__in": ["user", "professional"]},
        verbose_name=_("Tipo de Usuário"),
        null=True,
    )
    created_by_object_id = models.CharField(
        max_length=32, verbose_name=_("ID de Usuário"), null=True
    )
    created_by = GenericForeignKey("created_by_content_type", "created_by_object_id")

    feedback = models.CharField(max_length=255, verbose_name=_("Feedback da consulta"))
    eval = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Nota da consulta"),
    )

    class Meta:
        app_label = "appointments"
        db_table = "lacreiid_report"


class Cancellation(BaseModel):
    id = HashedAutoField(primary_key=True)
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="cancellations",
        verbose_name=_("Consulta"),
    )

    created_by_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        limit_choices_to={"model__in": ["user", "professional"]},
        verbose_name=_("Tipo de Usuário"),
        null=True,
    )
    created_by_object_id = models.CharField(
        max_length=32, verbose_name=_("ID de Usuário"), null=True
    )
    created_by = GenericForeignKey("created_by_content_type", "created_by_object_id")

    reason = models.CharField(max_length=255, verbose_name=_("Motivo"))

    class Meta:
        app_label = "appointments"
        db_table = "lacreiid_cancellation"


class Partner(BaseModel):
    id = HashedAutoField(primary_key=True)
    name = models.CharField(
        max_length=50,
        verbose_name=_("Nome do Parceiro"),
    )

    def __str__(self):
        return self.name

    class Meta:
        app_label = "appointments"


class CouponManager(models.Manager):
    pass


class Coupon(BaseModel):
    id = HashedAutoField(primary_key=True)
    code = models.CharField(
        max_length=20,
        validators=[OnlyUpperCaseAndNumbersValidator()],
        verbose_name=_("Código do cupom"),
    )
    discount = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name=_("Porcentagem de desconto"),
    )
    limit_date = models.DateField(
        null=True, blank=True, verbose_name=_("Validade do cupom")
    )
    usages_limit = models.IntegerField(
        validators=[MinValueValidator(1)], verbose_name=_("Limite de usos")
    )
    usages = models.IntegerField(default=0, verbose_name=_("Usos"))
    partner = models.ForeignKey(
        Partner,
        on_delete=models.SET_NULL,
        verbose_name=_("Nome do parceiro"),
        null=True,
        blank=True,
    )

    objects = CouponManager()

    class Meta:
        app_label = "appointments"
        db_table = "lacreiid_coupon"
