from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (
    Account,
    Post,
    LinkType,
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


@admin.register(LinkType)
class LinkTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    exclude = 'canvas_json',

    list_display = '__str__', 'schedule', 'ok', 'services'

    _true = '<img src="/static/admin/img/icon-yes.svg" alt="True">'
    _false = '<img src="/static/admin/img/icon-no.svg" alt="False">'

    def ok(self, obj):
        return mark_safe([
                             self._false,
                             self._true
                         ][obj.ok])

    def services(self, obj):
        return mark_safe('<br>'.join(
            '{} {}'.format(
                self._true if res.ok else self._false,
                res.service,
            )
            for res in obj.results.all()
        ))


@admin.register(PostResult)
class PostResultAdmin(admin.ModelAdmin):
    list_display = '__str__', 'ok', 'created_at'
    ordering = ['-created_at']
