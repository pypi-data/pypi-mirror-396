"""rblchecker.

Usage:
   rblchecker --config-path=<config-path>

Options:
  -h --help                                 Show this screen.
  --config-path=<config-path>               Path to config file.
"""

import sys

import docopt
from schema import Schema

from cyberfusion.RBLChecker import checkers
from cyberfusion.RBLChecker.config import get_config
from cyberfusion.RBLChecker.utilities import get_ip_addresses_in_ip_network


def get_args() -> docopt.Dict:
    """Get docopt args."""
    return docopt.docopt(__doc__)


def main() -> None:
    """Spawn relevant class for CLI function."""
    exit_code = 0

    # Validate input

    args = get_args()
    schema = Schema(
        {
            "--config-path": str,
        }
    )
    args = schema.validate(args)

    # Run checkers

    config = get_config(args["--config-path"])

    for ip_network in config["ip_networks"]:
        ip_addresses = get_ip_addresses_in_ip_network(ip_network)

        for ip_address in ip_addresses:
            # Check DNS

            for host in config["checkers"]["dns"]["hosts"]:
                listed, query_name, query_result = checkers.DNSChecker(
                    ip_address, host
                ).check()

                if listed:
                    exit_code = 1

                    print(
                        f"(DNS) IP address {ip_address} is listed on {host} ({query_name} -> {query_result})"
                    )

            # Check SNDS

            listed, reason = checkers.SNDSChecker(
                ip_address, config["checkers"]["snds"]["key"]
            ).check()

            if listed:
                exit_code = 1

                print(
                    f"(SNDS) IP address {ip_address} is listed on SNDS (reason: '{reason}')"
                )

    sys.exit(exit_code)
