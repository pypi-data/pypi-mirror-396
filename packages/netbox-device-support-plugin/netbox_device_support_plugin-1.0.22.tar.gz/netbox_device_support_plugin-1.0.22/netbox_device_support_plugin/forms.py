from django import forms
from netbox.forms.mixins import SavedFiltersMixin
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, FilterForm
from utilities.forms.rendering import FieldSet
from .models import (
    CiscoDeviceSupport,
    CiscoDeviceTypeSupport,
    FortinetDeviceSupport,
    PureStorageDeviceSupport,
)


#### Cisco Support ##########################################################################################


class CiscoDeviceSupportFilterForm(SavedFiltersMixin, FilterForm):
    model = CiscoDeviceSupport

    fieldsets = (
        FieldSet(
            "name",
            "pid",
            name=("General"),
        ),
        FieldSet(
            "recommended_release",
            "desired_release_status",
            "desired_release",
            "current_release_status",
            "current_release",
            name=("Software Release"),
        ),
        FieldSet(
            "sr_no_owner",
            "is_covered",
            "contract_supplier",
            "coverage_end_date",
            "service_line_descr",
            "warranty_end_date",
            name=("Device Support"),
        ),
        FieldSet(
            "partner_status",
            "partner_service_level",
            "partner_customer_number",
            "partner_coverage_end_date",
            name=("Partner Contract"),
        ),
        FieldSet(
            "eox_has_error",
            "eox_error",
            "eox_announcement_date",
            "end_of_sale_date",
            "end_of_sw_maintenance_releases",
            "end_of_security_vul_support_date",
            "end_of_routine_failure_analysis_date",
            "end_of_service_contract_renewal",
            "end_of_svc_attach_date",
            "last_date_of_support",
            name=("Device Type Support"),
        ),
    )

    name = forms.CharField(
        required=False,
        label="Device Name",
        help_text="Case-insensitive exact match",
    )

    pid = forms.CharField(
        required=False,
        label="PID",
        help_text="Case-insensitive exact match",
    )

    recommended_release = forms.CharField(
        required=False,
        label="Recommended Release",
        help_text="Case-insensitive containment test",
    )

    desired_release_status = forms.NullBooleanField(
        required=False,
        label="Desired Release Status",
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        help_text="True if the desired release matchs the recommended release",
    )

    desired_release = forms.CharField(
        required=False,
        label="Desired Release",
        help_text="Case-insensitive exact match",
    )

    current_release_status = forms.NullBooleanField(
        required=False,
        label="Current Release Status",
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        help_text="True if the current release matchs the desired release",
    )

    current_release = forms.CharField(
        required=False,
        label="Current Release",
        help_text="Case-insensitive exact match",
    )

    sr_no_owner = forms.NullBooleanField(
        required=False,
        label="Serial Owner",
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        help_text="True if the API user is associated with contract and device",
    )

    is_covered = forms.NullBooleanField(
        required=False,
        label="Is Covered",
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        help_text="True if the device is covered by a maintenance contract",
    )

    contract_supplier = forms.CharField(
        required=False,
        label="Contract Supplier",
        help_text="Case-insensitive containment test",
    )

    coverage_end_date = forms.CharField(
        required=False,
        label="End of Coverage Year",
        help_text="Specify the coverage end year (exact year match)",
    )

    service_line_descr = forms.CharField(
        required=False,
        label="Service Level",
        help_text="Case-insensitive containment test",
    )

    warranty_end_date = forms.CharField(
        required=False,
        label="Coverage End Date Year",
        help_text="Specify the warranty end year (exact year match)",
    )

    partner_status = forms.CharField(
        required=False,
        label="Partner Contract Status",
        help_text="Case-insensitive containment test",
    )

    partner_service_level = forms.CharField(
        required=False,
        label="Partner Service Level",
        help_text="Case-insensitive containment test",
    )

    partner_customer_number = forms.CharField(
        required=False,
        label="Partner Customer Number",
        help_text="Case-insensitive exact match",
    )

    partner_coverage_end_date = forms.CharField(
        required=False,
        label="Partner End of Coverage Year",
        help_text="Specify the coverage end year (exact year match)",
    )

    eox_has_error = forms.NullBooleanField(
        required=False,
        label="Has EoX Error",
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        help_text="True if the EoX API returned an error",
    )

    eox_error = forms.CharField(
        required=False,
        label="EoX Error",
        help_text="Case-insensitive containment test",
    )

    eox_announcement_date = forms.CharField(
        required=False,
        label="EoX Announcement Year",
        help_text="Specify the EoX announcement year (exact year match)",
    )

    end_of_sale_date = forms.CharField(
        required=False,
        label="End of Sales Year",
        help_text="Specify the end of sales year (exact year match)",
    )

    end_of_sw_maintenance_releases = forms.CharField(
        required=False,
        label="End of Software Maintenance Year",
        help_text="Specify the end of software maintenance release year (exact year match)",
    )

    end_of_security_vul_support_date = forms.CharField(
        required=False,
        label="End of Security Vulnerability Year",
        help_text="Specify the end of security vulnerability support year (exact year match)",
    )

    end_of_routine_failure_analysis_date = forms.CharField(
        required=False,
        label="End of Routine Failure Analysis Year",
        help_text="Specify the end of routine failure analysis year (exact year match)",
    )

    end_of_service_contract_renewal = forms.CharField(
        required=False,
        label="End of Service Contract Renewal Year",
        help_text="Specify the end of service contract renewal year (exact year match)",
    )

    end_of_svc_attach_date = forms.CharField(
        required=False,
        label="End of New Service-and-Support Contract Year",
        help_text="Specify the end of service-and-support contract year (exact year match)",
    )

    last_date_of_support = forms.CharField(
        required=False,
        label="Last Date of Support Year",
        help_text="Specify the last date of support year (exact year match)",
    )


class CiscoDeviceTypeSupportFilterForm(SavedFiltersMixin, FilterForm):
    model = CiscoDeviceTypeSupport

    fieldsets = (
        FieldSet(
            "name",
            "pid",
            name=("General"),
        ),
        FieldSet(
            "eox_has_error",
            "eox_error",
            "eox_announcement_date",
            "end_of_sale_date",
            "end_of_sw_maintenance_releases",
            "end_of_security_vul_support_date",
            "end_of_routine_failure_analysis_date",
            "end_of_service_contract_renewal",
            "end_of_svc_attach_date",
            "last_date_of_support",
            name=("Device Type Support"),
        ),
    )

    name = forms.CharField(
        required=False,
        label="Device Type Name",
        help_text="Case-insensitive exact match",
    )

    pid = forms.CharField(
        required=False,
        label="PID",
        help_text="Case-insensitive exact match",
    )

    eox_has_error = forms.NullBooleanField(
        required=False,
        label="Has EoX Error",
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        help_text="True if the EoX API returned an error",
    )

    eox_error = forms.CharField(
        required=False,
        label="EoX Error",
        help_text="Case-insensitive containment test",
    )

    eox_announcement_date = forms.CharField(
        required=False,
        label="EoX Announcement Year",
        help_text="Specify the EoX announcement year (exact year match)",
    )

    end_of_sale_date = forms.CharField(
        required=False,
        label="End of Sales Year",
        help_text="Specify the end of sales year (exact year match)",
    )

    end_of_sw_maintenance_releases = forms.CharField(
        required=False,
        label="End of Software Maintenance Year",
        help_text="Specify the end of software maintenance release year (exact year match)",
    )

    end_of_security_vul_support_date = forms.CharField(
        required=False,
        label="End of Security Vulnerability Year",
        help_text="Specify the end of security vulnerability support year (exact year match)",
    )

    end_of_routine_failure_analysis_date = forms.CharField(
        required=False,
        label="End of Routine Failure Analysis Year",
        help_text="Specify the end of routine failure analysis year (exact year match)",
    )

    end_of_service_contract_renewal = forms.CharField(
        required=False,
        label="End of Service Contract Renewal Year",
        help_text="Specify the end of service contract renewal year (exact year match)",
    )

    end_of_svc_attach_date = forms.CharField(
        required=False,
        label="End of New Service-and-Support Contract Year",
        help_text="Specify the end of service-and-support contract year (exact year match)",
    )

    last_date_of_support = forms.CharField(
        required=False,
        label="Last Date of Support Year",
        help_text="Specify the last date of support year (exact year match)",
    )


#### Fortinet Support #######################################################################################


class FortinetDeviceSupportFilterForm(SavedFiltersMixin, FilterForm):
    model = FortinetDeviceSupport

    fieldsets = (
        FieldSet(
            "name",
            "pid",
            name=("General"),
        ),
        FieldSet(
            "recommended_release",
            "desired_release_status",
            "desired_release",
            "current_release_status",
            "current_release",
            name=("Software Release"),
        ),
        FieldSet(
            "partner",
            "end_of_renewal_date",
            "end_of_support_date",
            name=("Device Support"),
        ),
    )

    name = forms.CharField(
        required=False,
        label="Device Name",
        help_text="Case-insensitive exact match",
    )

    pid = forms.CharField(
        required=False,
        label="PID",
        help_text="Case-insensitive exact match",
    )

    recommended_release = forms.CharField(
        required=False,
        label="Recommended Release",
        help_text="Case-insensitive containment test",
    )

    desired_release_status = forms.NullBooleanField(
        required=False,
        label="Desired Release Status",
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        help_text="True if the desired release matchs the recommended release",
    )

    desired_release = forms.CharField(
        required=False,
        label="Desired Release",
        help_text="Case-insensitive exact match",
    )

    current_release_status = forms.NullBooleanField(
        required=False,
        label="Current Release Status",
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        help_text="True if the current release matchs the desired release",
    )

    current_release = forms.CharField(
        required=False,
        label="Current Release",
        help_text="Case-insensitive exact match",
    )

    partner = forms.CharField(
        required=False,
        label="Partner",
        help_text="Case-insensitive exact match",
    )

    end_of_renewal_date = forms.CharField(
        required=False,
        label="End of Renewal Year",
        help_text="Specify the end of renewal year (exact year match)",
    )

    end_of_support_date = forms.CharField(
        required=False,
        label="End of Support Year",
        help_text="Specify the end of support year (exact year match)",
    )


#### PureStorage Support ####################################################################################


class PureStorageDeviceSupportFilterForm(SavedFiltersMixin, FilterForm):
    model = PureStorageDeviceSupport

    fieldsets = (
        FieldSet(
            "name",
            "pid",
            name=("General"),
        ),
        FieldSet(
            "desired_release",
            "current_release",
            name=("Software Release"),
        ),
    )

    name = forms.CharField(
        required=False,
        label="Device Name",
        help_text="Case-insensitive exact match",
    )

    pid = forms.CharField(
        required=False,
        label="PID",
        help_text="Case-insensitive exact match",
    )

    desired_release = forms.CharField(
        required=False,
        label="Desired Release",
        help_text="Case-insensitive exact match",
    )

    current_release = forms.CharField(
        required=False,
        label="Current Release",
        help_text="Case-insensitive exact match",
    )
