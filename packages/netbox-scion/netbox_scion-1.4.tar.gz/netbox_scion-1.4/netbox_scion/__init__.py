from netbox.plugins import PluginConfig

__version__ = '1.4'

class NetBoxScionConfig(PluginConfig):
    # REQUIRED plugin attributes
    name = 'netbox_scion'  # This MUST match your folder name and PLUGINS setting
    verbose_name = 'SCION'  # This appears as the menu section name
    description = 'NetBox plugin for managing SCION ISD-AS and Links'
    version = '1.4'
    author = 'Anapaya Systems AG'
    author_email = 'ops@anapaya.net'
    
    # The default_settings can be empty if you have none
    default_settings = {
        'top_level_menu': True,
    }
    required_settings = []
    # Set the base URL for the plugin's views
    base_url = 'scion'
    # Wire UI and API URLConfs (module-relative paths per NetBox expectations)
    urls = 'urls'
    api_urls = 'api.urls'
    
    # Optional settings
    required_settings = []


# This is REQUIRED. It tells NetBox which class is the configuration entry point.
config = NetBoxScionConfig
