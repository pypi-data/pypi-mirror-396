# python3-cyberfusion-rblchecker

Use rblchecker to check whether your outgoing mail IP addresses are listed on RBLs.

The following checkers are supported:

* DNS
* * Every host in the config is checked.
* Microsoft SNDS
* * Not only blacklisted IPs, but also IPs with a 'special' status are returned. See 'IP status' on https://sendersupport.olc.protection.outlook.com/snds/FAQ.aspx

# Install

## PyPI

Run the following command to install the package from PyPI:

    pip3 install rblchecker

## Debian

Run the following commands to build a Debian package:

    mk-build-deps -i -t 'apt -o Debug::pkgProblemResolver=yes --no-install-recommends -y'
    dpkg-buildpackage -us -uc


# Configure

Find an example config in `config.yml`.

# Usage

Run all checkers:

    rblchecker --config-path=...

Example output:

```
(DNS) IP address 198.51.100.100 is listed on access.redhawk.org (100.100.51.198.access.redhawk.org -> 127.0.0.0)
(SNDS) IP address 198.51.100.100 is listed on SNDS (reason: 'Junked due to user complaints or other evidence of spamming')
```

If there's any listings, the command exits with a non-zero RC.
