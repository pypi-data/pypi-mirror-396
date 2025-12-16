import django_filters
from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet
from .models import Organization, ISDAS, SCIONLink


class OrganizationFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    
    class Meta:
        model = Organization
        fields = ['id', 'short_name', 'full_name']

    def search(self, queryset, name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = (
                Q(short_name__icontains=value)
                | Q(full_name__icontains=value)
                | Q(description__icontains=value)
        )
        return queryset.filter(qs_filter)


class ISDAFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    
    class Meta:
        model = ISDAS
        fields = ['id', 'isd_as', 'organization']

    def search(self, queryset, name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = (
                Q(isd_as__icontains=value)
                | Q(description__icontains=value)
                | Q(organization__short_name__icontains=value)
                | Q(organization__full_name__icontains=value)
        )
        return queryset.filter(qs_filter)


class SCIONLinkFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    
    class Meta:
        model = SCIONLink
        fields = ['id', 'isd_as', 'core', 'relationship', 'status', 'peer_name', 'peer']

    def search(self, queryset, name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = (
            Q(isd_as__isd_as__icontains=value)
            | Q(core__icontains=value)
            | Q(peer_name__icontains=value)
            | Q(peer__icontains=value)
            | Q(ticket__icontains=value)
            | Q(status__icontains=value)
        )
        return queryset.filter(qs_filter)
