import sys
import time
import requests
from colorama import Fore, Style, init
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.exceptions import MultipleObjectsReturned
from typing import Generator, Union
from datetime import datetime
from dcim.choices import DeviceStatusChoices
from dcim.models import Manufacturer
from dcim.models import Device, DeviceType
from netbox_device_support_plugin.models import CiscoDeviceTypeSupport, CiscoDeviceSupport

init(autoreset=True, strip=False)


class Command(BaseCommand):
    help = "Sync local devices and device types with Cisco Support APIs"

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            "--manufacturer",
            action="store_true",
            default="Cisco",
            help="Manufacturer name (default: Cisco)",
        )

    def task_title(self, title: str) -> None:
        """
        Prints a Nornir style title.
        """
        msg = f"**** {title} "
        return f"\n{Style.BRIGHT}{Fore.GREEN}{msg}{'*' * (90 - len(msg))}{Fore.RESET}{Style.RESET_ALL}"

    def task_name(self, text: str) -> None:
        """
        Prints a Nornir style host task title.
        """
        msg = f"{text} "
        return f"\n{Style.BRIGHT}{Fore.CYAN}{msg}{'*' * (90 - len(msg))}{Fore.RESET}{Style.RESET_ALL}"

    def task_info(self, text: str, changed: bool) -> str:
        """
        Returns a Nornir style task info message.
        """
        color = Fore.YELLOW if changed else Fore.GREEN
        msg = f"---- {text} ** changed : {str(changed)} "
        return f"{Style.BRIGHT}{color}{msg}{'-' * (90 - len(msg))} INFO{Fore.RESET}{Style.RESET_ALL}"

    def task_error(self, text: str, changed: bool) -> str:
        """
        Returns a Nornir style task error message.
        """
        msg = f"---- {text} ** changed : {str(changed)} "
        return f"{Style.BRIGHT}{Fore.RED}{msg}{'-' * (90 - len(msg))} ERROR{Fore.RESET}{Style.RESET_ALL}"

    def task_host(self, host: str, changed: bool) -> str:
        """
        Returns a Nornir style host task name.
        """
        msg = f"* {host} ** changed : {str(changed)} "
        return f"{Style.BRIGHT}{Fore.BLUE}{msg}{'*' * (90 - len(msg))}{Fore.RESET}{Style.RESET_ALL}"

    def iterate_all(self, iterable: Union[list, dict], returned: str = "key") -> Generator:
        """Returns an iterator that returns all keys or values of a (nested) iterable.
        Arguments:
            - iterable: <list> or <dictionary>
            - returned: <string> "key" or "value" or <tuple of strings> "key-value"
        Returns:
            - <Generator>
        """
        if isinstance(iterable, dict):
            for key, value in iterable.items():
                if returned == "key":
                    yield key
                elif returned == "value":
                    if not isinstance(value, dict) or isinstance(value, list):
                        yield value
                elif returned == "key-value":
                    if not isinstance(value, dict) or isinstance(value, list):
                        yield key, value
                else:
                    raise ValueError("'returned' keyword only accepts 'key' or 'value' or 'key-value'.")
                for ret in self.iterate_all(value, returned=returned):
                    yield ret
        elif isinstance(iterable, list):
            for item in iterable:
                for ret in self.iterate_all(item, returned=returned):
                    yield ret

    def find_base_pid(self, data_dict):
        # Set a emptry PID string and if the PID can't be updated the empty PID string is returned
        pid = ""
        for item in self.iterate_all(iterable=data_dict, returned="key-value"):
            # Skip empty PID values
            if item[1] and item[0] == "base_pid":
                pid = item[1]
                break
            elif item[1] and item[0] == "orderable_pid":
                pid = item[1]
                break
        # Some basePID needs -A / -E to be removed or the API call will fail -> Maybe is a bug in the API
        pid_prefixes = ["C9300X-24Y", "C9500-32C", "C9500-48Y4C"]
        if pid.startswith(tuple(pid_prefixes)):
            # The software package suffix -A or -E can be removed
            pid = pid[:-2] if pid.endswith(tuple(["-A", "-E"])) else pid

        return pid

    def get_cisco_support_api_data(self, url, header):
        # Create a empty data dict for verification and to fill with the API response
        data = {}

        # Get the Cisco Support API data
        # Terminate the while loop with a timeout of max 120s (2min)
        timeout_start = time.time()
        while time.time() < timeout_start + 120:
            # Get the Cisco Support API data
            response = requests.get(url=url, headers=header, verify=False, timeout=self.REQUESTS_TIMEOUT)
            # Validate the API response
            if response.status_code == 200:
                # Deserialize JSON API Response into Python object "data"
                data = response.json()
                # Break out of the while loop
                break
            else:
                # Sleep and continue the while loop
                time.sleep(1)

        # Return the API response and the data dict which is empty in case the response was not successful
        return response, data

    def update_device_ss_data(self, serial_number, pid, data):
        #### Get model object for device type ###############################################################
        text = f"Get data for serial number {serial_number} with PID {pid}"
        # Get the device object from NetBox
        try:
            d = Device.objects.get(serial=serial_number)
        except MultipleObjectsReturned:
            # Error if netbox has multiple SN's and skip updating
            print(self.task_error(text=text, changed=False))
            print(f"Multiple objects exist within Netbox with serial number {serial_number}")
            return False

        # Check if a CiscoDeviceSupport object already exists, if not, create a new one
        try:
            ds = CiscoDeviceSupport.objects.get(device=d)
        except CiscoDeviceSupport.DoesNotExist:
            ds = CiscoDeviceSupport(device=d)

        #### Get recommended_release ########################################################################
        if isinstance(data, str):
            print(self.task_info(text=text, changed=False))
            print(f"{serial_number} - {data}")
            # Update recommended_release, desired_release and current_release
            ds.recommended_release = data
            ds.desired_release = data  # Needed for custom models save function
            ds.current_release = data  # # Needed for custom models save function
            # Save model object for device
            ds.save()

            return True

        # Empty string to fill with the recommended releases and the error description
        recommended_release = ""
        error_description = ""
        # As there can be multiple suggestions with the same ID and release, but only with different mdfId,
        # the no_duplicates list will be created to eliminate duplicate IDs and release information.
        no_duplicates = []

        for item in data["productList"]:
            # Skip list item if it's not a device software release type (e.g. NBAR2 Protocol Packs)
            device_release_list = ["IOS Software", "IOS XE Software", "NX-OS System Software-MDS"]
            if item["product"]["softwareType"] not in device_release_list:
                continue
            # Iterate over all softwar release suggestions
            for idx, suggestion in enumerate(item["suggestions"]):
                idx = idx + 1
                if suggestion["releaseFormat1"] and suggestion["releaseFormat1"] not in no_duplicates:
                    no_duplicates.append(suggestion["releaseFormat1"])
                    recommended_release += f"ID: {idx}, Release: {suggestion['releaseFormat1']}\n"
                elif (
                    suggestion["errorDetailsResponse"]
                    and suggestion["errorDetailsResponse"]["errorDescription"] not in no_duplicates
                ):
                    error_description += f"{suggestion['errorDetailsResponse']['errorDescription']}\n"

        # If the recommended_release string is empty, print the error_description and return False
        if not recommended_release:
            error_description_stdout = error_description.replace("\n", " / ")
            # Remove the last two characters from the string to remove the trailing slash
            if error_description_stdout.endswith(" / "):
                error_description_stdout = error_description_stdout[:-2]
            # Error 'No records Found' is not a real error, but a valid response from the API
            if "No records Found" in error_description:
                print(self.task_info(text=text, changed=False))
                print(f"{serial_number} - recommended_release: No records Found")
                # Update recommended_release if the value has changed
                if ds.recommended_release != "No records Found":
                    ds.recommended_release = "No records Found"
                    # Save model object for device
                    ds.save()

                return True
            # Else it's a real error. Print the error description and return False
            print(self.task_error(text=text, changed=False))
            print(f"{serial_number} - recommended_release: {error_description_stdout}")
            # Update recommended_release if the value has changed
            if ds.recommended_release != "":
                ds.recommended_release = ""
                # Save model object for device
                ds.save()

            return False

        recommended_release_stdout = recommended_release.replace("\n", " / ")
        # Remove the last two characters from the string to remove the trailing slash
        if recommended_release_stdout.endswith(" / "):
            recommended_release_stdout = recommended_release_stdout[:-2]

        print(self.task_info(text=text, changed=False))
        print(f"{serial_number} - recommended_release: {recommended_release_stdout}")
        # Update recommended_release if the value has changed
        if ds.recommended_release != recommended_release:
            ds.recommended_release = recommended_release
            # Save model object for device
            ds.save()

        # Desired release and current release can't be gathered by the Cisco Support API.
        # They should be added/updated over the RestAPI

        return True

    # Updates a single device with current SNI coverage status data
    def update_device_sni_status_data(self, device):
        #### Get model object for device type ###############################################################
        text = f"Get data for serial number {device['sr_no']}"
        # Get the device object from NetBox
        try:
            d = Device.objects.get(serial=device["sr_no"])
        except MultipleObjectsReturned:
            # Error if netbox has multiple SN's and skip updating
            print(self.task_error(text=text, changed=False))
            print(f"Multiple objects exist within Netbox with serial number {device['sr_no']}")
            return False

        # Check if a CiscoDeviceSupport object already exists, if not, create a new one
        try:
            ds = CiscoDeviceSupport.objects.get(device=d)
        except CiscoDeviceSupport.DoesNotExist:
            ds = CiscoDeviceSupport(device=d)

        #### Get sr_no_owner and api_status #################################################################
        # A "YES" string is not quite boolean :-)
        sr_no_owner = True if device["sr_no_owner"] == "YES" else False

        print(self.task_info(text=text, changed=False))
        print(f"{device['sr_no']} - sr_no_owner: {sr_no_owner}")

        # Update sr_no_owner and save model object for device
        if ds.sr_no_owner != sr_no_owner:
            ds.sr_no_owner = sr_no_owner
            ds.save()

        return True

    # Updates a single device with current SNI coverage summary data
    def update_device_sni_summary_data(self, device):
        # Control variable to only save the object if something has changed
        value_changed = False

        #### Get model object for device ####################################################################
        text = f"Get data for serial number {device['sr_no']}"
        # Get the device object from NetBox
        try:
            d = Device.objects.get(serial=device["sr_no"])
        except MultipleObjectsReturned:
            # Error if netbox has multiple SN's and skip updating
            print(self.task_error(text=text, changed=False))
            print(f"Multiple objects exist within Netbox with serial number {device['sr_no']}")
            return False

        # Check if a CiscoDeviceSupport object already exists, if not, create a new one
        try:
            ds = CiscoDeviceSupport.objects.get(device=d)
        except CiscoDeviceSupport.DoesNotExist:
            ds = CiscoDeviceSupport(device=d)

        #### Check if an error is present for the serial ####################################################

        if "ErrorResponse" in device:
            print(self.task_error(text=text, changed=False))
            error = device["ErrorResponse"]["APIError"]
            print(f"{device['sr_no']} - ErrorCode: {error['ErrorCode']}")
            print(f"{device['sr_no']} - ErrorDescription: {error['ErrorDescription']}")
            print(f"{device['sr_no']} - SuggestedAction: {error['SuggestedAction']}")
            return False

        print(self.task_info(text=text, changed=False))

        #### Get is_covered and contract_supplier ###########################################################
        # A "YES" string is not quite boolean :-)
        is_covered = True if device["is_covered"] == "YES" else False

        print(f"{device['sr_no']} - covered: {is_covered}")

        # Update is_covered if the value has changed
        if ds.is_covered != is_covered:
            ds.is_covered = is_covered
            value_changed = True

        # The field contract_supplier and all fields regarding a Cisco partner contract like IBM TLS can't be
        # updated by the script and should be updated over the REST API.

        #### Get service_contract_number ####################################################################
        try:
            if not device["service_contract_number"]:
                print(f"{device['sr_no']} - service_contract_number: None")
            else:
                service_contract_number = device["service_contract_number"]
                print(f"{device['sr_no']} - service_contract_number: {service_contract_number}")

                # Update service_contract_number if the value has changed
                if ds.service_contract_number != service_contract_number:
                    ds.service_contract_number = service_contract_number
                    value_changed = True

        except KeyError:
            print(f"{device['sr_no']} - service_contract_number: None")

        #### Get service_line_descr #########################################################################
        try:
            if not device["service_line_descr"]:
                print(f"{device['sr_no']} - service_line_descr: None")
            else:
                service_line_descr = device["service_line_descr"]
                print(f"{device['sr_no']} - service_line_descr: {service_line_descr}")

                # Update service_line_descr if the value has changed
                if ds.service_line_descr != service_line_descr:
                    ds.service_line_descr = service_line_descr
                    value_changed = True

        except KeyError:
            print(f"{device['sr_no']} - service_line_descr: None")

        #### Get warranty_type ##############################################################################
        try:
            if not device["warranty_type"]:
                print(f"{device['sr_no']} - warranty_type: None")
            else:
                warranty_type = device["warranty_type"]
                print(f"{device['sr_no']} - warranty_type: {warranty_type}")

                # Update warranty_type if the value has changed
                if ds.warranty_type != warranty_type:
                    ds.warranty_type = warranty_type
                    value_changed = True

        except KeyError:
            print(f"{device['sr_no']} - warranty_type: None")

        #### Get warranty_end_date ##########################################################################
        try:
            if not device["warranty_end_date"]:
                print(f"{device['sr_no']} - warranty_end_date: None")
            else:
                warranty_end_date_string = device["warranty_end_date"]
                warranty_end_date = datetime.strptime(warranty_end_date_string, "%Y-%m-%d").date()
                print(f"{device['sr_no']} - warranty_end_date: {warranty_end_date}")

                # Update warranty_end_date if the value has changed
                if ds.warranty_end_date != warranty_end_date:
                    ds.warranty_end_date = warranty_end_date
                    value_changed = True

        except KeyError:
            print(f"{device['sr_no']} - warranty_end_date: : None")

        #### Get covered_product_line_end_date ##############################################################
        try:
            if not device["covered_product_line_end_date"]:
                print(f"{device['sr_no']} - covered_product_line_end_date: None")
            else:
                coverage_end_date_string = device["covered_product_line_end_date"]
                coverage_end_date = datetime.strptime(coverage_end_date_string, "%Y-%m-%d").date()
                print(f"{device['sr_no']} - coverage_end_date: {coverage_end_date}")

                # Update coverage_end_date if the value has changed
                if ds.coverage_end_date != coverage_end_date:
                    ds.coverage_end_date = coverage_end_date
                    value_changed = True

        except KeyError:
            print(f"{device['sr_no']} - coverage_end_date: None")

        #### Save model object for device ###################################################################
        if value_changed:
            ds.save()

        return True

    def update_device_type_eox_data(self, pid, data):
        # Control variable to only save the object if something has changed
        value_changed = False

        #### Get model object for device type ###############################################################
        try:
            # Get the device type object for the supplied PID
            dt = DeviceType.objects.get(part_number=pid)

        except MultipleObjectsReturned:
            # Error if netbox has multiple PN's
            print(self.task_error(text=f"Get data for part number {pid}", changed=False))
            print(f"Multiple objects exist within Netbox with part number {pid}")
            return False

        # Check if CiscoDeviceTypeSupport record already exists
        try:
            dts = CiscoDeviceTypeSupport.objects.get(device_type=dt)
        # If not, create a new one for this Device Type
        except CiscoDeviceTypeSupport.DoesNotExist:
            dts = CiscoDeviceTypeSupport(device_type=dt)

        #### Get eox_has_error and eox_error ################################################################
        # Check if JSON contains EOXError with value field of the eox_errors list
        if "EOXError" in data["EOXRecord"][0]:
            # Error SSA_ERR_026 is good: EOX information does not exist for the following product ID(s)
            if (
                "SSA_ERR_026" in data["EOXRecord"][0]["EOXError"]["ErrorID"]
                or "EoX information does not exist" in data["EOXRecord"][0]["EOXError"]["ErrorDescription"]
            ):
                eox_has_error = False
                eox_error = "No EoX information announced"
                output = f"{pid} - eox_has_error: {eox_has_error}\n{pid} - {eox_error}"
            else:
                eox_has_error = True
                eox_error = data["EOXRecord"][0]["EOXError"]["ErrorDescription"]
                output = f"{pid} - eox_has_error: {eox_has_error}\n{pid} - EoXError: {eox_error}"

        # Do nothing when JSON field does not exist
        else:
            eox_has_error = False
            eox_error = None
            output = f"{pid} - eox_has_error: {eox_has_error}\n{pid} - EoX information announced"

        # Print the output for eox_has_error and eox_error
        if eox_has_error:
            print(self.task_error(text=f"Get data for PID {pid}", changed=False))
        else:
            print(self.task_info(text=f"Get data for PID {pid}", changed=False))
        print(output)

        # Update eox_has_error and eox_error if the value has changed
        if dts.eox_has_error != eox_has_error:
            dts.eox_has_error = eox_has_error
            value_changed = True
        if dts.eox_error != eox_error:
            dts.eox_error = eox_error
            value_changed = True

        #### Get eox_announcement_date ######################################################################
        try:
            # Check if JSON contains EOXExternalAnnouncementDate with value field
            if not data["EOXRecord"][0]["EOXExternalAnnouncementDate"]["value"]:
                print(f"{pid} - eox_announcement_date: None")
            else:
                eox_announcement_date_string = data["EOXRecord"][0]["EOXExternalAnnouncementDate"]["value"]
                # Cast this value to datetime.date object
                eox_announcement_date = datetime.strptime(eox_announcement_date_string, "%Y-%m-%d").date()
                print(f"{pid} - eox_announcement_date: {eox_announcement_date}")

                # Update eox_announcement_date if the value has changed
                if dts.eox_announcement_date != eox_announcement_date:
                    dts.eox_announcement_date = eox_announcement_date
                    value_changed = True

        # Do nothing when JSON field does not exist
        except KeyError:
            print(f"{pid} - eox_announcement_date: None")

        #### Get end_of_sale_date ###########################################################################
        try:
            # Check if JSON contains EndOfSaleDate with value field
            if not data["EOXRecord"][0]["EndOfSaleDate"]["value"]:
                print(f"{pid} - end_of_sale_date: None")
            else:
                end_of_sale_date_string = data["EOXRecord"][0]["EndOfSaleDate"]["value"]
                # Cast this value to datetime.date object
                end_of_sale_date = datetime.strptime(end_of_sale_date_string, "%Y-%m-%d").date()
                print(f"{pid} - end_of_sale_date: {end_of_sale_date}")

                # Update end_of_sale_date if the value has changed
                if dts.end_of_sale_date != end_of_sale_date:
                    dts.end_of_sale_date = end_of_sale_date
                    value_changed = True

        # Do nothing when JSON field does not exist
        except KeyError:
            print(f"{pid} - end_of_sale_date: None")

        #### Get end_of_sw_maintenance_releases #############################################################
        try:
            if not data["EOXRecord"][0]["EndOfSWMaintenanceReleases"]["value"]:
                print(f"{pid} - end_of_sw_maintenance_releases: None")
            else:
                end_of_sw_maintenance_releases_string = data["EOXRecord"][0]["EndOfSWMaintenanceReleases"][
                    "value"
                ]
                end_of_sw_maintenance_releases = datetime.strptime(
                    end_of_sw_maintenance_releases_string, "%Y-%m-%d"
                ).date()
                print(f"{pid} - end_of_sw_maintenance_releases: {end_of_sw_maintenance_releases}")

                # Update end_of_sw_maintenance_releases if the value has changed
                if dts.end_of_sw_maintenance_releases != end_of_sw_maintenance_releases:
                    dts.end_of_sw_maintenance_releases = end_of_sw_maintenance_releases
                    value_changed = True

        # Do nothing when JSON field does not exist
        except KeyError:
            print(f"{pid} - end_of_sw_maintenance_releases: None")

        #### Get end_of_security_vul_support_date ###########################################################
        try:
            if not data["EOXRecord"][0]["EndOfSecurityVulSupportDate"]["value"]:
                print(f"{pid} - end_of_security_vul_support_date: None")
            else:
                end_of_security_vul_support_date_string = data["EOXRecord"][0]["EndOfSecurityVulSupportDate"][
                    "value"
                ]
                end_of_security_vul_support_date = datetime.strptime(
                    end_of_security_vul_support_date_string, "%Y-%m-%d"
                ).date()
                print(f"{pid} - end_of_security_vul_support_date: {end_of_security_vul_support_date}")

                # Update end_of_security_vul_support_date if the value has changed
                if dts.end_of_security_vul_support_date != end_of_security_vul_support_date:
                    dts.end_of_security_vul_support_date = end_of_security_vul_support_date
                    value_changed = True

        # Do nothing when JSON field does not exist
        except KeyError:
            print(f"{pid} - end_of_security_vul_support_date: None")

        #### Get end_of_routine_failure_analysis_date #######################################################
        try:
            if not data["EOXRecord"][0]["EndOfRoutineFailureAnalysisDate"]["value"]:
                print(f"{pid} - end_of_routine_failure_analysis_date: None")
            else:
                end_of_routine_failure_analysis_date_string = data["EOXRecord"][0][
                    "EndOfRoutineFailureAnalysisDate"
                ]["value"]
                end_of_routine_failure_analysis_date = datetime.strptime(
                    end_of_routine_failure_analysis_date_string, "%Y-%m-%d"
                ).date()
                print(f"{pid} - end_of_routine_failure_analysis_date: {end_of_routine_failure_analysis_date}")

                # Update end_of_routine_failure_analysis_date if the value has changed
                if dts.end_of_routine_failure_analysis_date != end_of_routine_failure_analysis_date:
                    dts.end_of_routine_failure_analysis_date = end_of_routine_failure_analysis_date
                    value_changed = True

        # Do nothing when JSON field does not exist
        except KeyError:
            print(f"{pid} - end_of_routine_failure_analysis_date: None")

        #### Get end_of_service_contract_renewal ############################################################
        try:
            if not data["EOXRecord"][0]["EndOfServiceContractRenewal"]["value"]:
                print(f"{pid} - end_of_service_contract_renewal: None")
            else:
                end_of_service_contract_renewal_string = data["EOXRecord"][0]["EndOfServiceContractRenewal"][
                    "value"
                ]
                end_of_service_contract_renewal = datetime.strptime(
                    end_of_service_contract_renewal_string, "%Y-%m-%d"
                ).date()
                print(f"{pid} - end_of_service_contract_renewal: {end_of_service_contract_renewal}")

                # Update end_of_service_contract_renewal if the value has changed
                if dts.end_of_service_contract_renewal != end_of_service_contract_renewal:
                    dts.end_of_service_contract_renewal = end_of_service_contract_renewal
                    value_changed = True

        # Do nothing when JSON field does not exist
        except KeyError:
            print(f"{pid} - end_of_service_contract_renewal: None")

        #### Get last_date_of_support #######################################################################
        try:
            if not data["EOXRecord"][0]["LastDateOfSupport"]["value"]:
                print(f"{pid} - last_date_of_support: None")
            else:
                last_date_of_support_string = data["EOXRecord"][0]["LastDateOfSupport"]["value"]
                last_date_of_support = datetime.strptime(last_date_of_support_string, "%Y-%m-%d").date()
                print(f"{pid} - last_date_of_support: {last_date_of_support}")

                # Update last_date_of_support if the value has changed
                if dts.last_date_of_support != last_date_of_support:
                    dts.last_date_of_support = last_date_of_support
                    value_changed = True

        # Do nothing when JSON field does not exist
        except KeyError:
            print(f"{pid} - last_date_of_support: None")

        #### Get end_of_svc_attach_date #####################################################################
        try:
            if not data["EOXRecord"][0]["EndOfSvcAttachDate"]["value"]:
                print(f"{pid} - end_of_svc_attach_date: None")
            else:
                end_of_svc_attach_date_string = data["EOXRecord"][0]["EndOfSvcAttachDate"]["value"]
                end_of_svc_attach_date = datetime.strptime(end_of_svc_attach_date_string, "%Y-%m-%d").date()
                print(f"{pid} - end_of_svc_attach_date: {end_of_svc_attach_date}")

                # Update end_of_svc_attach_date if value has changed
                if dts.end_of_svc_attach_date != end_of_svc_attach_date:
                    dts.end_of_svc_attach_date = end_of_svc_attach_date
                    value_changed = True

        # Do nothing when JSON field does not exist
        except KeyError:
            print(f"{pid} - end_of_svc_attach_date: None")

        #### Save model object for device type ##############################################################
        if value_changed:
            dts.save()

        return False if eox_has_error else True

    def get_device_types(self, manufacturer):
        task = "Get Manufacturer"
        print(self.task_name(text=task))

        # trying to get the right manufacturer for this plugin
        try:
            m = Manufacturer.objects.get(name=manufacturer)
            print(self.task_info(text=task, changed=False))
            print(f"Found manufacturer {m}")

        except Manufacturer.DoesNotExist:
            print(self.task_error(text=task, changed=False))
            print(f"Manufacturer {manufacturer} does not exist")
            return False

        # trying to get all device types and it's base PIDs associated with this manufacturer
        try:
            dt = DeviceType.objects.filter(manufacturer=m)

        except DeviceType.DoesNotExist:
            print(self.task_error(text=task, changed=False))
            print(f"Manufacturer {manufacturer} - No Device Types")
            return False

        return dt

    def get_product_ids(self, manufacturer):
        product_ids = []
        failed = False

        # Get all device types for supplied manufacturer
        dt = self.get_device_types(manufacturer)

        print(self.task_name(text="Get PIDs"))

        # Iterate all this device types
        for device_type in dt:
            # Skip if the device type has no valid part number.
            # Part numbers must match the exact Cisco Base PID
            if not device_type.part_number:
                print(self.task_error(text=f"Get PID for {device_type}", changed=False))
                print(f"Found device type {device_type} WITHOUT PID - SKIPPING")
                failed = True
                continue

            # Found Part number, append it to the list (PID collection for EoX data done)
            print(self.task_info(text=f"Get PID for {device_type}", changed=False))
            print(f"Found device type {device_type} with PID {device_type.part_number}")

            product_ids.append(device_type.part_number)

        return product_ids, failed

    def get_serial_numbers(self, manufacturer):
        serial_numbers = []
        failed = False

        # Get all device types for supplied manufacturer
        dt = self.get_device_types(manufacturer)

        print(self.task_name(text="Get Serial Numbers"))

        # Iterate all this device types
        for device_type in dt:
            # trying to get all devices and its serial numbers for this device type (for contract data)
            try:
                d = Device.objects.filter(device_type=device_type)

                for device in d:
                    # Skip if the device role is "3rd-Party"
                    if device.role.slug == "3rd-party":
                        print(self.task_info(text=f"Get serial number for {device}", changed=False))
                        print(f"Found device {device} with role '3rd-Party' - SKIPPING")
                        continue
                    # Skip if the device has not status "Active"
                    if device.status != DeviceStatusChoices.STATUS_ACTIVE:
                        print(self.task_info(text=f"Get serial number for {device}", changed=False))
                        print(f"Found device {device} WITHOUT status Active - SKIPPING")
                        continue
                    # Skip if the device is active (from prev. if) and has no valid serial number.
                    if not device.serial:
                        print(self.task_error(text=f"Get serial number for {device}", changed=False))
                        print(f"Found device {device} WITHOUT serial number - SKIPPING")
                        failed = True
                        continue
                    # Else the device is active and has valid serial number
                    if device.serial and device.status == DeviceStatusChoices.STATUS_ACTIVE:
                        print(self.task_info(text=f"Get serial number for {device}", changed=False))
                        print(f"Found device {device} with serial number {device.serial}")
                        serial_numbers.append(device.serial)

            except Device.DoesNotExist:
                print(self.task_error(text=f"Get serial number for {dt}", changed=False))
                print(f"Device with device type {dt} does not exist")
                failed = True

        return serial_numbers, failed

    def logon(self):
        PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("netbox_device_support_plugin", dict())
        CISCO_CLIENT_ID = PLUGIN_SETTINGS.get("CISCO_SUPPORT_API_CLIENT_ID", "")
        CISCO_CLIENT_SECRET = PLUGIN_SETTINGS.get("CISCO_SUPPORT_API_CLIENT_SECRET", "")
        # Set the requests timeout for connect and read separatly
        self.REQUESTS_TIMEOUT = (3.05, 27)

        token_url = "https://id.cisco.com/oauth2/default/v1/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": CISCO_CLIENT_ID,
            "client_secret": CISCO_CLIENT_SECRET,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        access_token_response = requests.post(
            url=token_url, params=params, headers=headers, verify=False, timeout=self.REQUESTS_TIMEOUT
        )
        token = access_token_response.json()["access_token"]
        api_call_headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}

        return api_call_headers

    # Main entry point for the sync_cisco_support command of manage.py
    def handle(self, *args, **kwargs):
        SYNC_FAILED = False
        PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("netbox_device_support_plugin", dict())
        MANUFACTURER = PLUGIN_SETTINGS.get("CISCO_MANUFACTURER", "Cisco")

        # Logon one time and gather the required API key
        api_call_headers = self.logon()

        base_url = "https://apix.cisco.com"

        #### Step 1: Prepare all PIDs and serial numbers ####################################################
        print(self.task_title(title="Prepare PIDs"))
        product_ids, failed = self.get_product_ids(MANUFACTURER)
        if failed:
            SYNC_FAILED = True

        print(self.task_title(title="Prepare serial numbers"))
        serial_numbers, failed = self.get_serial_numbers(MANUFACTURER)
        if failed:
            SYNC_FAILED = True

        #### Step 2: Get EoX Data for all PIDs ##############################################################
        print(self.task_title(title="Update Device Type Support Information"))
        print(self.task_name(text="Get EoX Data for PIDs"))

        for pid in product_ids:
            # Get the Cisco Support API data
            url = f"{base_url}/supporttools/eox/rest/5/EOXByProductID/1/{pid}?responseencoding=json"
            response, data = self.get_cisco_support_api_data(url=url, header=api_call_headers)

            # Check if JSON contains EOXError
            if "EOXError" in data["EOXRecord"][0]:
                # Error SSA_ERR_021_Pid (Incorrect PID) can be wrong and therefor a second API call is made
                # with a wildcard search for the PID
                if (
                    "SSA_ERR_021_Pid" in data["EOXRecord"][0]["EOXError"]["ErrorID"]
                    or "Incorrect PID" in data["EOXRecord"][0]["EOXError"]["ErrorDescription"]
                ):
                    # Get the Cisco Support API data with a wildcard search for the PID
                    url = f"{base_url}/supporttools/eox/rest/5/EOXByProductID/1/*{pid}*?responseencoding=json"
                    response, data = self.get_cisco_support_api_data(url=url, header=api_call_headers)

            # Validate the data dict
            if data:
                # Call our Device Type Update method for that particular PID
                if not self.update_device_type_eox_data(pid, data):
                    SYNC_FAILED = True
            else:
                # Show an error
                SYNC_FAILED = True
                print(self.task_error(text=f"Get data for PID {pid}", changed=False))
                print(f"API Response: {response}")
                print(f"API Response Text: {response.text}")

        #### Step 3: Get SNI owner status for all serial numbers ############################################
        print(self.task_title(title="Update Device Support Information"))
        print(self.task_name(text="Get SNI Owner Status"))

        serial_numbers_copy = serial_numbers.copy()
        while serial_numbers_copy:
            # Pop the first items_to_fetch items of serial_numbers_copy into current_slice and then delete
            # them from serial numbers. We want to pass x items to the API each time we call it
            items_to_fetch = 50
            current_slice = serial_numbers_copy[:items_to_fetch]
            serial_numbers_copy[:items_to_fetch] = []

            # Get the Cisco Support API data
            url = f"{base_url}/sn2info/v2/coverage/owner_status/serial_numbers/{','.join(current_slice)}"
            response, data = self.get_cisco_support_api_data(url=url, header=api_call_headers)

            # Validate the data dict
            if data:
                # Iterate through all serial numbers included in the API response
                for device in data["serial_numbers"]:
                    # Call our Device Update method for that particular Device
                    if not self.update_device_sni_status_data(device):
                        SYNC_FAILED = True
            else:
                # Show an error
                SYNC_FAILED = True
                print(self.task_error(text=f"Get data for serial number", changed=False))
                print(f"API Response: {response}")
                print(f"API Response Text: {response.text}")
                print(f"Serial Numbers: {data['serial_numbers']}")

        #### Step 4: Get SNI summary for all serial numbers #################################################
        print(self.task_name(text="Get SNI Summary"))

        # Dict to store the serial number and pid as key-value pair to use later for the recommended release
        serial_pid = {}

        serial_numbers_copy = serial_numbers.copy()
        while serial_numbers_copy:
            # Pop the first items_to_fetch items of serial_numbers_copy into current_slice and then delete them from serial
            # numbers. We want to pass x items to the API each time we call it
            items_to_fetch = 50
            current_slice = serial_numbers_copy[:items_to_fetch]
            serial_numbers_copy[:items_to_fetch] = []

            # Get the Cisco Support API data
            url = f"{base_url}/sn2info/v2/coverage/summary/serial_numbers/{','.join(current_slice)}"
            response, data = self.get_cisco_support_api_data(url=url, header=api_call_headers)

            # Validate the data dict
            if data:
                # Iterate through all serial numbers included in the API response
                for device in data["serial_numbers"]:
                    # Create a dict with the serial and the product ids of all devices as key-value pairs
                    serial_pid[device["sr_no"]] = self.find_base_pid(device)
                    # Call our Device Update method for that particular Device
                    if not self.update_device_sni_summary_data(device):
                        SYNC_FAILED = True
            else:
                # Show an error
                SYNC_FAILED = True
                print(self.task_error(text=f"Get data for serial number", changed=False))
                print(f"API Response: {response}")
                print(f"API Response Text: {response.text}")
                print(f"Serial Numbers: {data['serial_numbers']}")

        #### Step 5: Get the recommended software release for all serial numbers ############################
        print(self.task_title(title="Update Device and Device Type Software Information"))
        print(self.task_name(text="Get Recommended Software Release for PIDs"))

        for serial_number, pid in serial_pid.items():
            # If pid is an empty string
            if not pid:
                SYNC_FAILED = True
                text = f"Get data for serial number {serial_number}"
                print(self.task_error(text=text, changed=False))
                print(f"{serial_number} - No PID found for this serial number")
                continue

            # Normalize the PID list to match the base_pid of the API specs
            # Find PIDs which don't have a Cisco software
            prefixes = ["UCSC", "AIR-AP"]
            suffixes = ["AXI", "AXI-E", "AXE", "AXE-E"]
            if pid.startswith(tuple(prefixes)) or pid.endswith(tuple(suffixes)):
                data = "PID without Cisco software"
                # Call our Device Type Update method for that particular PID
                self.update_device_ss_data(serial_number, pid, data)
                continue

            # Call the release suggestions
            url = f"{base_url}/software/suggestion/v2/suggestions/releases/productIds/{pid}"
            response, data = self.get_cisco_support_api_data(url=url, header=api_call_headers)

            # Validate the data dict
            if data:
                # Call our Device Type Update method for that particular PID
                if not self.update_device_ss_data(serial_number, pid, data):
                    SYNC_FAILED = True
            else:
                # Show an error
                SYNC_FAILED = True
                print(self.task_error(text=f"Get data for PID {pid}", changed=False))
                print(f"API Response: {response}")
                print(f"API Response Text: {response.text}")

        #### Step 6: Print the sync statuc summary ##########################################################
        task = "Sync Cisco Support API Data Result"
        print(self.task_name(text=task))

        if SYNC_FAILED:
            print(self.task_error(text=task, changed=False))
            print(f"\U0001f4a5 {task.upper()} FAILED \U0001f4a5")
            print(f"{Style.BRIGHT}{Fore.RED}-> Analyse the output for failed results")
            print("\n")
            sys.exit(1)
        else:
            print(self.task_info(text=task, changed=False))
            print(f"\u2728 {task.upper()} SUCCESSFUL \u2728")
            print("\n")
