from django.db import models
from django.utils.translation import gettext_lazy as _

from lacrei_models.utils.models import NULLABLE, BaseModel


class Country(BaseModel):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=2)
    active = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("País")
        verbose_name_plural = _("Países")
        app_label = "address"

    def __str__(self):
        return self.name


class State(BaseModel):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=2)
    ibge_code = models.IntegerField(**NULLABLE)
    active = models.BooleanField(default=False)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)

    class Meta:
        verbose_name = _("Estado")
        verbose_name_plural = _("Estados")
        app_label = "address"

    def __str__(self):
        return self.name


class City(BaseModel):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.PROTECT)
    ibge_code = models.IntegerField(**NULLABLE)
    active = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Cidade")
        verbose_name_plural = _("Cidades")
        app_label = "address"

    def __str__(self):
        return self.name


class Neighborhood(BaseModel):
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.PROTECT)

    class Meta:
        verbose_name = _("Bairro")
        verbose_name_plural = _("Bairros")
        app_label = "address"

    def __str__(self):
        return self.name


class ZipCode(BaseModel):
    code = models.CharField(max_length=100)
    address_line_1 = models.CharField(
        max_length=200, help_text=_("Logradouro"), **NULLABLE
    )
    address_line_2 = models.CharField(
        max_length=200, help_text=_("Complemento"), **NULLABLE
    )
    ibge_code = models.CharField(
        max_length=50, help_text=_("Código do IBGE"), **NULLABLE
    )
    neighborhood_name = models.CharField(
        max_length=200, help_text=_("Nome do bairro"), **NULLABLE
    )
    city = models.ForeignKey(City, on_delete=models.PROTECT, null=True, blank=False)
    neighborhood = models.ForeignKey(
        Neighborhood,
        on_delete=models.PROTECT,
        related_name="zip_codes",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("CEP")
        verbose_name_plural = _("CEPs")
        app_label = "address"

    def __str__(self):
        return self.code
