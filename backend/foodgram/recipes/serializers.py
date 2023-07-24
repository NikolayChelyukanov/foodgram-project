from django.core.validators import MinValueValidator
from django.shortcuts import get_object_or_404
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from .models import (
    Favorite, Ingredient, IngredientRecipe, Recipe, ShoppingCart, Tag,
)
from users.serializers import SpecialUserSerializer


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeFavoriteShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientRecipeReadSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_id(self, obj):
        return obj.ingredient.id

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class IngredientRecipeWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(validators=(MinValueValidator(1),))

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount',)


class RecipeReadSerializer(serializers.ModelSerializer):
    author = SpecialUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')

    @staticmethod
    def get_ingredients(recipe):
        ingredients = IngredientRecipe.objects.filter(recipe=recipe)
        return IngredientRecipeReadSerializer(ingredients, many=True).data

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=recipe).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    author = SpecialUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    ingredients = IngredientRecipeWriteSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(validators=(MinValueValidator(1),))

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time')

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            amount = ingredient['amount']
            ingredient = get_object_or_404(Ingredient, pk=ingredient['id'])
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.set(tags)
        ingredients = validated_data.pop('ingredients', None)
        if ingredients is not None:
            instance.ingredients.clear()
            for ingredient in ingredients:
                amount = ingredient['amount']
                ingredient = get_object_or_404(Ingredient, pk=ingredient['id'])
                IngredientRecipe.objects.update_or_create(
                    recipe=instance,
                    ingredient=ingredient,
                    defaults={'amount': amount})
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')})
        return serializer.data
