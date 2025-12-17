# python3-cyberfusion-self-discover

self-discover serves autodiscover (Outlook) and autoconfig (Thunderbird) XML files for mail auto-configuration.

# Install

## PyPI

Run the following command to install the package from PyPI:

    pip3 install python3-cyberfusion-self-discover

## Debian

Run the following commands to build a Debian package:

    mk-build-deps -i -t 'apt -o Debug::pkgProblemResolver=yes --no-install-recommends -y'
    dpkg-buildpackage -us -uc

# Configure

Pass the following environment variables:

* `IMAP_SERVER_HOSTNAME`
* `POP3_SERVER_HOSTNAME`
* `SMTP_SERVER_HOSTNAME`

# Usage

## Manually

Run the app using an ASGI server such as Uvicorn.

### systemd

    systemctl start self-discover.service
