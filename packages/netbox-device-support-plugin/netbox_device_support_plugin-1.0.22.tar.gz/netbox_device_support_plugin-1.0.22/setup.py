#!/usr/bin/env python3
"""Build the netbox-cisco-maintenance Python Package with setuptools"""

import codecs
import os.path
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setup(
    name="netbox-device-support-plugin",
    version=get_version("netbox_device_support_plugin/version.py"),
    author="Willi Kubny",
    author_email="willi.kubny@gmail.com",
    description="Cisco device support, device type support, and software release information with the Cisco support APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
    ],
    license="MIT",
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
