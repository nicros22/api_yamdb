from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator
from django.utils import timezone

from .constants import MAX_LENGTH_MODEL

ROLE_CHOICES = (
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Админ'),
)


class Category(models.Model):
    """Базовая модель категорий"""
    name = models.CharField(max_length=MAX_LENGTH_MODEL)
    slug = models.SlugField(max_length=MAX_LENGTH_MODEL, unique=True)

    def __str__(self):
        return self.slug


class Genre(models.Model):
    "Базовая модель жанров"
    name = models.CharField(max_length=MAX_LENGTH_MODEL)
    slug = models.SlugField(max_length=MAX_LENGTH_MODEL, unique=True)

    def __str__(self):
        return self.slug


class Title(models.Model):
    """Базовая модель произведений"""
    name = models.CharField(max_length=MAX_LENGTH_MODEL, verbose_name='Название')
    genre = models.ManyToManyField(Genre,
                                   related_name='genre',
                                   verbose_name='Жанр',
                                   through='GenreTitle')
    year = models.IntegerField(
        validators=[MaxValueValidator(timezone.now().year)], verbose_name='Год'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='category',
        verbose_name='Категория'
    )
    description = models.TextField(
        null=True,
        verbose_name='Описание'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Связь многие ко многим между произведениями и жанрами"""
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    piece = models.ForeignKey(Title, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.genre} - {self.piece}'


class User(AbstractUser):
    """Базовая модель пользователей"""
    email = models.EmailField(unique=True, verbose_name='Email')
    bio = models.TextField(blank=True, verbose_name='О себе')
    role = models.CharField(max_length=MAX_LENGTH_MODEL,
                            choices=ROLE_CHOICES,
                            default='user',
                            verbose_name='Роль')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_user(self):
        return self.role == 'user'

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    @property
    def is_admin(self):
        return self.role == 'admin'
