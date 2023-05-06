from typing import List

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from api.filters import TitleFilter
from api.mixins import ModelMixinSet
from api.permissions import (
    AdminOnly,
    IsAdminUserOrReadOnly,
    AdminModeratorAuthorPermission,

)
from api.serializers import TokenSerializer, SignupSerializer
from api.serializers import (
    UsersSerializer,
    NotAdminSerializer,
    CommentSerializer,
    CategorySerializer,
    GenreSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    ReviewSerializer,
)
from reviews.models import Title, Genre, Category, Review
from users.models import User


class TitleViewSet(ModelViewSet):
    """
    Вьюсет для модели Title.

    Права доступа: Админ,
    остальные только на чтение.
    """

    queryset = Title.objects.annotate(
        rating=Avg('reviews__score'),
    ).all()
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self) -> serializers:
        """
        Выбор класса сериализатора.

        Returns:
            В завимости от команды возвращает
            класс сериализатора на чтение или на запись.
        """
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class GenreViewSet(ModelMixinSet):
    """Админ может создавать жанры, остальные только просматривать."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'slug'
    search_fields = ('name',)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для модели Comment.

    Права доступа: админ, модератор и авторизованный пользователь.
    Дополнительно:
    1) get_queryset() - получать список комментариев к отзыву.
    2) Переопределяем perform_create() - создавать комментарии
    к отзывам.
    """
    serializer_class = CommentSerializer
    permission_classes = (AdminModeratorAuthorPermission,)

    def get_queryset(self) -> List[str]:
        """
        Запрашиваем список комментариев к отзыву.

        Returns:
            Если отзыв существует , возврашает список комментариев
            к данному отзыву.
        """
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
        )
        return review.comments.all()

    def perform_create(self, serializer: CommentSerializer) -> None:
        """
        Авт. пользователи, модераторы и админы могут создавать комментарии.
        Args:
        serializer: преобразование POST запроса
        в JSON объект со всей информацией о комментарии.
        """
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
        )
        serializer.save(
            author=self.request.user,
            review=review,
        )


class CategoryViewSet(ModelMixinSet):
    """
    Получить доступ всех категорий. Права доступа : дотсупно без токена
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (AdminModeratorAuthorPermission,)

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'),
        )
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'),
        )
        serializer.save(author=self.request.user, title=title)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (AdminOnly, IsAuthenticated)
    lookup_field = 'username'
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me',
    )
    def get_current_user_info(self, request):
        serializer = UsersSerializer(request.user)
        if request.method == 'PATCH':
            if request.user.is_admin:
                serializer = UsersSerializer(
                    request.user,
                    data=request.data,
                    partial=True,
                )
            else:
                serializer = NotAdminSerializer(
                    request.user,
                    data=request.data,
                    partial=True,
                )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data)


class APIGetToken(APIView):
    """Получение JWT-token'a."""

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user = User.objects.get(username=data['username'])
        except User.DoesNotExist:
            return Response(
                {'username': 'Пользователь не найден'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if data.get('confirmation_code') == user.confirmation_code:
            token = RefreshToken.for_user(user).access_token
            return Response(
                {'token': str(token)},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {'confirmation_code': 'Неправильный код'},
            status=status.HTTP_400_BAD_REQUEST,
        )


class APISignup(APIView):
    """Получение кода подтверждения."""

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)

        if not serializer.is_valid(raise_exception=True):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        email = serializer.data.get('email')
        username = serializer.data.get('username')
        user, created = User.objects.get_or_create(
            email=email,
            username=username,
        )
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            'Код подтверждения YaMDb',
            f'Здравствуйте, {user.username}!'
            f'\nВаш код подтверждения: {confirmation_code}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
