from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SpecialUserViewSet

router_v1 = DefaultRouter()

router_v1.register('users', SpecialUserViewSet)

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]
