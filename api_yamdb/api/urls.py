from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (UserViewSet,
                    GenresViewSet,
                    CategoriesViewSet,
                    TitlesViewSet)

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
    path('v1/auth/signup/', ),
    path('v1/auth/token/', ),
    path('v1/', include(router.urls)),
]
