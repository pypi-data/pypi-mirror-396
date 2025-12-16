from django.urls import path
from . import views, models

app_name = 'netbox_scion'

urlpatterns = (
    # Plugin home
    path('', views.PluginHomeView.as_view(), name='home'),
    # AJAX URLs
    path('ajax/isdas-appliances/', views.get_isdas_appliances, name='isdas_appliances_ajax'),
    
    # Organization URLs
    path('organizations/', views.OrganizationListView.as_view(), name='organization_list'),
    path('organizations/add/', views.OrganizationEditView.as_view(), name='organization_add'),
    path('organizations/delete/', views.OrganizationBulkDeleteView.as_view(), name='organization_bulk_delete'),
    path('organizations/<int:pk>/', views.OrganizationView.as_view(), name='organization'),
    path('organizations/<int:pk>/edit/', views.OrganizationEditView.as_view(), name='organization_edit'),
    path('organizations/<int:pk>/delete/', views.OrganizationDeleteView.as_view(), name='organization_delete'),
    path('organizations/<int:pk>/changelog/', views.OrganizationChangeLogView.as_view(), name='organization_changelog', kwargs={'model': models.Organization}),

    # ISD-AS URLs
    path('isd-ases/', views.ISDAListView.as_view(), name='isdas_list'),
    path('isd-ases/add/', views.ISDAEditView.as_view(), name='isdas_add'),
    path('isd-ases/delete/', views.ISDABulkDeleteView.as_view(), name='isdas_bulk_delete'),
    path('isd-ases/<int:pk>/', views.ISDAView.as_view(), name='isdas'),
    path('isd-ases/<int:pk>/edit/', views.ISDAEditView.as_view(), name='isdas_edit'),
    path('isd-ases/<int:pk>/delete/', views.ISDADeleteView.as_view(), name='isdas_delete'),
    path('isd-ases/<int:pk>/changelog/', views.ISDAChangeLogView.as_view(), name='isdas_changelog', kwargs={'model': models.ISDAS}),
    # Appliance management URLs
    path('isd-ases/<int:pk>/add-appliance/', views.add_appliance_to_isdas, name='add_appliance'),
    path('isd-ases/<int:pk>/edit-appliance/<str:appliance_name>/', views.edit_appliance_in_isdas, name='edit_appliance'),
    path('isd-ases/<int:pk>/remove-appliance/<str:appliance_name>/', views.remove_appliance_from_isdas, name='remove_appliance'),

    # SCION Link URLs
    path('links/', views.SCIONLinkListView.as_view(), name='scionlink_list'),
    path('links/add/', views.SCIONLinkEditView.as_view(), name='scionlink_add'),
    path('links/delete/', views.SCIONLinkBulkDeleteView.as_view(), name='scionlink_bulk_delete'),
    path('links/<int:pk>/', views.SCIONLinkView.as_view(), name='scionlink'),
    path('links/<int:pk>/edit/', views.SCIONLinkEditView.as_view(), name='scionlink_edit'),
    path('links/<int:pk>/delete/', views.SCIONLinkDeleteView.as_view(), name='scionlink_delete'),
    path('links/<int:pk>/changelog/', views.SCIONLinkChangeLogView.as_view(), name='scionlink_changelog', kwargs={'model': models.SCIONLink}),
)
