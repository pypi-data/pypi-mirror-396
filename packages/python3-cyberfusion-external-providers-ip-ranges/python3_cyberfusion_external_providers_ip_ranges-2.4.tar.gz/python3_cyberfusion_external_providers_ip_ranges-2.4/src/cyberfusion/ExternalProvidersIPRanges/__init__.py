"""Empty file to turn this into a package."""

import os
from abc import ABCMeta, abstractmethod
from typing import List

import requests

from cyberfusion.FermSupport.configuration import Configuration


def get_ferm_base_path() -> str:
    """Get ferm base path."""
    return os.path.join(
        os.path.sep,
        "etc",
        "ferm",
        "vars.d",
    )


class ExternalProviderIPRangeHandlerInterface(metaclass=ABCMeta):
    """Interface for external provider IP range handlers."""

    def __init__(  # noqa: B027
        self,
    ) -> None:
        """Do nothing."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Get external provider name."""

    @property
    @abstractmethod
    def ip_ranges(self) -> List[str]:
        """Get IP ranges."""


class AtlassianIPRangeHandler(ExternalProviderIPRangeHandlerInterface):
    """Class for external provider IP range handler."""

    @property
    def name(self) -> str:
        """Get external provider name."""
        return "atlassian"

    @property
    def ip_ranges(self) -> List[str]:
        """Get IP ranges."""
        result = []

        request = requests.get("https://ip-ranges.atlassian.com/")
        request.raise_for_status()
        data = request.json()

        for item in data["items"]:
            result.append(item["cidr"])

        return result


class AWSIPRangeHandler(ExternalProviderIPRangeHandlerInterface):
    """Class for external provider IP range handler."""

    @property
    def name(self) -> str:
        """Get external provider name."""
        return "aws"

    @property
    def ip_ranges(self) -> List[str]:
        """Get IP ranges."""
        result = []

        request = requests.get("https://ip-ranges.amazonaws.com/ip-ranges.json")
        request.raise_for_status()
        data = request.json()

        for item in data["prefixes"]:
            result.append(item["ip_prefix"])

        for item in data["ipv6_prefixes"]:
            result.append(item["ipv6_prefix"])

        return result


class GoogleCloudIPRangeHandler(ExternalProviderIPRangeHandlerInterface):
    """Class for external provider IP range handler."""

    @property
    def name(self) -> str:
        """Get external provider name."""
        return "google_cloud"

    @property
    def ip_ranges(self) -> List[str]:
        """Get IP ranges."""
        result = []

        request = requests.get("https://www.gstatic.com/ipranges/cloud.json")
        request.raise_for_status()
        data = request.json()

        for item in data["prefixes"]:
            if "ipv6Prefix" in item:
                result.append(item["ipv6Prefix"])
            else:
                result.append(item["ipv4Prefix"])

        return result


class BuddyIPRangeHandler(ExternalProviderIPRangeHandlerInterface):
    """Class for external provider IP range handler."""

    @property
    def name(self) -> str:
        """Get external provider name."""
        return "buddy"

    @property
    def ip_ranges(self) -> List[str]:
        """Get IP ranges."""
        result = []

        ip_ranges = []

        request = requests.get("https://buddy.works/api/ips")
        request.raise_for_status()
        ip_ranges.extend(request.json()["runners"])

        request = requests.get("https://buddy.works/api/ips/eu")
        request.raise_for_status()
        ip_ranges.extend(request.json()["runners"])

        for item in ip_ranges:
            result.append(item)

        return result


def main() -> None:
    """Spawn relevant class for CLI function."""
    configuration = Configuration(
        path=os.path.join(
            get_ferm_base_path(),
            "external-providers-ip-ranges.conf",
        )
    )

    handlers = [
        BuddyIPRangeHandler(),
        GoogleCloudIPRangeHandler(),
        AtlassianIPRangeHandler(),
        AWSIPRangeHandler(),
    ]

    for handler in handlers:
        configuration.add_variable(name=handler.name, values=handler.ip_ranges)

    configuration.save()
