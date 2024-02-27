from sys import stderr
import secrets
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from rest_framework import status, viewsets, decorators
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt import tokens
from loguru import logger
from django.contrib.auth.hashers import check_password

from .mixins import ReviewsModelMixin
from .serializers import (UserSerializer,
                          MeSerializer,
                          GenreSerializer,
                          CategorySerializer,
                          TitleSerializer,
                          TitleViewSerializer,
                          SignUpSerializer,
                          ConfirmationSerializer,
                          CommentSerializer,
                          ReviewSerializer)

from reviews.models import Category, Genre, Title, User
from .filters import TitleFilter

logger.add(stderr, format='<white>{time:HH:mm:ss}</white>'
                          ' | <level>{level: <8}</level>'
                          ' | <cyan>{line}</cyan>'
                          ' - <white>{message}</white>')



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
    # permission_classes = (IsAdminOrReadOnly,)
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


def send_confirmation_email(email, confirmation_code):
    subject = 'Confirmation Code for YourApp'
    message = f'Your confirmation code is: {confirmation_code}'
    from_email = 'yamdb@yamdb.com'
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list)


@decorators.api_view(['POST'])
def signup(request):
    serializer = SignUpSerializer(data=request.data)
    existing_user = User.objects.filter(
        username=request.data.get('username')
    ).first()
    existing_mail = User.objects.filter(
        email=request.data.get('email')
    ).first()
    if existing_user or existing_mail:
        email = request.data.get('email')
        confirmation_code = secrets.token_hex(6)
        if not existing_user:
            return Response(
                {'email': [email,]},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not existing_mail:
            return Response(
                {'username': [existing_user.username,]},
                status=status.HTTP_400_BAD_REQUEST
            )
        if email == existing_user.email:
            existing_user.set_password(confirmation_code)
            existing_user.save()
            send_confirmation_email(existing_user.email, confirmation_code)
            return Response({
                'email': existing_user.email,
                'username': existing_user.username
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'email': [email,],
                 'username': [existing_user.username,]},
                status=status.HTTP_400_BAD_REQUEST
            )

    if serializer.is_valid():
        confirmation_code = secrets.token_hex(6)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')

        user = User.objects.create(username=username, email=email)
        user.set_password(confirmation_code)
        user.save()

        send_confirmation_email(user.email, confirmation_code)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@decorators.api_view(['POST'])
def get_token(request):
    serializer = ConfirmationSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']
        user = User.objects.get(username=username)

        if check_password(confirmation_code, user.password):
            refresh = tokens.RefreshToken.for_user(user)
            return Response(
                {'token': f'{refresh.access_token}'},
                status=status.HTTP_200_OK
            )

    return Response(
        {'message': 'Invalid confirmation code'},
        status=status.HTTP_400_BAD_REQUEST
    )

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)