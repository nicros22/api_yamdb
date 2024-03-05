from django.db import models
from .constants import MAX_LENGTH_MODEL


class BaseModel(models.Model):

    name = models.CharField(max_length=MAX_LENGTH_MODEL)
    slug = models.SlugField(unique=True)

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.slug
