import os
from typing import TypedDict
from uuid import uuid4

from django.db import models
from django.utils.deconstruct import deconstructible


class ModelsHooksMixin:
    def save(self, *args, **kwargs):
        is_being_created = self._state.adding
        if is_being_created:
            self.pre_create_instance(*args, **kwargs)
            super().save(*args, **kwargs)
            self.post_create_instance(*args, **kwargs)
        else:
            self.pre_update_instance(*args, **kwargs)
            super().save(*args, **kwargs)
            self.post_update_instance(*args, **kwargs)

    def post_create_instance(self, *args, **kwargs):
        pass

    def post_update_instance(self, *args, **kwargs):
        pass

    def pre_create_instance(self, *args, **kwargs):
        pass

    def pre_update_instance(self, *args, **kwargs):
        pass


class BaseModel(ModelsHooksMixin, models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        abstract = True


@deconstructible
class GetHasher:
    def __init__(self, size=8):
        self.size = size

    def __call__(self):
        return self._get_hash_pk()

    def _get_hash_pk(self):
        return uuid4().hex[: self.size]


class HashedAutoField(models.CharField):
    def __init__(self, *args, **kwargs):
        size = kwargs.pop("size", 8)
        defaults = {"default": GetHasher(size), "max_length": 32, "editable": False}
        defaults.update(kwargs)
        super().__init__(*args, **defaults)


@deconstructible
class HashedFileName(object):
    def __init__(self, path):
        self.path = os.path.join(path, "%s%s")

    def __call__(self, instance, filename):
        extension = os.path.splitext(filename)[1]
        return self.path % (uuid4(), extension)


class NullableOptions(TypedDict):
    null: bool
    blank: bool


NULLABLE: NullableOptions = {"null": True, "blank": True}
