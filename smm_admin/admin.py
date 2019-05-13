from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (
    Account,
    Post,
    Service,
    PostResult,
)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    pass


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 0


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    inlines = (
        ServiceInline,
    )


class PostResultInline(admin.TabularInline):
    model = PostResult
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    exclude = ['canvas_json']

    inlines = [PostResultInline]

    list_display = '__str__', 'schedule', 'status', 'services'

    list_filter = 'account', 'name', 'schedule', 'status'
    search_fields = 'name', 'schedule'

    _true = '<img src="/static/admin/img/icon-yes.svg" alt="True">'
    _false = '<img src="/static/admin/img/icon-no.svg" alt="False">'

    def services(self, obj):
        return mark_safe('<br>'.join(
            '{} {}'.format(
                self._true if res.ok else self._false,
                res.service,
            )
            for res in obj.results.all()
        ))

    @staticmethod
    def links(obj):
        return mark_safe(
            '{}<br>{}'.format(obj.artstation, obj.instagram),
        )
