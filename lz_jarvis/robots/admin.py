from django.contrib import admin

from robots.models import RSeoStatus


@admin.register(RSeoStatus)
class RSeoStatusAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'owner',
        'keyword',
        'domain',
        'google',
        'yahoo',
        'bing',
        'duckduck',
        'destination'
    )
