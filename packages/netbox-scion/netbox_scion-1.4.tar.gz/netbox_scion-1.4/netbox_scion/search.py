from netbox.search import SearchIndex, register_search
from .models import Organization, ISDAS, SCIONLink


@register_search
class OrganizationIndex(SearchIndex):
    model = Organization
    fields = (
        ('short_name', 100),
        ('full_name', 200),
        ('description', 500),
    )


@register_search
class ISDAIndex(SearchIndex):
    model = ISDAS
    fields = (
        ('isd_as', 100),
        ('description', 500),
    )


@register_search
class SCIONLinkIndex(SearchIndex):
    model = SCIONLink
    fields = (
        ('core', 100),
        ('peer_name', 150),
        ('peer', 150),
        ('status', 50),
        ('ticket', 200),
    )
