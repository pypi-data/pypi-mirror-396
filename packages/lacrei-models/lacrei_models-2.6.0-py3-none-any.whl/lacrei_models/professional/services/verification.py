import logging

from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from lacrei_models.utils.social_choices import (
    AnswerType,
    EthnicGroupChoices,
    GenderIdentityChoices,
    PronounChoices,
    SexualityChoices,
)

PROFESSIONAL_VALIDATION_PENDING_ADMIN = _("Pendente Lacrei")
PROFESSIONAL_VALIDATION_PENDING_DATA_INPUT = _("Pendente Profissional")
PROFESSIONAL_ALREADY_APPROVED_FOR_STEP = _("Aprovado")

logger = logging.getLogger(__name__)


class VerificationStep:
    name: str
    url_path_to_submit: str
    url_path_to_wait_completion: str
    description: str

    def __init__(self, professional):
        self.professional = professional

    @cached_property
    def is_completed(self):  # pragma: no cover
        raise NotImplementedError

    @cached_property
    def is_submitted(self):  # pragma: no cover
        raise NotImplementedError

    @cached_property
    def redirect_to(self):
        if self.is_completed:
            return None

        if self.is_submitted:
            return self.url_path_to_wait_completion

        return self.url_path_to_submit

    def to_representation(self):
        return {
            "is_completed": self.is_completed,
            "is_submitted": self.is_submitted,
            "redirect_to": self.redirect_to,
            "description": self.description,
            "internal_message": (
                PROFESSIONAL_ALREADY_APPROVED_FOR_STEP
                if self.is_completed
                else (
                    PROFESSIONAL_VALIDATION_PENDING_DATA_INPUT
                    if not self.is_submitted
                    else PROFESSIONAL_VALIDATION_PENDING_ADMIN
                )
            ),
        }


class BoardRegistrationNumber(VerificationStep):
    """
    Uma pessoa interna da lacrei irá validar o número do conselho no respectivo portal."

    Após validação, será enviado um email de confirmação, onde:
    - Se rejeitado: apagamos o cadastro e pedimos para refazer, com um número certo.
    - Se aprovado: segue para o pós cadastro.
    """

    name = "board_registration_number"
    url_path_to_submit = "/"
    url_path_to_wait_completion = "/saude/verificacao-inscricao/"
    description = "1ª - Validação no conselho"

    @cached_property
    def is_completed(self):
        return self.professional.profile_status == "approved"

    @cached_property
    def is_submitted(self):
        return True


class EmailConfirmation(VerificationStep):
    """
    Nessa etapa, uma pessoa interna da Lacrei já aprovou o cadastro,
    e agora aguardamos a pessoa profissional confirmar o email.
    """

    name = "email_confirmation"
    url_path_to_submit = "/"
    url_path_to_wait_completion = "/saude/verificacao-inscricao/"
    description = "2ª - Confirmação do email"

    @cached_property
    def is_completed(self):
        return self.professional.user.email_verified

    @cached_property
    def is_submitted(self):
        # Se a etapa anterior (BoardRegistrationNumber) foi aprovada,
        # então esta etapa está automaticamente "submitted"
        return BoardRegistrationNumber(self.professional).is_completed


class PostRegistrationData(VerificationStep):
    """
    Nessa passo a pessoa profissional irá enviar os dados restantes para o cadastro.

    Após validação, será enviado um email de confirmação, onde:
    - Se rejeitado: mandamos email pedindo para reenviar os dados.
    - Se aprovado: Liberado para ficar ativo na plataforma
    """

    name = "post_registration_data"
    url_path_to_submit = "/saude/cadastro-dados-pessoais/"
    url_path_to_wait_completion = "/saude/painel-cadastro-analise/"
    description = "4ª - Pós cadastro"

    @cached_property
    def is_completed(self):
        return self.professional.active

    @cached_property
    def is_submitted(self):
        return hasattr(self.professional, "clinic") and bool(
            self.professional.board_certification_selfie
        )


class IntersectionalityData(VerificationStep):
    """
    Na etapa, pedimos que adicione os dados de interseccionalidade.
    """

    name = "add_intersectionality_data"
    url_path_to_submit = "/saude/cadastro-diversidade/"
    url_path_to_wait_completion = ""
    description = "3ª - Diversidade"

    # Função auxiliar para verificar se 'Outro' foi preenchido
    def _has_other_answer(self, field_value, answer_type_enum):
        """Verifica se o campo tem o código 'OU' E se existe um registro em OtherProfileAnswer."""
        if field_value == EthnicGroupChoices.OUTRO.value:  # Usa .value para CharField
            try:
                # Usa o related_manager 'other_answers' para buscar a resposta
                return self.professional.other_answers.filter(
                    answer_type=answer_type_enum.value
                ).exists()
            except Exception:
                return False
        return False

    @cached_property
    def is_completed(self):
        professional = self.professional

        ethnic_check = bool(professional.ethnic_group) and (
            professional.ethnic_group != EthnicGroupChoices.OUTRO.value
            or self._has_other_answer(
                professional.ethnic_group, AnswerType.ETHNIC_GROUP
            )
        )

        gender_check = bool(professional.gender_identity) and (
            professional.gender_identity != GenderIdentityChoices.OUTRO.value
            or self._has_other_answer(
                professional.gender_identity, AnswerType.GENDER_IDENTITY
            )
        )

        sexuality_check = bool(professional.sexuality) and (
            professional.sexuality != SexualityChoices.OUTRO.value
            or self._has_other_answer(professional.sexuality, AnswerType.SEXUALITY)
        )

        pronoun_check = bool(professional.pronoun) and (
            professional.pronoun != PronounChoices.OUTRO.value
            or self._has_other_answer(professional.pronoun, AnswerType.PRONOUN)
        )

        disability_check = bool(professional.disability_types)

        return all(
            [
                ethnic_check,
                gender_check,
                sexuality_check,
                pronoun_check,
                disability_check,
            ]
        )

    @cached_property
    def is_submitted(self):
        return self.is_completed


class VerificationStepsService:
    def __init__(self, professional):
        self.professional = professional
        self.steps = [
            BoardRegistrationNumber(professional),
            EmailConfirmation(professional),
            IntersectionalityData(professional),
            PostRegistrationData(professional),
        ]

    def to_representation(self) -> dict:
        current_step = None
        steps_repr = {}

        for step in self.steps:
            if not step.is_completed and not current_step:
                current_step = step.name

            steps_repr[step.name] = step.to_representation()

        return {"current_step": current_step, "steps": steps_repr}

    def current_step(self):
        representation = self.to_representation()
        if not representation["current_step"]:
            return None
        return representation["steps"][representation["current_step"]]
