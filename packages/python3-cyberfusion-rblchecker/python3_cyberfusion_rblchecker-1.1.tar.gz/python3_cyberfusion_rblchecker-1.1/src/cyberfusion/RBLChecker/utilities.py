"""Utilities."""

import ipaddress
from ipaddress import IPv4Address, IPv6Address
from typing import List, Union

from netaddr import iter_iprange


def get_ip_addresses_in_range(start_range: str, end_range: str) -> List[str]:
    """Get IP addresses in range."""
    return [
        str(ip_address) for ip_address in iter_iprange(start_range, end_range, step=1)
    ]


def get_ip_addresses_in_ip_network(
    ip_network: str,
) -> List[Union[IPv4Address, IPv6Address]]:
    """Get IP addresses in IP network."""
    return list(ipaddress.ip_network(ip_network).hosts())


def get_address_family(ip_address: Union[IPv6Address, IPv4Address]) -> int:
    """Get IP address family."""
    return ip_address.version


def reverse_ip_address(ip_address: Union[IPv6Address, IPv4Address]) -> str:
    """Reverse IP address."""
    if get_address_family(ip_address) == 6:
        return _reverse_ipv6_address(str(ip_address))

    return _reverse_ipv4_address(str(ip_address))


def _reverse_ipv4_address(ipv4_address: str) -> str:
    """Reverse IPv4 address."""
    list_ = ipv4_address.split(".")

    list_.reverse()

    return ".".join(list_)


def _reverse_ipv6_address(ipv6_address: str) -> str:
    """Reverse IPv6 address."""

    # 2001:0db8:: -> 2001:0db8:0000:0000:0000:0000:0000:0000
    exploded = IPv6Address(ipv6_address).exploded

    # -> 20010db8000000000000000000000000
    without_colons = exploded.replace(":", "")

    # -> 0000000000000000000000008bd01002
    reversed_ = without_colons[::-1]

    # -> 0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2
    with_dots = ".".join(reversed_)

    return with_dots
