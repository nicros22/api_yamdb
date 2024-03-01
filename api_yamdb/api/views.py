import secrets

from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt import tokens
from reviews.models import Category, Genre, Title, User

from .filters import TitleFilter
from .mixins import ReviewsModelMixin
from .permissions import (AuthorOrAdmin, IsAdminOrReadOnly,
                          IsOwnerOrModeratorOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          ConfirmationSerializer, GenreSerializer,
                          MeSerializer, ReviewSerializer, SignUpSerializer,
                          TitleSerializer, TitleViewSerializer, UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('pk')
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (AuthorOrAdmin,)
    filter_backends = (SearchFilter,)
    lookup_field = 'username'
    filterset_fields = ('username')
    search_fields = ('username', )

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PUT')

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=(IsAuthenticated, ),
        url_path='me',
    )
    def about_me(self, request):
        user = get_object_or_404(User, username=self.request.user)
        if request.method == 'GET':
            serializer = MeSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = MeSerializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class GenresViewSet(ReviewsModelMixin):
    queryset = Genre.objects.all().order_by('pk')
    serializer_class = GenreSerializer


class CategoriesViewSet(ReviewsModelMixin):
    queryset = Category.objects.all().order_by('pk')
    serializer_class = CategorySerializer


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('pk')
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    pagination_class = PageNumberPagination

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed(request.method)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve',):
            return TitleViewSerializer
        return TitleSerializer

    def partial_update(self, request, *args, **kwargs):
        name = request.data.get('name')
        if name and len(name) > 256:
            raise ValidationError(
                'Название произведения не может быть длиннее 256 символов.')
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def handle_exception(self, exc):
        if isinstance(exc, MethodNotAllowed):
            return Response(
                {'detail': 'Метод не разрешен'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED)
        if isinstance(exc, ValidationError):
            return Response(
                {'detail': str(exc)},
                status=status.HTTP_400_BAD_REQUEST)
        return super().handle_exception(exc)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsOwnerOrModeratorOrReadOnly]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        new_queryset = title.reviews.all()
        return new_queryset

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)

    def update(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Метод не разрешен'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrModeratorOrReadOnly]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        try:
            review = title.reviews.get(id=self.kwargs.get('review_id'))
        except TypeError:
            TypeError('У произведения нет такого отзыва')
        queryset = review.comments.all().order_by('pk')
        return queryset

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        try:
            review = title.reviews.get(id=self.kwargs.get('review_id'))
        except TypeError:
            TypeError('У произведения нет такого отзыва')
        serializer.save(author=self.request.user, review=review)

    def update(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Метод не разрешен'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class AuthenticationViewset(viewsets.GenericViewSet):
    def send_confirmation_email(self, email, confirmation_code):
        subject = 'Confirmation Code for YourApp'
        message = f'Your confirmation code is: {confirmation_code}'
        from_email = 'yamdb@yamdb.com'
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)

    @action(
        methods=['POST'],
        detail=False,
        url_path='signup',
        url_name='signup',
        permission_classes=(AllowAny,)
    )
    def signup(self, request):
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
                self.send_confirmation_email(
                    existing_user.email,
                    confirmation_code
                )
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

            self.send_confirmation_email(user.email, confirmation_code)

            return Response(
                serializer.validated_data,
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['POST'],
        detail=False,
        url_path='token',
        url_name='toekn',
        permission_classes=(AllowAny,)
    )
    def get_token(self, request):
        serializer = ConfirmationSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            confirmation_code = serializer.validated_data['confirmation_code']
            user = get_object_or_404(User, username=username)

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
