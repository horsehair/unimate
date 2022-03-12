from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from django.contrib.auth.models import User
from .models import *

# Register your models here.


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "profile"

class SMSInline(admin.StackedInline):
    model = SMSAuthRequest
    can_delete = False
    verbose_name_plural = "sms"


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, SMSInline,)


admin.site.register(User, UserAdmin)
admin.site.register(Profile)
admin.site.register(Withdraw)
admin.site.register(Room)
admin.site.register(RoomUser)

admin.site.register(University)
admin.site.register(College)
admin.site.register(Major)

admin.site.register(Meet)
admin.site.register(MeetUser)