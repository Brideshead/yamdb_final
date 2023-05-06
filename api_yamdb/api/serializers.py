from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title
from users.validators import validate_username
from users.models import User


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'bio',
        )


class NotAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'bio',
        )
        read_only_fields = ('role',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ('id',)
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        lookup_field = 'slug'
        exclude = ('id',)


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализация Title на чтение."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(
        read_only=True,
        many=True,
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализация Title на запись."""

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
    )

    class Meta:
        fields = '__all__'
        model = Title


class CommentSerializer(serializers.ModelSerializer):
    """Сериализация модели Комментариев."""

    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True,
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        fields = '__all__'
        model = Comment


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Review
        fields = '__all__'

    def validate_score(self, score):
        if not 0 < score <= 10:
            raise serializers.ValidationError('Оценка от 1 до 10 ')
        return score

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if (
                request.method == 'POST'
                and Review.objects.filter(title=title, author=author).exists()
        ):
            raise ValidationError('Нельзя оставлять несколько отзывов')
        return data


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[
            validate_username,
        ],
    )

    email = serializers.EmailField(
        required=True,
        max_length=254,
    )

    def validate(self, data):
        """Валидация e-mail и username."""
        email = data.get('email')
        username = data.get('username')
        try:
            user = User.objects.get(email=email)
            if username != user.username:
                raise ValidationError(
                    f'Пользователю {username} соответствует другой e-mail',
                )
        except User.DoesNotExist:
            pass

        try:
            user = User.objects.get(username=username)
            if email != user.email:
                raise ValidationError(
                    'Пара username/email не зарегистрирована в сервисе',
                )
        except User.DoesNotExist:
            pass
        return data


class TokenSerializer(serializers.ModelSerializer):
    confirmation_code = serializers.CharField(
        required=True,
    )
    username = serializers.CharField(
        required=True,
        max_length=150,
    )

    class Meta:
        model = User
        fields = (
            'username',
            'confirmation_code',
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )
        read_only_fields = ('role',)


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )
