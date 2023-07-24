from django.contrib import admin

from .models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email',
                    'first_name', 'last_name', 'is_staff')
    list_filter = ('email', 'username')
    search_fields = ('username', 'first_name', 'last_name')


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    list_filter = ('user', 'author')


admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(User, UserAdmin)
