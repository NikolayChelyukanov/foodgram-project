import datetime as dt

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter
from .models import (
    Favorite, Ingredient, IngredientRecipe, Recipe, ShoppingCart, Tag,
)
from .permissions import IsAuthorAdminOrReadOnlyPermission
from .serializers import (
    IngredientSerializer, RecipeFavoriteSerializer, RecipeReadSerializer,
    RecipeShoppingCartSerializer, RecipeWriteSerializer, TagSerializer,
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (IsAuthorAdminOrReadOnlyPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        user = request.user
        recipe_id = self.kwargs.get('pk')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if self.request.method == 'POST':
            serializer = RecipeFavoriteSerializer(
                recipe,
                data={'id': recipe.id,
                      'name': recipe.name,
                      'image': recipe.image,
                      'cooking_time': recipe.cooking_time},
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            Favorite.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            favorite = Favorite.objects.filter(user=user,
                                               recipe=recipe).first()
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, **kwargs):
        user = request.user
        recipe_id = self.kwargs.get('pk')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if self.request.method == 'POST':
            serializer = RecipeShoppingCartSerializer(
                recipe,
                data={'id': recipe.id,
                      'name': recipe.name,
                      'image': recipe.image,
                      'cooking_time': recipe.cooking_time},
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            ShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        if self.request.method == 'DELETE':
            shopping_cart = ShoppingCart.objects.filter(user=user,
                                                        recipe=recipe).first()
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        HEADER_FONT_SIZE = 18
        BODY_FONT_SIZE = 14
        FOOTER_FONT_SIZE = 8
        LEFT_MARGIN = 80
        HEADER_TOP_MARGIN = 770
        HEADER_LINE_SPACE = 30
        HEADER_SECOND_LINE = HEADER_TOP_MARGIN - HEADER_LINE_SPACE
        BODY_TOP_MARGIN = HEADER_SECOND_LINE - HEADER_LINE_SPACE
        BODY_LINE_SPACE = 20
        FOOTER_LINE_SPACE = 10

        recipes_ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_cart__user=request.user).order_by('ingredient')
        cart = recipes_ingredients.values(
            'ingredient__name',
            'ingredient__measurement_unit').annotate(total=Sum('amount'))
        recipes = ShoppingCart.objects.filter(
            user=request.user).values('recipe__name')

        shopping_list = []
        for ingredient in cart:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            total = ingredient['total']
            line = u'\u2022' + f' {name} ({unit}) - {total}'
            shopping_list.append(line)

        recipes_list = []
        for recipe in recipes:
            recipes_list.append(recipe['recipe__name'])

        timestamp = dt.datetime.utcnow() + dt.timedelta(hours=3)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="My_list.pdf"'
        pdf_file = canvas.Canvas(response, pagesize=A4)
        registerFont(TTFont('DejaVuSerif', 'DejaVuSerif.ttf'))

        pdf_file.setFont('DejaVuSerif', HEADER_FONT_SIZE)
        pdf_file.drawString(
            LEFT_MARGIN, HEADER_TOP_MARGIN,
            f'Список покупок пользователя {request.user.get_full_name()}')
        pdf_file.setFont('DejaVuSerif', BODY_FONT_SIZE)
        pdf_file.drawString(LEFT_MARGIN, HEADER_SECOND_LINE,
                            'Для приготовления: ' + ', '.join(recipes_list))
        pdf_file.setFont('DejaVuSerif', BODY_FONT_SIZE)
        for ingredient in shopping_list:
            pdf_file.drawString(LEFT_MARGIN, BODY_TOP_MARGIN, ingredient)
            BODY_TOP_MARGIN -= BODY_LINE_SPACE
        pdf_file.setFont('DejaVuSerif', FOOTER_FONT_SIZE)
        pdf_file.drawString(
            LEFT_MARGIN,
            BODY_TOP_MARGIN - FOOTER_LINE_SPACE,
            'Создано в приложении Foodgram ' + timestamp.strftime(
                '%d-%m-%Y %H:%M'))
        pdf_file.drawString(
            LEFT_MARGIN, BODY_TOP_MARGIN - FOOTER_LINE_SPACE * 2,
            'Автор: Николай Челюканов')

        pdf_file.showPage()
        pdf_file.save()
        return response
