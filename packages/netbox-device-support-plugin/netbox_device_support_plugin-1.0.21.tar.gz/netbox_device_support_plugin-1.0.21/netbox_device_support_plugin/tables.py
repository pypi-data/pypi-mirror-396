import django_tables2 as tables
from django.utils.translation import gettext as _

from netbox.tables import NetBoxTable, columns
from .models import (
    CiscoDeviceSupport,
    CiscoDeviceTypeSupport,
    FortinetDeviceSupport,
    PureStorageDeviceSupport,
)


#### Cisco Support ##########################################################################################


class CiscoDeviceSupportTable(NetBoxTable):
    id = tables.Column(linkify=False)

    device = tables.Column(linkify=True)

    desired_release_status = columns.BooleanColumn()
    current_release_status = columns.BooleanColumn()
    sr_no_owner = columns.BooleanColumn()
    is_covered = columns.BooleanColumn()
    eox_has_error = columns.BooleanColumn()

    coverage_end_date = columns.DateColumn()
    warranty_end_date = columns.DateColumn()
    partner_coverage_end_date = columns.DateColumn()
    eox_announcement_date = columns.DateColumn()
    end_of_sale_date = columns.DateColumn()
    end_of_sw_maintenance_releases = columns.DateColumn()
    end_of_security_vul_support_date = columns.DateColumn()
    end_of_routine_failure_analysis_date = columns.DateColumn()
    end_of_service_contract_renewal = columns.DateColumn()
    end_of_svc_attach_date = columns.DateColumn()
    last_date_of_support = columns.DateColumn()

    actions = columns.ActionsColumn(actions=("delete",))

    class Meta(NetBoxTable.Meta):
        model = CiscoDeviceSupport
        # fmt: off
        fields = (
            "pk", "id", "device", "pid", "serial", "recommended_release", "desired_release",
            "current_release", "desired_release_status", "current_release_status", "api_status",
            "sr_no_owner", "is_covered", "contract_supplier", "coverage_end_date", "service_line_descr",
            "service_contract_number", "warranty_end_date", "warranty_type", "partner_status",
            "partner_service_level", "partner_customer_number", "partner_coverage_end_date",
            "eox_has_error", "eox_error", "eox_announcement_date", "end_of_sale_date",
            "end_of_sw_maintenance_releases", "end_of_security_vul_support_date",
            "end_of_routine_failure_analysis_date", "end_of_service_contract_renewal",
            "last_date_of_support", "end_of_svc_attach_date",
        )
        default_columns = (
            "device", "desired_release_status", "desired_release", "current_release_status",
            "current_release", "sr_no_owner", "is_covered", "contract_supplier", "coverage_end_date",
            "service_line_descr", "eox_announcement_date",
        )
        # fmt: on


class CiscoDeviceTypeSupportTable(NetBoxTable):
    id = tables.Column(linkify=False)

    device_type = tables.Column(linkify=True)

    eox_has_error = columns.BooleanColumn()

    eox_announcement_date = columns.DateColumn()
    end_of_sale_date = columns.DateColumn()
    end_of_sw_maintenance_releases = columns.DateColumn()
    end_of_security_vul_support_date = columns.DateColumn()
    end_of_routine_failure_analysis_date = columns.DateColumn()
    end_of_service_contract_renewal = columns.DateColumn()
    end_of_svc_attach_date = columns.DateColumn()
    last_date_of_support = columns.DateColumn()

    actions = columns.ActionsColumn(actions=("delete",))

    class Meta(NetBoxTable.Meta):
        model = CiscoDeviceTypeSupport
        # fmt: off
        fields = (
            "pk", "id", "device_type", "pid", "eox_has_error", "eox_error", "eox_announcement_date",
            "end_of_sale_date", "end_of_sw_maintenance_releases", "end_of_security_vul_support_date",
            "end_of_routine_failure_analysis_date", "end_of_service_contract_renewal",
            "last_date_of_support", "end_of_svc_attach_date",
        )
        default_columns = (
            "device_type", "eox_has_error", "eox_error", "eox_announcement_date", "end_of_sale_date",
            "end_of_sw_maintenance_releases", "end_of_security_vul_support_date",
            "end_of_routine_failure_analysis_date", "end_of_service_contract_renewal",
            "last_date_of_support", "end_of_svc_attach_date",
        )
        # fmt: on


#### Fortinet Support #######################################################################################


class FortinetDeviceSupportTable(NetBoxTable):
    id = tables.Column(linkify=False)

    device = tables.Column(linkify=True)

    desired_release_status = columns.BooleanColumn()
    current_release_status = columns.BooleanColumn()

    actions = columns.ActionsColumn(actions=("delete",))

    class Meta(NetBoxTable.Meta):
        model = FortinetDeviceSupport
        # fmt: off
        fields = (
            "pk", "id", "device", "pid", "serial", "recommended_release", "desired_release",
            "current_release", "desired_release_status", "current_release_status", "partner",
            "end_of_renewal_date", "end_of_support_date",
        )
        default_columns = (
            "device", "desired_release_status", "desired_release", "current_release_status",
            "current_release", "end_of_renewal_date", "end_of_support_date",
        )
        # fmt: on


#### PureStorage Support ####################################################################################


class PureStorageDeviceSupportTable(NetBoxTable):
    id = tables.Column(linkify=False)

    device = tables.Column(linkify=True)

    actions = columns.ActionsColumn(actions=("delete",))

    class Meta(NetBoxTable.Meta):
        model = PureStorageDeviceSupport
        # fmt: off
        fields = (
            "pk", "id", "device", "pid", "serial", "desired_release", "current_release",
        )
        default_columns = (
            "device", "desired_release", "current_release",
        )
        # fmt: on
