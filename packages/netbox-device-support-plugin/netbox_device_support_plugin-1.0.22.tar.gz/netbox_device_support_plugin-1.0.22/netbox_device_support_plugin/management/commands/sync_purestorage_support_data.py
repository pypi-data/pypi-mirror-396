import sys
import time
import requests
from colorama import Fore, Style, init
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import MultipleObjectsReturned
from typing import Generator, Union
from datetime import datetime
from requests import api
from dcim.models import Manufacturer
from dcim.models import Device, DeviceType
from netbox_device_support_plugin.models import FortinetDeviceSupport

init(autoreset=True, strip=False)


class Command(BaseCommand):
    help = "Sync local devices with the Pure Storage Pure1 API"

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            "--manufacturer",
            action="store_true",
            default="Fortinet",
            help="Manufacturer name (default: Pure Storage)",
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
                    # Skip if the device has no valid serial number.
                    if not device.serial:
                        print(self.task_error(text=f"Get serial number for {device}", changed=False))
                        print(f"Found device {device} WITHOUT serial number - SKIPPING")
                        failed = True
                        continue

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
        CISCO_CLIENT_ID = PLUGIN_SETTINGS.get("PURESTORAGE_SUPPORT_API_CLIENT_ID", "")
        CISCO_CLIENT_SECRET = PLUGIN_SETTINGS.get("PURESTORAGE_SUPPORT_API_CLIENT_SECRET", "")
        # Set the requests timeout for connect and read separatly
        self.REQUESTS_TIMEOUT = (3.05, 27)

        """
        token_url = "https://customerapiauth.fortinet.com/api/v1/oauth/token/"

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
        """

        return None

    # Main entry point for the sync_cisco_support command of manage.py
    def handle(self, *args, **kwargs):
        SYNC_FAILED = False
        PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("netbox_device_support_plugin", dict())
        MANUFACTURER = PLUGIN_SETTINGS.get("PURESTORAGE_MANUFACTURER", "Pure Storage")

        #### Step 1: Prepare all PIDs and serial numbers ####################################################
        print(self.task_title(title="Prepare PIDs"))
        product_ids, failed = self.get_product_ids(MANUFACTURER)
        if failed:
            SYNC_FAILED = True

        print(self.task_title(title="Prepare serial numbers"))
        serial_numbers, failed = self.get_serial_numbers(MANUFACTURER)
        if failed:
            SYNC_FAILED = True

        #### Step X: Print the sync statuc summary ##########################################################
        task = "Sync Pure Storage Pure1 API Data Result"
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
