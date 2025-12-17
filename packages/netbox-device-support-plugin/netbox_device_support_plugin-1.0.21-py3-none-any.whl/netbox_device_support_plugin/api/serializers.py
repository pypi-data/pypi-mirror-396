from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from dcim.api.serializers import DeviceTypeSerializer, DeviceSerializer
from ..models import (
    CiscoDeviceTypeSupport,
    CiscoDeviceSupport,
    FortinetDeviceSupport,
    PureStorageDeviceSupport,
)


#### Cisco Support ##########################################################################################


class CiscoDeviceTypeSupportSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_device_support_plugin-api:ciscodevicetypesupport-detail"
    )

    device_type = DeviceTypeSerializer(nested=True)

    class Meta:
        model = CiscoDeviceTypeSupport
        # fmt: off
        fields = (
            "id", "url", "display", "name", "device_type", "pid", "eox_has_error", "eox_error",
            "eox_announcement_date", "end_of_sale_date", "end_of_sw_maintenance_releases",
            "end_of_security_vul_support_date", "end_of_routine_failure_analysis_date",
            "end_of_service_contract_renewal", "last_date_of_support", "end_of_svc_attach_date",
            "tags", "custom_fields", "created", "last_updated",
        )
        brief_fields = ("id", "url", "display", "name", "device_type", "pid", "eox_has_error", "eox_error")
        # fmt: on


class CiscoDeviceSupportSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_device_support_plugin-api:ciscodevicesupport-detail"
    )

    device = DeviceSerializer(nested=True)

    class Meta:
        model = CiscoDeviceSupport
        # fmt: off
        fields = (
            "id", "url", "display", "name", "device", "pid", "serial", "api_status", "sr_no_owner",
            "is_covered", "coverage_end_date", "contract_supplier", "service_line_descr",
            "service_contract_number", "warranty_end_date", "warranty_type", "partner_status",
            "partner_service_level", "partner_customer_number", "partner_coverage_end_date",
            "recommended_release", "desired_release", "current_release", "desired_release_status",
            "current_release_status", "eox_has_error", "eox_error", "eox_announcement_date",
            "end_of_sale_date", "end_of_sw_maintenance_releases", "end_of_security_vul_support_date",
            "end_of_routine_failure_analysis_date", "end_of_service_contract_renewal",
            "last_date_of_support", "end_of_svc_attach_date", "tags", "custom_fields", "created",
            "last_updated",
        )
        brief_fields = (
            "id", "url", "display", "name", "device", "pid", "serial", "api_status",
            "sr_no_owner","is_covered", "coverage_end_date", "contract_supplier",
        )
        # fmt: on


#### Fortinet Support #######################################################################################


class FortinetDeviceSupportSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_device_support_plugin-api:fortinetdevicesupport-detail"
    )

    device = DeviceSerializer(nested=True)

    class Meta:
        model = FortinetDeviceSupport
        # fmt: off
        fields = (
            "id", "url", "display", "name", "device", "pid", "serial", "recommended_release",
            "desired_release", "current_release", "desired_release_status", "current_release_status",
            "partner", "end_of_renewal_date", "end_of_support_date", "tags", "custom_fields", "created",
            "last_updated",
        )
        brief_fields = (
            "id", "url", "display", "name", "device", "pid", "serial", "recommended_release",
            "desired_release", "current_release", "desired_release_status", "current_release_status",
        )
        # fmt: on


#### PureStorage Support ####################################################################################


class PureStorageDeviceSupportSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_device_support_plugin-api:purestoragedevicesupport-detail"
    )

    device = DeviceSerializer(nested=True)

    class Meta:
        model = PureStorageDeviceSupport
        # fmt: off
        fields = (
            "id", "url", "display", "name", "device", "pid", "serial", "desired_release", "current_release",
            "tags", "custom_fields", "created", "last_updated",
        )
        brief_fields = (
            "id", "url", "display", "name", "device", "pid", "serial", "desired_release", "current_release",
        )
        # fmt: on
