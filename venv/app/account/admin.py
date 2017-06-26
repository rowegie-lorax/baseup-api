from django.contrib import admin
from .models import User, Account

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = ('first_name', 'last_name', 'email', 'is_active', 'is_admin', )
	exclude = ('create_at', 'update_at', 'password')


admin.site.register(Account)
