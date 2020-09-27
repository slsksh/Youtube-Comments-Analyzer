from django.contrib import admin
from .models import UserInfo
# Register your models here.
class UserInfoAdmin(admin.ModelAdmin):
	pass

admin.site.register(UserInfo, UserInfoAdmin)
