from allauth.account.models import EmailAddress
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext as _
from phonenumber_field.modelfields import PhoneNumberField

from lacrei_models.client.managers import UserManager
from lacrei_models.utils.models import (
    NULLABLE,
    BaseModel,
    HashedAutoField,
    HashedFileName,
)
from lacrei_models.utils.social_choices import (
    AnswerType,
    DisabilityTypeChoices,
    EthnicGroupChoices,
    GenderIdentityChoices,
    PronounChoices,
    SexualityChoices,
)
from lacrei_models.utils.validators import OnlyAlphabeticValidator


class User(AbstractUser, BaseModel):
    USER = "user"
    PROFESSIONAL = "professional"
    LOGGED_AS_CHOICES = [(USER, _("Usuário")), (PROFESSIONAL, _("Profissional"))]
    id = HashedAutoField(primary_key=True)
    logged_as = models.CharField(
        max_length=12,
        choices=LOGGED_AS_CHOICES,
        null=True,
        blank=True,
        help_text=_("Indica se o usuário está logado como Usuário ou Profissional"),
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(
        max_length=150, blank=False, validators=[OnlyAlphabeticValidator()]
    )
    last_name = models.CharField(
        max_length=150, blank=False, validators=[OnlyAlphabeticValidator()]
    )
    birth_date = models.DateField(**NULLABLE)
    is_18_years_old_or_more = models.BooleanField(**NULLABLE)
    last_login = models.DateTimeField(auto_now_add=True)
    email_verified = models.BooleanField(default=False)

    accepted_privacy_document = models.BooleanField(default=False)
    privacy_document = models.ForeignKey(
        "client.PrivacyDocument", on_delete=models.PROTECT, null=True, blank=False
    )
    newsletter_subscribed = models.BooleanField(default=True)

    phone = PhoneNumberField(null=True, blank=True)
    phone_verified = models.BooleanField(default=False)
    phone_verification_token = models.CharField(max_length=6, **NULLABLE)
    phone_verification_token_expires_at = models.DateTimeField(**NULLABLE)

    objects = UserManager()
    username = None
    date_joined = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("Pessoa Usuária")
        verbose_name_plural = _("Pessoas Usuárias")
        app_label = "client"
        db_table = "lacreiid_user"

    def post_create_instance(self, *args, **kwargs):
        self.profile = Profile.objects.create(user=self)


class PrivacyDocument(BaseModel):
    privacy_policy = models.URLField()
    terms_of_use = models.URLField()
    profile_type = models.CharField(
        max_length=20,
        choices=[("client", _("Lacrei ID")), ("professional", _("Lacrei Saúde"))],
    )

    class Meta:
        verbose_name = _("Termo de uso e privacidade")
        verbose_name_plural = _("Termos de uso e privacidade")
        app_label = "client"
        db_table = "lacreiid_privacydocument"

    def __str__(self):
        return f"{self.id} - {self.profile_type} - {self.created_at}"


class BaseProfile(BaseModel):
    ethnic_group = models.CharField(
        max_length=2,
        choices=EthnicGroupChoices.choices,
        **NULLABLE,
        verbose_name=_("Grupo Étnico"),
    )
    gender_identity = models.CharField(
        max_length=2,
        choices=GenderIdentityChoices.choices,
        **NULLABLE,
        verbose_name=_("Identidade de Gênero"),
    )
    sexuality = models.CharField(
        max_length=2,
        choices=SexualityChoices.choices,
        **NULLABLE,
        verbose_name=_("Sexualidade"),
    )
    pronoun = models.CharField(
        max_length=2,
        choices=PronounChoices.choices,
        **NULLABLE,
        verbose_name=_("Pronome"),
    )
    disability_types = ArrayField(
        models.CharField(
            max_length=2,
            choices=DisabilityTypeChoices.choices,
        ),
        **NULLABLE,
        verbose_name=_("Tipos de deficiência"),
    )

    def _get_other_value(self, answer_type_code):
        """Função auxiliar para buscar o objeto 'Outro' no banco de dados,
        navegando via User para a instância Profile (Client).
        """
        try:

            return self.user.profile.other_answers.get(answer_type=answer_type_code)

        except Exception:
            return None

    @property
    def display_ethnic_group(self):
        if self.ethnic_group == EthnicGroupChoices.OUTRO:
            other_answer = self._get_other_value(AnswerType.ETHNIC_GROUP)
            return other_answer.custom_value if other_answer else None
        return self.ethnic_group or None

    @property
    def display_gender_identity(self):
        if self.gender_identity == GenderIdentityChoices.OUTRO:
            other_answer = self._get_other_value(AnswerType.GENDER_IDENTITY.value)
            return other_answer.custom_value if other_answer else None
        return self.gender_identity or None

    @property
    def display_sexuality(self):
        if self.sexuality == SexualityChoices.OUTRO:
            other_answer = self._get_other_value(AnswerType.SEXUALITY.value)
            return other_answer.custom_value if other_answer else _("Outro")

        return self.sexuality or None

    @property
    def display_pronoun(self):
        if self.pronoun == PronounChoices.OUTRO:
            other_answer = self._get_other_value(AnswerType.PRONOUN.value)

            return other_answer.custom_value if other_answer else None
        return self.pronoun or None

    @property
    def display_article(self):
        if self.pronoun == PronounChoices.OUTRO:
            other_answer = self._get_other_value(
                OtherProfileAnswer.AnswerType.PRONOUN.value
            )

            if other_answer and other_answer.custom_value:
                return other_answer.custom_value[-1].lower()
            return None

        try:
            PRONOUN_ARTICLE_MAP = {
                PronounChoices.ELE_DELE.value: "o",
                PronounChoices.ELA_DELA.value: "a",
                PronounChoices.ELU_DELU.value: "e",
            }
            return PRONOUN_ARTICLE_MAP.get(self.pronoun)

        except Exception:
            return None

    @property
    def display_disability_types(self):
        codigos_selecionados = self.disability_types or []

        labels = []
        other_answer = None

        if DisabilityTypeChoices.OUTRA.value in codigos_selecionados:
            other_answer = self._get_other_value(AnswerType.DISABILITY)

        CODIGOS_FIXOS = [
            DisabilityTypeChoices.NAO_POSSUI.value,
            DisabilityTypeChoices.AUDITIVA.value,
            DisabilityTypeChoices.COGNITIVA.value,
            DisabilityTypeChoices.MOTORA.value,
            DisabilityTypeChoices.MULTIPLA.value,
            DisabilityTypeChoices.VISUAL.value,
        ]

        for codigo in codigos_selecionados:
            try:
                if codigo in CODIGOS_FIXOS:
                    labels.append(codigo)

                elif codigo == DisabilityTypeChoices.OUTRA.value:
                    if other_answer and other_answer.custom_value:
                        labels.append(other_answer.custom_value)
                    else:
                        label = str(DisabilityTypeChoices(codigo).label)
                        labels.append(label)

                else:
                    label = str(DisabilityTypeChoices(codigo).label)
                    labels.append(label)

            except ValueError:
                continue

        return labels if labels else None

    class Meta:
        abstract = True


class OtherProfileAnswer(models.Model):
    user = models.ForeignKey(
        "client.User",
        on_delete=models.CASCADE,
        related_name="user_other_answers",
        verbose_name=_("pessoa usuária"),
    )
    profile = models.ForeignKey(
        "client.Profile",
        on_delete=models.CASCADE,
        related_name="other_answers",
        verbose_name=_("Perfil Relacionado"),
    )
    answer_type = models.CharField(
        max_length=2, choices=AnswerType.choices, verbose_name=_("Tipo de Resposta")
    )
    custom_value = models.CharField(max_length=100, verbose_name=_("Valor Customizado"))

    class Meta:
        verbose_name = _("Resposta 'Outra' do épico de pós cadastro")
        verbose_name_plural = _("Respostas 'Outras' do épico de pós cadastro")
        # Garante que só haja uma resposta 'Outra' por tipo por perfil
        unique_together = ("profile", "answer_type")
        app_label = "client"
        db_table = "lacreiid_other_profile_answer"


class Profile(BaseProfile):
    id = HashedAutoField(primary_key=True)
    user = models.OneToOneField(
        User, on_delete=models.PROTECT, verbose_name=_("Lacrei ID")
    )
    completed = models.BooleanField(
        default=False,
        verbose_name=_("Perfil completo"),
    )
    photo = models.ImageField(
        null=True,
        upload_to=HashedFileName("profile_photos"),
        verbose_name=_("Foto de perfil"),
    )
    photo_description = models.TextField(
        null=True, blank=True, help_text=_("Descrição da foto")
    )

    def __str__(self):
        try:
            return self.user.first_name
        except User.DoesNotExist:
            return "Perfil sem usuário"

    class Meta:
        verbose_name = _("Perfil")
        verbose_name_plural = _("Perfis")
        app_label = "client"
        db_table = "lacreiid_profile"


class CustomEmailAddress(EmailAddress):
    class Meta:
        proxy = True
        app_label = "client"
        db_table = "lacreiid_custom_email_address"


class LegacyProfileData(BaseModel):
    """
    Modelo de backup para armazenar dados de diversidade do Profile em formato de TEXTO
    (name/pronoun) antes da refatoração para Enums.
    """

    profile = models.OneToOneField(
        "Profile",
        on_delete=models.CASCADE,
        related_name="legacy_data",
        verbose_name=_("Perfil Original"),
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
        verbose_name = _("Dados Legados do Perfil")
        verbose_name_plural = _("Dados Legados do Perfil")
        app_label = "client"
        db_table = "lacreiid_legacy_profile_data"
