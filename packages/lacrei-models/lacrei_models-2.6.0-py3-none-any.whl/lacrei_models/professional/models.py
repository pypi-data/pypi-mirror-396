from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _
from phonenumber_field.modelfields import PhoneNumberField
from watson import search as watson

from lacrei_models.client.models import NULLABLE, BaseProfile
from lacrei_models.professional.services.verification import (
    BoardRegistrationNumber,
    PostRegistrationData,
    VerificationStepsService,
)
from lacrei_models.utils.models import BaseModel, HashedAutoField, HashedFileName
from lacrei_models.utils.validators import BRCPFValidator, OnlyAlphabeticValidator

CONTACT_REQUEST_SMS_MESSAGE = "Código Lacrei Saúde: {validation_code}. Não compartilhe."


PROFILE_STATUS = [
    ("pending", _("Informações pendentes")),
    ("in_review", _("Em revisão")),
    ("rejected", _("Rejeitado")),
    ("approved", _("Aprovado")),
]

VERIFICATION_STEPS_MAP = {
    "board_registration_number": {
        "choice_description": "1º etapa - Numero de inscrição",
        "verification_step": BoardRegistrationNumber,
    },
    "post_registration_data": {
        "choice_description": "2º etapa - Pós cadastro",
        "verification_step": PostRegistrationData,
    },
}
VERIFICATION_STEPS_CHOICES = (
    (key, value["choice_description"]) for key, value in VERIFICATION_STEPS_MAP.items()
)


class Profession(BaseModel):
    name = models.CharField(max_length=100)
    search_synonym = models.CharField(max_length=256, default=None, **NULLABLE)

    class Meta:
        verbose_name = _("Profissão")
        verbose_name_plural = _("Profissões")
        app_label = "professional"
        db_table = "lacreisaude_profession"

    def __str__(self):
        return self.name


class WaitingList(BaseModel):
    email = models.EmailField()
    profession = models.ForeignKey(Profession, on_delete=models.PROTECT)
    state = models.ForeignKey("address.State", on_delete=models.PROTECT)

    class Meta:
        verbose_name = _("Lista de espera")
        verbose_name_plural = _("Listas de espera")
        app_label = "professional"
        db_table = "lacreisaude_waitinglist"


class Professional(BaseProfile):
    CPF = "CPF"
    CNPJ = "CNPJ"
    EMAIL = "EMAIL"
    CELULAR = "PHONE"
    EVP = "EVP"
    tipo_chave = [
        (CPF, _("CPF")),
        (CNPJ, _("CNPJ")),
        (EMAIL, _("EMAIL")),
        (CELULAR, _("PHONE")),
        (EVP, _("EVP")),
    ]
    id = HashedAutoField(primary_key=True)
    user = models.OneToOneField("client.User", on_delete=models.PROTECT)
    full_name = models.CharField(
        max_length=200,
        verbose_name=_("Nome completo"),
        validators=[OnlyAlphabeticValidator()],
    )
    about_me = models.TextField(**NULLABLE, verbose_name=_("Sobre mim"))
    profile_status = models.CharField(
        max_length=30,
        choices=PROFILE_STATUS,
        default="pending",
        verbose_name=_("Status do perfil"),
    )
    state = models.ForeignKey(
        "address.State", on_delete=models.PROTECT, verbose_name=_("Estado")
    )
    active = models.BooleanField(
        default=False,
        help_text=(
            _("Define se o perfil está ativo e pode ser alterado pelos administradores")
        ),
        verbose_name=_("Ativo"),
    )
    published = models.BooleanField(
        default=True,
        help_text=(
            _(
                "Define se o perfil está publicado "
                "e pode ser alterado pelo próprio profissional"
            )
        ),
        verbose_name=_("Publicado"),
    )
    document_number = models.CharField(
        max_length=20, **NULLABLE, validators=[BRCPFValidator()], verbose_name=_("CPF")
    )
    profession = models.ForeignKey(
        Profession,
        related_name="professionals",
        on_delete=models.PROTECT,
        verbose_name=_("Profissão"),
    )
    search_synonym = models.CharField(max_length=256, default=None, **NULLABLE)
    board_registration_number = models.CharField(
        max_length=100, verbose_name=_("Número do registro do conselho")
    )
    accepted_privacy_document = models.BooleanField(
        default=False, verbose_name=_("Documento de privacidade aceito")
    )
    privacy_document = models.ForeignKey(
        "client.PrivacyDocument",
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        verbose_name=_("Documento de privacidade"),
    )
    safety_measures = models.CharField(
        max_length=1000,
        **NULLABLE,
        help_text=_("Medidas de segurança do Covid, por exemplo"),
        verbose_name=_("Medidas de segurança"),
    )
    specialty = models.CharField(
        **NULLABLE,
        max_length=250,
        help_text=_("Especialidade da pessoa profissional, como cardiologia"),
        verbose_name=_("Especialidade clínica"),
    )
    specialty_number_rqe = models.CharField(
        **NULLABLE,
        max_length=10,
        help_text=_("Registro de Qualificação de Especialidade (RQE)"),
        verbose_name=_("Registro de Qualificação de Especialidade (RQE)"),
    )
    board_certification_selfie = models.ImageField(
        **NULLABLE,
        upload_to=HashedFileName("board_certification_selfie"),
        verbose_name=_("Selfie do documento de registro do conselho"),
    )
    photo = models.ImageField(
        **NULLABLE,
        upload_to=HashedFileName("professional_photos"),
        verbose_name=_("Foto de perfil"),
    )
    photo_description = models.CharField(
        **NULLABLE,
        max_length=250,
        help_text=_("Descrição da foto de perfil para pessoas com deficiência visual"),
        verbose_name=_("Descrição da foto de perfil"),
    )
    google_calendar_credentials_json = models.JSONField(
        null=True,
        blank=True,
        help_text="Credenciais OAuth 2.0 para a API do Google Calendar.",
    )
    chave_pix = models.CharField(max_length=100, default=None, **NULLABLE)
    tipo_chave_pix = models.CharField(
        max_length=10,
        choices=tipo_chave,
        default=None,
        null=True,
        blank=True,
        verbose_name=_("tipo de chave pix"),
    )
    income_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        **NULLABLE,
        verbose_name=_("Renda/Faturamento Mensal"),
        help_text=_(
            "Renda mensal para PF ou faturamento mensal para PJ (obrigatório para criação)"
        ),
    )

    class Meta:
        verbose_name = _("Profissional")
        verbose_name_plural = _("Profissionais")
        app_label = "professional"
        db_table = "lacreisaude_professional"

    def __str__(self):
        return self.full_name

    @property
    def current_step(self):
        current_step = VerificationStepsService(self).current_step()
        if not current_step:
            return None
        return current_step["description"], current_step["internal_message"]


class Clinic(BaseModel):
    id = HashedAutoField(primary_key=True)
    professional = models.OneToOneField(
        Professional,
        on_delete=models.PROTECT,
        related_name="clinic",
        verbose_name=_("Profissional"),
    )
    is_presential_clinic = models.BooleanField(
        default=True, verbose_name=_("Clínica Presencial")
    )
    is_online_clinic = models.BooleanField(
        default=False, verbose_name=_("Clínica Online")
    )
    name = models.CharField(
        max_length=100, **NULLABLE, verbose_name=_("Nome da Clínica")
    )
    zip_code = models.CharField(max_length=20, **NULLABLE, verbose_name=_("CEP"))
    registered_neighborhood = models.ForeignKey(
        "address.Neighborhood",
        on_delete=models.PROTECT,
        help_text=_("ID do bairro encontrado na API de busca de CEP"),
        **NULLABLE,
        verbose_name=_("ID do bairro"),
    )
    neighborhood = models.CharField(
        max_length=200,
        help_text=_("Nome do bairro"),
        **NULLABLE,
        verbose_name=_("Bairro"),
    )
    city = models.CharField(
        max_length=200,
        help_text=_("Nome da cidade"),
        **NULLABLE,
        verbose_name=_("Cidade"),
    )
    state = models.ForeignKey(
        "address.State", on_delete=models.PROTECT, verbose_name=_("Estado"), **NULLABLE
    )
    address = models.CharField(
        max_length=200,
        help_text=_("Endereço completo, incluindo número"),
        **NULLABLE,
        verbose_name=_("Endereço"),
    )
    address_line2 = models.CharField(
        max_length=200,
        help_text=_("Complemento do endereço"),
        **NULLABLE,
        verbose_name=_("Complemento"),
    )
    phone = PhoneNumberField(
        help_text=_("Telefone da clínica"),
        **NULLABLE,
        verbose_name=_("Telefone da clínica"),
    )
    phone_whatsapp = PhoneNumberField(
        help_text=_("Telefone WhatsApp"), **NULLABLE, verbose_name=_("Whatsapp")
    )
    consult_price = models.DecimalField(
        decimal_places=2,
        max_digits=9,
        validators=[MinValueValidator(Decimal(0.00))],
        help_text=_("Valor da Consulta"),
        **NULLABLE,
        verbose_name=_("Valor da Consulta"),
    )
    duration_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text=_("Duração em minutos da consulta"),
        **NULLABLE,
        verbose_name=_("Duração da consulta"),
    )
    accepts_insurance_providers = models.BooleanField(
        default=False,
        help_text=_("Aceita Convênios?"),
        verbose_name=_("Aceita Convênios"),
    )
    provides_accessibility_standards = models.BooleanField(
        default=False,
        help_text=_("Clínica possui acessibilidade?"),
        verbose_name=_("Clínica possui acessibilidade"),
    )
    online_clinic_phone = PhoneNumberField(
        help_text=_("Telefone da clínica"),
        **NULLABLE,
        verbose_name=_("Telefone da clínica"),
    )
    online_clinic_phone_whatsapp = PhoneNumberField(
        help_text=_("Telefone WhatsApp"), **NULLABLE, verbose_name="WhatsApp"
    )
    online_clinic_consult_price = models.DecimalField(
        decimal_places=2,
        max_digits=9,
        validators=[MinValueValidator(Decimal(0.00))],
        help_text=_("Valor da Consulta"),
        **NULLABLE,
        verbose_name=_("Valor da Consulta online"),
    )
    online_clinic_duration_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text=_("Duração em minutos da consulta"),
        **NULLABLE,
        verbose_name=_("Duração da consulta"),
    )
    online_clinic_accepts_insurance_providers = models.BooleanField(
        default=False,
        help_text=_("Aceita Convênios?"),
        verbose_name=_("Aceita Convênios"),
    )

    def __str__(self):
        return self.name or f"{self._meta.verbose_name} (id: {self.id})"

    class Meta:
        verbose_name = _("Clínica")
        verbose_name_plural = _("Clínicas")
        app_label = "professional"
        db_table = "lacreisaude_clinic"

    def post_create_instance(self, *args, **kwargs):
        # Esta lógica reativa (hook) permanece no modelo
        watson.default_search_engine.update_obj_index(self.professional)

    def post_update_instance(self, *args, **kwargs):
        # Esta lógica reativa (hook) permanece no modelo
        watson.default_search_engine.update_obj_index(self.professional)

    @property
    def full_address(self):
        # Esta lógica de APRESENTAÇÃO permanece no modelo
        parts = [
            self.address or "",
            self.address_line2 or "",
            self.neighborhood or "",
            self.city or "",
            self.state.code if self.state else "",
        ]
        return ", ".join(filter(None, parts)) or "Endereço não cadastrado"


class ClinicOpeningSchedule(BaseModel):
    ONLINE = "online"
    PRESENTIAL = "presential"
    SCHEDULE_TYPES = [
        (ONLINE, _("Online")),
        (PRESENTIAL, _("Presential")),
    ]
    SUN = "sun"
    MON = "mon"
    TUE = "tue"
    WED = "wed"
    THU = "thu"
    FRI = "fri"
    SAT = "sat"
    WEEKDAYS = [
        (SUN, _("Domingo")),
        (MON, _("Segunda-feira")),
        (TUE, _("Terça-feira")),
        (WED, _("Quarta-feira")),
        (THU, _("Quinta-feira")),
        (FRI, _("Sexta-feira")),
        (SAT, _("Sábado")),
    ]
    WEEKDAYS_MAP = {k: v for k, v in WEEKDAYS}
    id = HashedAutoField(primary_key=True)
    schedule_type = models.CharField(
        max_length=15,
        choices=SCHEDULE_TYPES,
        default="presential",
        verbose_name=_("Tipo de agendamento"),
    )
    weekday = models.CharField(
        max_length=3, choices=WEEKDAYS, verbose_name="Dia da semana"
    )
    clinic = models.ForeignKey(
        Clinic, on_delete=models.CASCADE, related_name="opening_schedules"
    )
    opening_time = models.TimeField(verbose_name="Horário de Abertura")
    closing_time = models.TimeField(verbose_name="Horário de fechamento")

    class Meta:
        verbose_name = _("Horário de abertura da clínica")
        verbose_name_plural = _("Horários de abertura da clínica")
        app_label = "professional"
        db_table = "lacreisaude_clinic_opening_schedule"


class ProfessionalReview(BaseModel):
    id = HashedAutoField(primary_key=True)
    reviewed_by = models.ForeignKey(
        "client.User", on_delete=models.PROTECT, verbose_name=_("Revisado por")
    )
    professional = models.ForeignKey(
        Professional,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Profissional"),
    )
    professional_name = models.CharField(
        max_length=250, verbose_name=_("Nome do profissional")
    )
    profession = models.ForeignKey(
        Profession,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_("Profissão"),
    )
    internal_note = models.TextField(verbose_name=_("Nota interna"))
    status = models.CharField(
        max_length=20,
        choices=[
            ("approved", "Aprovado"),
            ("rejected", "Rejeitado"),
        ],
    )
    rejected_professional_data = models.JSONField(
        null=True,
        blank=True,
    )
    step = models.CharField(
        max_length=30,
        choices=VERIFICATION_STEPS_CHOICES,
        null=True,
        verbose_name=_("Etapas"),
    )

    def __str__(self):
        return self.professional_name

    class Meta:
        verbose_name = _("Revisão de profissional")
        verbose_name_plural = _("Revisão de profissionais")
        app_label = "professional"


class ContactRequest(BaseModel):
    id = HashedAutoField(primary_key=True)
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        help_text=_("Pessoa usuária solicitando o contato da profissional"),
        on_delete=models.deletion.PROTECT,
        verbose_name=_("Solicitante"),
    )
    requester_ip_address = models.GenericIPAddressField(verbose_name=_("Endereço IP"))
    requester_phone_number = PhoneNumberField(verbose_name=_("Telefone solicitante"))
    requester_user_agent = models.TextField(verbose_name=_("User Agent"))
    professional = models.ForeignKey(
        Professional, on_delete=models.deletion.PROTECT, verbose_name=_("Profissional")
    )
    validation_code = models.CharField(
        max_length=6, verbose_name=_("Código de validação")
    )
    code_confirmed = models.BooleanField(
        default=False, verbose_name=_("Código confirmado")
    )
    expires_at = models.DateTimeField(verbose_name=_("Expira em"))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_("Criado em"))

    class Meta:
        verbose_name = _("Solicitação de Contato")
        verbose_name_plural = _("Solicitações de Contato")
        app_label = "professional"

    EXPIRES_IN_DAYS = 7

    def __str__(self) -> str:
        return f"{self.requester} -> {self.professional}"

    @property
    def sms_message(self):
        return CONTACT_REQUEST_SMS_MESSAGE.format(validation_code=self.validation_code)


class Complaint(BaseModel):
    id = HashedAutoField(primary_key=True)
    complaint_types = models.CharField(
        max_length=200, null=True, blank=True, verbose_name=_("Tipos de comportamento")
    )
    other_complaint_type = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Outros tipos de comportamento",
    )
    incident_date = models.DateField(verbose_name=_("Data do ocorrido"))
    incident_time = models.TimeField(verbose_name=_("Horário do ocorrido"))
    reported_by = models.ForeignKey(
        "client.User", on_delete=models.PROTECT, verbose_name=_("Reportado por")
    )
    description = models.TextField(verbose_name=_("Descrição do ocorrido"))
    professional = models.ForeignKey(
        Professional, on_delete=models.deletion.PROTECT, verbose_name=_("Profissional")
    )

    class Meta:
        verbose_name = _("Denúncia")
        verbose_name_plural = _("Denúncias")
        app_label = "professional"
        db_table = "lacreisaude_complaint"


class ProfessionalSubaccount(BaseModel):
    id = HashedAutoField(primary_key=True)
    professional = models.OneToOneField(
        "professional.Professional",
        on_delete=models.CASCADE,
        related_name="subaccount",
        verbose_name=_("Profissional"),
    )
    asaas_id = models.CharField(
        max_length=100, unique=True, verbose_name=_("ID no Asaas")
    )
    onboarding_url = models.URLField(
        max_length=500, **NULLABLE, verbose_name=_("URL de Onboarding de Documentos")
    )
    status_general = models.CharField(
        max_length=50, default="AWAITING_APPROVAL", verbose_name=_("Status Geral")
    )
    status_commercial_info = models.CharField(
        max_length=50,
        default="AWAITING_APPROVAL",
        verbose_name=_("Status Info. Comerciais"),
    )
    status_bank_account = models.CharField(
        max_length=50,
        default="AWAITING_APPROVAL",
        verbose_name=_("Status Conta Bancária"),
    )
    status_documentation = models.CharField(
        max_length=50,
        default="AWAITING_APPROVAL",
        verbose_name=_("Status Documentação"),
    )

    class Meta:
        verbose_name = _("Subconta de Profissional (Asaas)")
        verbose_name_plural = _("Subcontas de Profissionais (Asaas)")
        app_label = "professional"
        db_table = "lacreisaude_professional_subaccount"

    def __str__(self):
        return f"Subconta de {self.professional.full_name} ({self.asaas_id})"


class SubaccountDocument(BaseModel):
    id = HashedAutoField(primary_key=True)
    subaccount = models.ForeignKey(
        ProfessionalSubaccount,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name=_("Subconta"),
    )
    document_type = models.CharField(
        max_length=100,
        verbose_name=_("Tipo de Documento"),
        help_text=_("Ex: IDENTIFICATION, SOCIAL_CONTRACT"),
    )
    file = models.FileField(
        upload_to=HashedFileName("subaccount_documents"),
        verbose_name=_("Arquivo do Documento"),
    )
    asaas_id = models.CharField(
        max_length=100, unique=True, verbose_name=_("ID do Documento no Asaas")
    )
    status = models.CharField(
        max_length=50, default="pending", verbose_name=_("Status do Documento")
    )
    rejection_reason = models.TextField(
        **NULLABLE, verbose_name=_("Motivo da Rejeição")
    )

    class Meta:
        verbose_name = _("Documento de Subconta")
        verbose_name_plural = _("Documentos de Subcontas")
        app_label = "professional"
        db_table = "lacreisaude_subaccount_document"

    def __str__(self):
        return f"Documento {self.document_type} de {self.subaccount.professional.full_name}"


class LegacyProfessionalData(BaseModel):
    """
    Modelo para armazenar dados de diversidade LEGADOS do Professional,
    espelhando a estrutura (Foreign Keys names + CharField 'Other') do sistema antigo.
    """

    professional = models.OneToOneField(
        "Professional",
        on_delete=models.CASCADE,
        related_name="legacy_social_data",
        verbose_name=_("Profissional Original"),
    )

    ethnic_group_name = models.CharField(
        max_length=100,
        **NULLABLE,
        verbose_name=_("Grupo Étnico (Nome Legado)"),
    )

    gender_identity_name = models.CharField(
        max_length=100,
        **NULLABLE,
        verbose_name=_("Identidade de Gênero (Nome Legado)"),
    )

    sexual_orientation_name = models.CharField(
        max_length=100,
        **NULLABLE,
        verbose_name=_("Orientação Sexual (Nome Legado)"),
    )

    pronoun_text = models.CharField(
        max_length=50, **NULLABLE, verbose_name=_("Pronome (Texto Legado)")
    )

    article_text = models.CharField(
        max_length=1, **NULLABLE, verbose_name=_("Artigo (Texto Legado)")
    )

    disability_types_names = models.TextField(
        **NULLABLE, verbose_name=_("Tipos de Deficiência (Nomes, LEGADO)")
    )

    other_ethnic_group = models.CharField(
        max_length=100, **NULLABLE, verbose_name=_("Outro Grupo Étnico (LEGADO)")
    )
    other_gender_identity = models.CharField(
        max_length=100,
        **NULLABLE,
        verbose_name=_("Outra Identidade de Gênero (LEGADO)"),
    )
    other_sexual_orientation = models.CharField(
        max_length=100, **NULLABLE, verbose_name=_("Outra Orientação Sexual (LEGADO)")
    )
    other_pronoun = models.CharField(
        max_length=100, **NULLABLE, verbose_name=_("Outro Pronome (LEGADO)")
    )
    other_disability_types = models.CharField(
        max_length=100,
        **NULLABLE,
        verbose_name=_("Outro Tipos de deficiência (LEGADO)"),
    )
    other_article = models.CharField(
        max_length=1, **NULLABLE, verbose_name=_("Outro Artigo (LEGADO)")
    )

    class Meta:
        verbose_name = _("Dados Sociais Legados do Profissional")
        verbose_name_plural = _("Dados Sociais Legados dos Profissionais")
        app_label = "professional"
        db_table = "lacreisaude_legacy_professional_data"
