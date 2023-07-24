from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Название тега', unique=True, max_length=200)
    color = models.CharField(
        'Цвет тега', max_length=7)
    slug = models.SlugField(
        'Сокращенное название тэга',
        unique=True, max_length=200)

    class Meta:
        ordering = ('id',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингрииента', max_length=200)
    measurement_unit = models.CharField(
        'Единица измерения', max_length=200)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    name = models.CharField(
        'Название рецепта', max_length=200)
    image = models.ImageField(
        'Фото блюда из рецепта',
        upload_to='recipes/images/')
    author = models.ForeignKey(
        User, related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта')
    text = models.TextField('Описание рецепта')
    cooking_time = models.PositiveIntegerField('Время приготовления (мин)')
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True)
    tags = models.ManyToManyField(
        Tag, through='TagRecipe',
        related_name='recipes',
        verbose_name='Тэги')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты')

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Тэг в рецепте'
        verbose_name_plural = 'Тэги в рецептах'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField('Количество ингредиента')

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Любимый рецепт')

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт в списке покупок')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
