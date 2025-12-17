from django.contrib import admin
from .models import (
    CiscoDeviceTypeSupport,
    CiscoDeviceSupport,
    FortinetDeviceSupport,
    PureStorageDeviceSupport,
)


#### Cisco Support ##########################################################################################


@admin.register(CiscoDeviceTypeSupport)
class DeviceSupportAdmin(admin.ModelAdmin):
    exclude = (
        "name",
        "pid",
    )

    list_display = (
        "device_type",
        "pid",
        "eox_has_error",
        "eox_error",
        "eox_announcement_date",
        "end_of_sale_date",
        "end_of_sw_maintenance_releases",
        "end_of_security_vul_support_date",
        "end_of_routine_failure_analysis_date",
        "end_of_service_contract_renewal",
        "last_date_of_support",
        "end_of_svc_attach_date",
    )


@admin.register(CiscoDeviceSupport)
class DeviceSupportAdmin(admin.ModelAdmin):
    exclude = (
        "name",
        "serial",
        "api_status",
        "desired_release_status",
        "current_release_status",
        "pid",
        "eox_has_error",
        "eox_error",
        "eox_announcement_date",
        "end_of_sale_date",
        "end_of_sw_maintenance_releases",
        "end_of_security_vul_support_date",
        "end_of_routine_failure_analysis_date",
        "end_of_service_contract_renewal",
        "last_date_of_support",
        "end_of_svc_attach_date",
    )

    list_display = (
        "device",
        "name",
        "serial",
        "pid",
        "api_status",
        "recommended_release",
        "desired_release",
        "current_release",
        "contract_supplier",
        "sr_no_owner",
        "is_covered",
        "service_contract_number",
        "service_line_descr",
        "coverage_end_date",
        "warranty_end_date",
        "warranty_type",
        "partner_status",
        "partner_service_level",
        "partner_customer_number",
        "partner_coverage_end_date",
    )


#### Fortinet Support #######################################################################################


@admin.register(FortinetDeviceSupport)
class DeviceSupportAdmin(admin.ModelAdmin):
    exclude = (
        "name",
        "serial",
        "pid",
        "desired_release_status",
        "current_release_status",
    )

    list_display = (
        "device",
        "name",
        "serial",
        "pid",
        "recommended_release",
        "desired_release",
        "current_release",
    )


#### PureStorage Support ####################################################################################


@admin.register(PureStorageDeviceSupport)
class DeviceSupportAdmin(admin.ModelAdmin):
    exclude = (
        "name",
        "serial",
        "pid",
    )

    list_display = (
        "device",
        "name",
        "serial",
        "pid",
        "desired_release",
        "current_release",
    )
