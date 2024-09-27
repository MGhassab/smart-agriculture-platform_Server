from django.contrib import admin

from Baghyar.admin import get_linked_repr
from LightApp.models import Verification, DebugLog


@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'username_field', 'code', 'expire', 'send_sms', )
    search_fields = ('id', 'username_field')

    def username_field(self, verify: Verification):
        return verify.customer.user.username
    username_field.short_description = 'کاربر'


@admin.register(DebugLog)
class DebugLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created', 'description', )

