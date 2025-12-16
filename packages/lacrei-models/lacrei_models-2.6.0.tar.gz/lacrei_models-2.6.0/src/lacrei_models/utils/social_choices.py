from django.db import models
from django.utils.translation import gettext_lazy as _


class EthnicGroupChoices(models.TextChoices):
    """
    Representa as opções fixas para o Grupo Étnico.
    """

    AMARELA = "AM", _("Amarela")
    BRANCA = "BR", _("Branca")
    INDIGENA = "IN", _("Indígena")
    PARDA = "PA", _("Parda")
    PRETA = "PR", _("Preta")
    OUTRO = "OU", _("Outro (Especificar)")


class GenderIdentityChoices(models.TextChoices):
    """
    Representa as opções fixas para a Identidade de Gênero.
    """

    AGENERA = "AG", _("Agênera")
    FLUIDA = "FL", _("Fluida")
    HOMEM_CIS = "HC", _("Homem Cisgênero")
    HOMEM_TRANS = "HT", _("Homem Transgênero")
    INTERSSEXO = "IT", _("Interssexo")
    MULHER_CIS = "MC", _("Mulher Cisgênero")
    MULHER_TRANS = "MT", _("Mulher Transgênero")
    NAO_BINARIA = "NB", _("Não-binária")
    TRAVESTI = "TV", _("Travesti")
    OUTRO = "OU", _("Outra (Especificar)")


class SexualityChoices(models.TextChoices):
    """
    Representa as opções fixas para a Sexualidade.
    """

    ASSEXUAL = "AS", _("Assexual")
    BISSEXUAL = "BI", _("Bissexual")
    DEMISSEXUAL = "DE", _("Demissexual")
    GAY = "GA", _("Gay")
    HETEROSSEXUAL = "HT", _("Heterossexual")
    PANSEXUAL = "PA", _("Pansexual")
    LESBICA = "LE", _("Lésbica")
    OUTRO = "OU", _("Outra (Especificar)")


class PronounChoices(models.TextChoices):
    """
    Representa as opções fixas para Pronome, incluindo o Artigo para
    a lógica do 'display_article'.
    """

    ELE_DELE = "EL", _("Ele/Dele")
    ELA_DELA = "EA", _("Ela/Dela")
    ELU_DELU = "EU", _("Elu/Delu")
    OUTRO = "OU", _("Outro")

    def get_article(self):
        """Retorna o terceiro elemento da tupla de escolha (o artigo)."""
        try:
            return self._value_[2]
        except IndexError:
            return None


class DisabilityTypeChoices(models.TextChoices):
    """
    Representa as opções fixas para Tipos de Deficiência (seleção múltipla).
    """

    NAO_POSSUI = "NP", _("Não possuo deficiência")
    AUDITIVA = "AU", _("Auditiva")
    COGNITIVA = "CO", _("Cognitiva")
    MOTORA = "MO", _("Motora")
    MULTIPLA = "MU", _("Múltipla")
    VISUAL = "VI", _("Visual")
    OUTRA = "OU", _("Outra")


class AnswerType(models.TextChoices):
    """
    Representa as opções fixas para os campos onde são permitidos outros.
    """

    ETHNIC_GROUP = "EG", _("Grupo Étnico")
    GENDER_IDENTITY = "GI", _("Identidade de Gênero")
    SEXUALITY = "SE", _("Sexualidade")
    PRONOUN = "PR", _("Pronome")
    DISABILITY = "DS", _("Deficiência")
