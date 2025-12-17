from django.conf import settings
from netbox.plugins import PluginTemplateExtension
from .models import (
    CiscoDeviceTypeSupport,
    CiscoDeviceSupport,
    FortinetDeviceSupport,
    PureStorageDeviceSupport,
)


# Get all needed settings from the plugin settings
PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("netbox_device_support_plugin", dict())
TEMPLATE_EXTENSION_PLACEMENT = PLUGIN_SETTINGS.get("TEMPLATE_EXTENSION_PLACEMENT", "right")


#### Cisco Support ##########################################################################################


class CiscoDeviceTypeSupportInformation(PluginTemplateExtension):
    models = ["dcim.devicetype"]

    def _template_content(self):
        try:
            cisco_device_type_support = CiscoDeviceTypeSupport.objects.get(device_type=self.context["object"])
        except CiscoDeviceTypeSupport.DoesNotExist:
            cisco_device_type_support = None

        return self.render(
            "cisco/cisco_device_type_support.html",
            {"cisco_device_type_support": cisco_device_type_support},
        )

    if TEMPLATE_EXTENSION_PLACEMENT == "left":

        def left_page(self):
            return self._template_content()

    else:

        def right_page(self):
            return self._template_content()


class CiscoDeviceSupportInformation(PluginTemplateExtension):
    models = ["dcim.device"]

    def _template_content(self):
        try:
            cisco_device_support = CiscoDeviceSupport.objects.get(device=self.context["object"])
        except CiscoDeviceSupport.DoesNotExist:
            cisco_device_support = None

        try:
            cisco_device_type_support = CiscoDeviceTypeSupport.objects.get(
                device_type=self.context["object"].device_type
            )
        except CiscoDeviceTypeSupport.DoesNotExist:
            cisco_device_type_support = None

        return self.render(
            "cisco/cisco_device_support.html",
            {
                "cisco_device_support": cisco_device_support,
                "cisco_device_type_support": cisco_device_type_support,
            },
        )

    if TEMPLATE_EXTENSION_PLACEMENT == "left":

        def left_page(self):
            return self._template_content()

    else:

        def right_page(self):
            return self._template_content()


#### Fortinet Support #######################################################################################


class FortinetDeviceSupportInformation(PluginTemplateExtension):
    models = ["dcim.device"]

    def _template_content(self):
        try:
            fortinet_device_support = FortinetDeviceSupport.objects.get(device=self.context["object"])
        except FortinetDeviceSupport.DoesNotExist:
            fortinet_device_support = None

        return self.render(
            "fortinet/fortinet_device_support.html",
            {"fortinet_device_support": fortinet_device_support},
        )

    if TEMPLATE_EXTENSION_PLACEMENT == "left":

        def left_page(self):
            return self._template_content()

    else:

        def right_page(self):
            return self._template_content()


#### PureStorage Support ####################################################################################


class PureStorageDeviceSupportInformation(PluginTemplateExtension):
    models = ["dcim.device"]

    def _template_content(self):
        try:
            purestorage_device_support = PureStorageDeviceSupport.objects.get(device=self.context["object"])
        except PureStorageDeviceSupport.DoesNotExist:
            purestorage_device_support = None

        return self.render(
            "purestorage/purestorage_device_support.html",
            {"purestorage_device_support": purestorage_device_support},
        )

    if TEMPLATE_EXTENSION_PLACEMENT == "left":

        def left_page(self):
            return self._template_content()

    else:

        def right_page(self):
            return self._template_content()


#### Template Extensions ####################################################################################

# Template extensions to be loaded when the plugin is loaded
template_extensions = [
    CiscoDeviceTypeSupportInformation,
    CiscoDeviceSupportInformation,
    FortinetDeviceSupportInformation,
    PureStorageDeviceSupportInformation,
]
