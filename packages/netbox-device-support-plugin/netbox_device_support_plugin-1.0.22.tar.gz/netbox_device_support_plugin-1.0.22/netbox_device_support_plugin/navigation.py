from django.conf import settings
from netbox.plugins import PluginMenu
from netbox.plugins import PluginMenuItem


# Get all needed settings from the plugin settings
PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("netbox_device_support_plugin", dict())
DEVICE_VENDORS = PLUGIN_SETTINGS.get("DEVICE_VENDORS", ["Cisco"])
CISCO_MANUFACTURER = PLUGIN_SETTINGS.get("CISCO_MANUFACTURER", "Cisco")
FORTINET_MANUFACTURER = PLUGIN_SETTINGS.get("FORTINET_MANUFACTURER", "Fortinet")
PURESTORAGE_MANUFACTURER = PLUGIN_SETTINGS.get("PURESTORAGE_MANUFACTURER", "Pure Storage")

# Create an empty tuple to store the menu groups and its menu items
menu_groups = ()

#### Cisco Support ##########################################################################################

# Add the menu items for the Cisco device support views if configured in the plugin settings
if CISCO_MANUFACTURER in DEVICE_VENDORS:
    # Create a tuple to store the Cisco menu items
    cisco_device = PluginMenuItem(
        link="plugins:netbox_device_support_plugin:ciscodevicesupport_list",
        link_text="Devices",
    )
    cisco_device_type = PluginMenuItem(
        link="plugins:netbox_device_support_plugin:ciscodevicetypesupport_list",
        link_text="Device Types",
    )
    # Add the Cisco menu items to the menu group
    menu_groups += (("Cisco", (cisco_device, cisco_device_type,)),)  # fmt: skip

#### Fortinet Support #######################################################################################

# Add the menu items for the Fortinet device support views if configured in the plugin settings
if FORTINET_MANUFACTURER in DEVICE_VENDORS:
    # Create a tuple to store the Fortinet menu items
    forti_device = PluginMenuItem(
        link="plugins:netbox_device_support_plugin:fortinetdevicesupport_list",
        link_text="Devices",
    )
    # Add the Fortinet menu items to the menu group
    menu_groups += (("Fortinet", (forti_device,)),)  # fmt: skip

#### PureStorage Support ####################################################################################

# Add the menu items for the PureStorage device support views if configured in the plugin settings
if PURESTORAGE_MANUFACTURER in DEVICE_VENDORS:
    # Create a tuple to store the PureStorage menu items
    pure_device = PluginMenuItem(
        link="plugins:netbox_device_support_plugin:purestoragedevicesupport_list",
        link_text="Devices",
    )
    # Add the PureStorage menu items to the menu group
    menu_groups += (("Pure Storage", (pure_device,)),)  # fmt: skip

#### Menu ###################################################################################################

# Create the PluginMenu object with the menu groups
menu = PluginMenu(
    label="Device Support",
    icon_class="mdi mdi-lifebuoy",
    groups=menu_groups,
)
