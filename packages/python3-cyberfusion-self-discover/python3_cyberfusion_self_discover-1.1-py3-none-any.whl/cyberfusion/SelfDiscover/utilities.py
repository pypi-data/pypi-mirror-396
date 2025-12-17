"""Utilities."""

import xml.etree.ElementTree as ET

from fastapi import Request

from cyberfusion.SelfDiscover.exceptions import MissingHostError


def get_host_from_request(request: Request) -> str:
    """Get host (HTTP header) from Starlette request object.

    Use this function when the host must be set, as it raises an exception if not.
    """
    host = request.url.hostname

    if not host:
        raise MissingHostError

    return host


def get_pox_autodiscover_response(
    imap_server_hostname: str,
    pop3_server_hostname: str,
    smtp_server_hostname: str,
    login_name: str,
) -> str:
    """Get POX ('plain old XML') autodiscover response.

    See: https://learn.microsoft.com/en-us/exchange/client-developer/web-service-reference/pox-autodiscover-response-for-exchange
    """
    root = ET.Element(
        "Autodiscover",
        xmlns="http://schemas.microsoft.com/exchange/autodiscover/responseschema/2006",
    )

    Response = ET.SubElement(
        root,
        "Response",
        xmlns="http://schemas.microsoft.com/exchange/autodiscover/outlook/responseschema/2006a",
    )

    Account = ET.SubElement(Response, "Account")
    ET.SubElement(Account, "AccountType").text = "email"
    ET.SubElement(Account, "Action").text = "settings"

    Protocol = ET.SubElement(Account, "Protocol")
    ET.SubElement(Protocol, "Type").text = "IMAP"
    ET.SubElement(Protocol, "Server").text = imap_server_hostname
    ET.SubElement(Protocol, "Port").text = "993"
    ET.SubElement(Protocol, "DomainRequired").text = "off"
    ET.SubElement(Protocol, "LoginName").text = login_name
    ET.SubElement(Protocol, "SPA").text = "off"
    ET.SubElement(Protocol, "SSL").text = "on"
    ET.SubElement(Protocol, "AuthRequired").text = "on"

    Protocol = ET.SubElement(Account, "Protocol")
    ET.SubElement(Protocol, "Type").text = "POP3"
    ET.SubElement(Protocol, "Server").text = pop3_server_hostname
    ET.SubElement(Protocol, "Port").text = "995"
    ET.SubElement(Protocol, "DomainRequired").text = "off"
    ET.SubElement(Protocol, "LoginName").text = login_name
    ET.SubElement(Protocol, "SPA").text = "off"
    ET.SubElement(Protocol, "SSL").text = "on"
    ET.SubElement(Protocol, "AuthRequired").text = "on"

    Protocol = ET.SubElement(Account, "Protocol")
    ET.SubElement(Protocol, "Type").text = "SMTP"
    ET.SubElement(Protocol, "Server").text = smtp_server_hostname
    ET.SubElement(Protocol, "Port").text = "587"
    ET.SubElement(Protocol, "DomainRequired").text = "off"
    ET.SubElement(Protocol, "LoginName").text = login_name
    ET.SubElement(Protocol, "SPA").text = "off"
    ET.SubElement(Protocol, "Encryption").text = "TLS"
    ET.SubElement(Protocol, "AuthRequired").text = "on"
    ET.SubElement(Protocol, "UsePOPAuth").text = "off"
    ET.SubElement(Protocol, "SMTPLast").text = "off"

    tree = ET.ElementTree(root)
    ET.indent(tree, space="    ", level=0)

    return ET.tostring(root, encoding="unicode", xml_declaration=True) + "\n"


def get_thunderbird_autoconfig_response(
    imap_server_hostname: str,
    pop3_server_hostname: str,
    smtp_server_hostname: str,
    login_name: str,
    domain: str,
) -> str:
    """Get Thunderbird autoconfig response."""
    root = ET.Element("clientConfig", version="1.1")

    emailProvider = ET.SubElement(root, "emailProvider", id=domain)
    ET.SubElement(emailProvider, "domain").text = domain
    ET.SubElement(emailProvider, "displayName").text = "%EMAILADDRESS%"

    incomingServer = ET.SubElement(emailProvider, "incomingServer", type="imap")
    ET.SubElement(incomingServer, "hostname").text = imap_server_hostname
    ET.SubElement(incomingServer, "port").text = "993"
    ET.SubElement(incomingServer, "socketType").text = "SSL"
    ET.SubElement(incomingServer, "username").text = "%EMAILADDRESS%"
    ET.SubElement(incomingServer, "authentication").text = "password-cleartext"

    outgoingServer = ET.SubElement(emailProvider, "outgoingServer", type="smtp")
    ET.SubElement(outgoingServer, "hostname").text = smtp_server_hostname
    ET.SubElement(outgoingServer, "port").text = "587"
    ET.SubElement(outgoingServer, "socketType").text = "STARTTLS"
    ET.SubElement(outgoingServer, "username").text = "%EMAILADDRESS%"
    ET.SubElement(outgoingServer, "authentication").text = "password-cleartext"

    tree = ET.ElementTree(root)
    ET.indent(tree, space="    ", level=0)

    return ET.tostring(root, encoding="unicode", xml_declaration=True) + "\n"
