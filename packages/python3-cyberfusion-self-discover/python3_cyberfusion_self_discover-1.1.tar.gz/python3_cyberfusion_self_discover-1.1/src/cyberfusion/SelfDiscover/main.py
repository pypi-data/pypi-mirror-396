"""App."""

import defusedxml.ElementTree as SafeET
from fastapi import FastAPI, Query, Request, Response, status

from cyberfusion.SelfDiscover.settings import settings
from cyberfusion.SelfDiscover.utilities import (
    get_host_from_request,
    get_pox_autodiscover_response,
    get_thunderbird_autoconfig_response,
)

app = FastAPI()

PREFIX_AUTODISCOVER = "autodiscover"
PREFIX_AUTOCONFIG = "autoconfig"


@app.post("/autodiscover/autodiscover.xml")  # type: ignore[untyped-decorator]
async def pox_autodiscover(request: Request) -> Response:
    """Get POX ('plain old XML') autodiscover response."""
    if get_host_from_request(request).split(".")[0] != PREFIX_AUTODISCOVER:
        return Response(
            content=f"URL must start with '{PREFIX_AUTODISCOVER}'",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    body = await request.body()

    try:
        parsed_body = SafeET.fromstring(body)
    except SafeET.ParseError:
        return Response(
            content="Payload must be valid XML",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # 'xmlns' includes http or https. Example with https on #1, with http on #2.
    #
    # 1: https://learn.microsoft.com/en-us/exchange/client-developer/web-service-reference/pox-autodiscover-request-for-exchange
    # 2: https://learn.microsoft.com/en-us/openspecs/exchange_server_protocols/ms-oxdscli/fc420a31-5180-4a28-8397-8db8977861c6

    email_address = parsed_body.find(
        ".//{http://schemas.microsoft.com/exchange/autodiscover/outlook/requestschema/2006}EMailAddress"
    )

    if email_address is None:
        email_address = parsed_body.find(
            ".//{https://schemas.microsoft.com/exchange/autodiscover/outlook/requestschema/2006}EMailAddress"
        )

    if email_address is None:
        return Response(
            content="Email address must be present in XML payload",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    data = get_pox_autodiscover_response(
        settings.IMAP_SERVER_HOSTNAME,
        settings.POP3_SERVER_HOSTNAME,
        settings.SMTP_SERVER_HOSTNAME,
        email_address.text,
    )

    return Response(content=data, media_type="application/xml")


@app.get("/mail/config-v1.1.xml")  # type: ignore[untyped-decorator]
async def thunderbird_autoconfig(
    request: Request,
    email_address: str = Query(alias="emailaddress"),  # noqa: B008
) -> Response:
    """Get Thunderbird autoconfig response."""
    if get_host_from_request(request).split(".")[0] != PREFIX_AUTOCONFIG:
        return Response(
            content=f"URL must start with '{PREFIX_AUTOCONFIG}'",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    hostname_without_autoconfig = get_host_from_request(request).split(".")
    hostname_without_autoconfig.remove(
        PREFIX_AUTOCONFIG
    )  # Due to the check above, we know that this is the first element

    data = get_thunderbird_autoconfig_response(
        settings.IMAP_SERVER_HOSTNAME,
        settings.POP3_SERVER_HOSTNAME,
        settings.SMTP_SERVER_HOSTNAME,
        email_address,
        ".".join(hostname_without_autoconfig),
    )

    return Response(content=data, media_type="application/xml")
