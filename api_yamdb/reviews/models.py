from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from reviews.validators import validate_year
from users.models import User


class Genre(models.Model):
    """Жанры произведений."""
    name = models.CharField(
        max_length=256,
        verbose_name='Название жанра',
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Slug жанра',
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name', ]

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(
        'Имя категории',
        max_length=200,
    )
    slug = models.SlugField(
        'Slug категории',
        unique=True,
        db_index=True,
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return f'{self.name} {self.name}'


class Title(models.Model):
    """
    Модель объектов произведений.

    Attributes:
        name: Название произведения.
        year: Год публикации.
        category: Категория произведения. Установлена связь
            с моделью Category, при удалении категории
            у произведения удаляются данные о категории.
        description: Описание произведения.
        genre: Жанр произведения. Установлена связь
            с моделью Genre.
    """
    name = models.CharField(
        'название',
        max_length=200,
        db_index=True,
    )
    year = models.IntegerField(
        'год',
        validators=(validate_year,),
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='категория',
        null=True,
        blank=True,
    )
    description = models.TextField(
        'описание',
        max_length=255,
        null=True,
        blank=True,
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='жанр',
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self) -> str:
        """Возвращаем в консоль назв. произведения."""
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='произведение',
    )
    text = models.CharField(
        max_length=200,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='автор',
    )
    score = models.PositiveSmallIntegerField(
        'оценка',
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10),
        ),
        error_messages={'validators': 'Оценка от 1 до 10'},
    )
    pub_date = models.DateTimeField(
        'дата публикации',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author',),
                name='unique_review',
            ),
        ]
        ordering = ('pub_date',)

    def __str__(self):
        return self.text


class GenreTitle(models.Model):
    """Произведения - жанры."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Жанр',
    )

    class Meta:
        verbose_name = 'Произведение и жанр'
        verbose_name_plural = 'Произведения и жанры'

    def __str__(self):
        return f'{self.title} в жанре {self.genre}'


class Comment(models.Model):
    """
    Модель комментариев.

    Attributes:
        review: Отзыв. Установлена связь
            с моделью Review, при удалении отзыва
            удаляются все комментарии к данному отзыву.
        text: Текст комментария.
        author: Автор комментария. Установлена связь
            с моделью User, при удалении пользователя
            удаляется также все комментарии данного
            пользователя.
        pub_date: Дата публикации комментария.
    """

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='отзыв',
    )
    text = models.TextField(
        'текст комментария',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор',
    )
    pub_date = models.DateTimeField(
        'дата публикации',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        """Возвращаем в консоль текст комментария."""
        return f'{self.text[:30]} : {self.author}'
