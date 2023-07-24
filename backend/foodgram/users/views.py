from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from .models import Subscription
from .pagination import LimitPageNumberPagination
from .serializers import SpecialUserSerializer, SubscribeSerializer

User = get_user_model()


class SpecialUserViewSet(UserViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = User.objects.all()
    serializer = SpecialUserSerializer
    paginations_class = LimitPageNumberPagination

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages, many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        if request.method == 'POST':
            if user == author:
                raise ValidationError('Нельзя подписаться на самого себя',
                                      code=status.HTTP_400_BAD_REQUEST)
            if Subscription.objects.filter(user=user,
                                           author=author).exists():
                raise ValidationError('Вы уже подписаны на этого автора',
                                      code=status.HTTP_400_BAD_REQUEST)
            serializer = SubscribeSerializer(
                author,
                context={'request': request})
            Subscription.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not Subscription.objects.filter(user=user,
                                               author=author).exists():
                raise ValidationError('Вы не были подписаны на этого автора',
                                      code=status.HTTP_400_BAD_REQUEST)
            subscription = get_object_or_404(Subscription,
                                             user=user, author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
