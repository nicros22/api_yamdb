from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.db import models
from .abstract import BaseModel
from django.utils import timezone

from .constants import MAX_LENGTH_MODEL, MAX_LENGTH_EMAIL

ROLE_CHOICES = (
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Админ'),
)


class Category(BaseModel):
    """Базовая модель категорий."""


class Genre(BaseModel):
    """Базовая модель жанров."""


class Title(models.Model):
    """Базовая модель произведений."""

    def year_validator(value):
        if value > timezone.now().year:
            raise ValidationError('Год не может быть будущим.')

    name = models.CharField(
        max_length=MAX_LENGTH_MODEL,
        verbose_name='Название',
    )
    genre = models.ManyToManyField(Genre,
                                   related_name='genre',
                                   verbose_name='Жанр',
                                   through='GenreTitle')
    year = models.SmallIntegerField(
        validators=[year_validator], verbose_name='Год'
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
        ordering = ('name',)

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Связь многие ко многим между произведениями и жанрами."""

    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    piece = models.ForeignKey(Title, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.genre} - {self.piece}'


class User(AbstractUser):
    """Базовая модель пользователей."""

    email = models.EmailField(unique=True,
                              verbose_name='Email',
                              max_length=MAX_LENGTH_EMAIL)
    bio = models.TextField(blank=True, verbose_name='О себе')
    role = models.CharField(max_length=MAX_LENGTH_MODEL,
                            choices=ROLE_CHOICES,
                            default='user',
                            verbose_name='Роль')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    @property
    def is_admin(self):
        return self.role == 'admin'


class Review(models.Model):
    """Модель для отзывов."""

    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField(max_length=MAX_LENGTH_MODEL)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)], default=0)
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'], name="unique_review")
        ]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Модель для комментариев."""

    review = models.ForeignKey(
        Review, on_delete=models.CASCADE)
    text = models.TextField(max_length=MAX_LENGTH_MODEL)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.review
