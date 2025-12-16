from django.contrib import admin
from .models import Organization, ISDAS, SCIONLink


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'full_name', 'created', 'last_updated')
    list_filter = ('created', 'last_updated')
    search_fields = ('short_name', 'full_name', 'description')
    ordering = ('short_name',)


@admin.register(ISDAS)
class ISDAAdmin(admin.ModelAdmin):
    list_display = ('isd_as', 'organization', 'created', 'last_updated')
    list_filter = ('organization', 'created', 'last_updated')
    search_fields = ('isd_as', 'description', 'organization__short_name')
    ordering = ('isd_as',)


@admin.register(SCIONLink)
class SCIONLinkAdmin(admin.ModelAdmin):
    list_display = ('isd_as', 'interface_id', 'peer_name', 'peer', 'status', 'ticket')
    list_filter = ('isd_as', 'relationship')
    search_fields = ('peer_name', 'peer', 'ticket', 'isd_as__isd_as')
