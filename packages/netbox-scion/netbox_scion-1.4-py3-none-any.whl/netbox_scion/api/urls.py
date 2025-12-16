from django.urls import path
from netbox.api.routers import NetBoxRouter
from . import views

app_name = 'netbox_scion'

router = NetBoxRouter()
router.register('organizations', views.OrganizationViewSet)
# Use hyphenated paths to follow NetBox conventions
router.register('isd-ases', views.ISDASViewSet)
router.register('links', views.SCIONLinkViewSet)

urlpatterns = router.urls + [
    path('isdas-cores/', views.ISDASCoreLookupView.as_view(), name='isdas-cores'),
]
