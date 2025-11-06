import ipaddress
import socket
from dataclasses import dataclass
from urllib.parse import urlparse

from app.clients.exa_client import (
    ExaClient,
    ExaClientNotConfiguredError,
    ExaClientError,
    get_exa_client,
)


class InvalidUrlError(Exception):
    pass


class ForbiddenUrlError(Exception):
    pass


class UrlContentFetchError(Exception):
    pass


class UrlIngestionConfigurationError(Exception):
    pass


@dataclass
class UrlIngestionResult:
    raw_content: str
    clean_content: str


def normalize_text(content: str) -> str:
    normalized = content.replace("\r\n", "\n").replace("\r", "\n").strip()
    return normalized


def validate_public_url(url: str) -> str:
    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        raise InvalidUrlError("URL must use http or https")

    if not parsed.hostname:
        raise InvalidUrlError("URL must include a hostname")

    if parsed.username or parsed.password:
        raise InvalidUrlError("URL credentials are not allowed")

    ensure_public_hostname(parsed.hostname)
    return parsed.geturl()


def ensure_public_hostname(hostname: str) -> None:
    if hostname.lower() == "localhost":
        raise ForbiddenUrlError("localhost is not allowed")

    direct_ip = parse_ip_address(hostname)
    if direct_ip is not None:
        ensure_public_ip(direct_ip)
        return

    try:
        address_infos = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise InvalidUrlError("Hostname could not be resolved") from exc

    resolved_ips: set[str] = set()
    for _, _, _, _, sockaddr in address_infos:
        host = sockaddr[0]
        if isinstance(host, str):
            resolved_ips.add(host)

    for value in resolved_ips:
        ensure_public_ip(ipaddress.ip_address(value))


def parse_ip_address(value: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    try:
        return ipaddress.ip_address(value)
    except ValueError:
        return None


# Reject non-public targets before calling Exa to reduce malicious page content impact.
def ensure_public_ip(address: ipaddress.IPv4Address | ipaddress.IPv6Address) -> None:
    if (
        address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_multicast
        or address.is_reserved
        or address.is_unspecified
    ):
        raise ForbiddenUrlError("URL resolves to a forbidden IP range")


def ingest_url_content(url: str, exa_client: ExaClient | None = None) -> UrlIngestionResult:
    safe_url = validate_public_url(url)
    client = exa_client or get_exa_client()

    try:
        raw_content = client.fetch_clean_text(safe_url)
    except ExaClientNotConfiguredError as exc:
        raise UrlIngestionConfigurationError("EXA_API_KEY is not configured") from exc
    except ExaClientError as exc:
        raise UrlContentFetchError("Could not fetch URL content from Exa") from exc

    clean_content = normalize_text(raw_content)
    if not clean_content:
        raise UrlContentFetchError("Fetched URL content is empty")

    return UrlIngestionResult(raw_content=raw_content, clean_content=clean_content)
