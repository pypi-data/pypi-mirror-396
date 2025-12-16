from django.conf import settings
from netbox.plugins import PluginMenu, PluginMenuItem, PluginMenuButton

plugin_settings = settings.PLUGINS_CONFIG.get('netbox_scion', {})

organization_button = PluginMenuButton(
    link='plugins:netbox_scion:organization_add',
    title='Add',
    icon_class='mdi mdi-plus-thick',
)

isdas_button = PluginMenuButton(
    link='plugins:netbox_scion:isdas_add',
    title='Add',
    icon_class='mdi mdi-plus-thick',
)

scionlink_button = PluginMenuButton(
    link='plugins:netbox_scion:scionlink_add',
    title='Add',
    icon_class='mdi mdi-plus-thick',
)

_menu_items = (
    PluginMenuItem(
        link='plugins:netbox_scion:organization_list',
        link_text='Organizations',
        buttons=(organization_button,)
    ),
    PluginMenuItem(
        link='plugins:netbox_scion:isdas_list',
        link_text='ISD-ASes',
        buttons=(isdas_button,)
    ),
    PluginMenuItem(
        link='plugins:netbox_scion:scionlink_list',
        link_text='SCION Links',
        buttons=(scionlink_button,)
    ),
)

_menu_items_primary = _menu_items

if plugin_settings.get('top_level_menu'):
    menu = PluginMenu(
        label="SCION",
        groups=(
            ("SCION", _menu_items),
        ),
        icon_class="mdi mdi-wan",
    )
else:
    menu_items = _menu_items_primary