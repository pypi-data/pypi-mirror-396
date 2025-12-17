from django.conf import settings
from netbox.api.routers import NetBoxRouter
from . import views


# Get all needed settings from the plugin settings
PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("netbox_device_support_plugin", dict())
DEVICE_VENDORS = PLUGIN_SETTINGS.get("DEVICE_VENDORS", ["Cisco"])
CISCO_MANUFACTURER = PLUGIN_SETTINGS.get("CISCO_MANUFACTURER", "Cisco")
FORTINET_MANUFACTURER = PLUGIN_SETTINGS.get("FORTINET_MANUFACTURER", "Fortinet")
PURESTORAGE_MANUFACTURER = PLUGIN_SETTINGS.get("PURESTORAGE_MANUFACTURER", "Pure Storage")

# Set the Django app name
app_name = "netbox_device_support_plugin"

# Create the NetBoxRouter
router = NetBoxRouter()

# Create the Cisco Support URLs
if CISCO_MANUFACTURER in DEVICE_VENDORS:
    router.register(r"cisco-device", views.CiscoDeviceSupportViewSet)
    router.register(r"cisco-device-type", views.CiscoDeviceTypeSupportViewSet)

if FORTINET_MANUFACTURER in DEVICE_VENDORS:
    # Create the Fortnet Support URLs
    router.register(r"fortinet-device", views.FortinetDeviceSupportViewSet)

if PURESTORAGE_MANUFACTURER in DEVICE_VENDORS:
    # Create the PureStorage Support URLs
    router.register(r"purestorage-device", views.PureStorageDeviceSupportViewSet)

# Create the urlpatterns
urlpatterns = router.urls
