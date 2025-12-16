from netbox.api.viewsets import NetBoxModelViewSet
from django.db.models import Count
from django.http import JsonResponse
from django.views import View
from .. import filtersets, models
from .serializers import OrganizationSerializer, ISDASSerializer, SCIONLinkSerializer


class ISDASCoreLookupView(View):
    """
    AJAX endpoint to get available cores for a specific ISD-AS
    """
    def get(self, request):
        isdas_id = request.GET.get('isdas_id')
        if not isdas_id:
            return JsonResponse({'cores': []})
        
        try:
            isdas = models.ISDAS.objects.get(id=isdas_id)
            cores = isdas.cores or []
            return JsonResponse({'cores': cores})
        except models.ISDAS.DoesNotExist:
            return JsonResponse({'cores': []})


class OrganizationViewSet(NetBoxModelViewSet):
    queryset = models.Organization.objects.prefetch_related('isd_ases').annotate(
        isd_ases_count=Count('isd_ases')
    )
    serializer_class = OrganizationSerializer
    filterset_class = filtersets.OrganizationFilterSet


class ISDASViewSet(NetBoxModelViewSet):
    queryset = models.ISDAS.objects.select_related('organization').prefetch_related('links').annotate(
        links_count=Count('links')
    )
    serializer_class = ISDASSerializer
    filterset_class = filtersets.ISDAFilterSet


class SCIONLinkViewSet(NetBoxModelViewSet):
    queryset = models.SCIONLink.objects.select_related('isd_as', 'isd_as__organization')
    serializer_class = SCIONLinkSerializer
    filterset_class = filtersets.SCIONLinkFilterSet
