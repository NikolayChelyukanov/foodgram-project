from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        'Имя пользователя для входа в приложение',
        max_length=150,
        unique=True,
        null=False,
        blank=False)
    email = models.EmailField(
        'Адрес электронной почты',
        max_length=254,
        blank=False,
        null=False,
        unique=True)
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=False)
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=False)
    password = models.CharField(
        'Пароль',
        max_length=150,
        blank=False)

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь, который подписывается')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор, на которого подписываются')

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
