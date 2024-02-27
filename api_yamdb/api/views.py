from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

from .mixins import ReviewsModelMixin
from .serializers import (UserSerializer,
                          MeSerializer,
                          GenreSerializer,
                          CategorySerializer,
                          TitleSerializer,
                          TitleViewSerializer,
                          CommentSerializer,
                          ReviewSerializer)
from reviews.models import Category, Genre, Title, User
from .filters import TitleFilter



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'username'
    lookup_value_regex = r'[\w\@\.\+\-]+'
    filter_backends = (SearchFilter, )
    search_fields = ('username', )

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[IsAuthenticated],
        url_path='me',
        url_name='me',
    )
    def about_me(self, request):
        user = get_object_or_404(User, username=self.request.user)
        if request.method == 'GET':
            serializer = MeSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'PATCH':
            serializer = MeSerializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class GenresViewSet(ReviewsModelMixin):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoriesViewSet(ReviewsModelMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    #permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH',):
            return TitleViewSerializer
        return TitleSerializer
      
      
class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_title(self):
        title_id = self.kwargs['title_id']
        return get_object_or_404(Title, id=title_id)

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(user=self.request.user, title=title)
        review = serializer.instance
        review.title.average_rating()

    def perform_update(self, serializer):
        review = serializer.save()
        review.title.average_rating()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_review(self):
        title_id = self.kwargs['title_id']
        review_id = self.kwargs['review_id']
        return get_object_or_404(Review, id=review_id, title__id=title_id)

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)