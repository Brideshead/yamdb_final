from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    APIGetToken,
    APISignup,
    UsersViewSet,
    GenreViewSet,
    TitleViewSet,
    CommentViewSet,
    CategoryViewSet,
    ReviewViewSet,
)


api_name = 'api'

router = DefaultRouter()

router.register(
    'users',
    UsersViewSet,
    basename='users',
)

router.register(
    'titles',
    TitleViewSet,
    basename='titles',
)
router.register(
    'genres',
    GenreViewSet,
    basename='genres',
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments',
)
router.register(
    'categories',
    CategoryViewSet,
    basename='categories',
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews',
)


urlpatterns = [
    path(
        'v1/auth/signup/',
        APISignup.as_view(),
        name='signup',
    ),
    path(
        'v1/auth/token/',
        APIGetToken.as_view(),
        name='token',
    ),
    path('v1/', include(router.urls)),
]
