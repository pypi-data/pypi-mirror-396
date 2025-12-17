# python3-cyberfusion-external-providers-ip-ranges

Scripts to add IP ranges of external providers to [ferm](http://ferm.foo-projects.org/) variables.

## Supported providers

* Google Cloud
* Atlassian
* [Buddy](https://buddy.works/)

# Install

## PyPI

Run the following command to install the package from PyPI:

    pip3 install python3-cyberfusion-external-providers-ip-ranges

## Debian

Run the following commands to build a Debian package:

    mk-build-deps -i -t 'apt -o Debug::pkgProblemResolver=yes --no-install-recommends -y'
    dpkg-buildpackage -us -uc

# Configure

No configuration is supported.

# Usage

Run the following command for help:

    external-providers-ip-ranges-cli -h

## Cron

The Debian package installs a cron. This cron runs the command above per supported provider.
