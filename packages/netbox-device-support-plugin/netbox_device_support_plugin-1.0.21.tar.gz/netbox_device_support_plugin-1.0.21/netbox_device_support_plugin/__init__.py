from netbox.plugins import PluginConfig
from .version import __version__


class DeviceSupportConfig(PluginConfig):
    name = "netbox_device_support_plugin"
    verbose_name = "Device Support Plugin"
    description = "Device support information about software release, maintenance contract, license and more with various vendor APIs"
    version = __version__
    author = "Willi Kubny"
    author_email = "willi.kubny@gmail.com"
    base_url = "device-support"
    min_version = "3.5.0"
    required_settings = []
    default_settings = {
        # General Settings
        "TEMPLATE_EXTENSION_PLACEMENT": "right",  # "right" or "left"
        "DEVICE_VENDORS": ["Cisco"],  # List of vendors names to be used in the plugin
        # Cisco Settings
        "CISCO_MANUFACTURER": "Cisco",
        "CISCO_SUPPORT_API_CLIENT_ID": "",
        "CISCO_SUPPORT_API_CLIENT_SECRET": "",
        # Fortinet Settings
        "FORTINET_MANUFACTURER": "Fortinet",
        "FORTINET_SUPPORT_API_CLIENT_ID": "",
        "FORTINET_SUPPORT_API_CLIENT_SECRET": "",
        # PureStorage Settings
        "PURESTORAGE_MANUFACTURER": "Pure Storage",
        "PURESTORAGE_SUPPORT_API_CLIENT_ID": "",
        "PURESTORAGE_SUPPORT_API_CLIENT_SECRET": "",
    }


config = DeviceSupportConfig
