from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (UserViewSet,
                    GenresViewSet,
                    CategoriesViewSet,
                    TitlesViewSet,
                    get_token,
                    signup)

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('genres', GenresViewSet, basename='genres')
router.register('categories', CategoriesViewSet, basename='categories')
router.register('titles', TitlesViewSet, basename='titles')
# router.register(
#     r'titles/(?P<title_id>\d+)/reviews',
#     ReviewViewSet,
#     basename='reviews',
# )
# router.register(
#     r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
#     CommentViewSet,
#     basename='comments',
# )

urlpatterns = [
    path('v1/auth/signup/', signup),
    path('v1/auth/token/', get_token),
    path('v1/', include(router.urls)),
]
