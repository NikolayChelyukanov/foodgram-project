from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from .models import Subscription, User
from recipes.models import Recipe


class SpecialUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed')

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=author).exists()


class RecipeSubscriptionSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(SpecialUserSerializer):
    recipes_count = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)

    class Meta(SpecialUserSerializer.Meta):
        fields = SpecialUserSerializer.Meta.fields + (
            'recipes', 'recipes_count')
        read_only_fields = ('email', 'username')

    def get_recipes_count(self, author):
        return author.recipes.count()

    def get_recipes(self, author):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = author.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeSubscriptionSerializer(
            recipes, many=True, read_only=True)
        return serializer.data

    @staticmethod
    def get_recipes_count(obj):
        return obj.recipes.count()


class SpecialUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'password')
