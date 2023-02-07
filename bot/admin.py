from django.contrib import admin

from bot.models import TgUser


class TgUserAdmin(admin.ModelAdmin):
    list_display = ('tg_id', 'username', 'user')
    list_filter = ('tg_id', 'username')
    readonly_fields = ('tg_id', 'username', 'user_id', 'verification_code', 'user')


admin.site.register(TgUser, TgUserAdmin)
