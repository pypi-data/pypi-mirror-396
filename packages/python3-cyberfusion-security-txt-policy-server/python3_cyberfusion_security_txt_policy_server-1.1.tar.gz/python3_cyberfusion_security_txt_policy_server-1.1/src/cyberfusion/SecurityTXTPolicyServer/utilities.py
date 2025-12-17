"""Generic HTTP and URL utilities."""

import datetime
from dataclasses import dataclass
from typing import List, Optional

import validators

from cyberfusion.SecurityTXTPolicyServer.exceptions.http_host_header import (
    HTTPHostHeaderDomainEmptyError,
    HTTPHostHeaderDomainInvalidError,
)

CHAR_PREFIX_WILDCARD = "*"
CHAR_LABEL = "."


@dataclass
class SecurityTXTPolicy:
    """Represents security.txt policy."""

    url_contacts: List[str]
    email_contacts: List[str]
    expires_timestamp: int
    encryption_key_urls: List[str]
    acknowledgment_urls: List[str]
    preferred_languages: List[str]
    policy_urls: List[str]
    opening_urls: List[str]
    domains: List[str]

    def __str__(self) -> str:
        """Get string representation of .well-known/security.txt file."""
        lines = []

        for url_contact in self.url_contacts:
            lines.append(f"Contact: {url_contact}")

        for email_contact in self.email_contacts:
            lines.append(f"Contact: mailto:{email_contact}")

        lines.append(
            f"Expires: {datetime.datetime.fromtimestamp(self.expires_timestamp, tz=datetime.timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')}"
        )

        for encryption_key_url in self.encryption_key_urls:
            lines.append(f"Encryption: {encryption_key_url}")

        for acknowledgment_url in self.acknowledgment_urls:
            lines.append(f"Acknowledgments: {acknowledgment_url}")

        lines.append(f"Preferred-Languages: {', '.join(self.preferred_languages)}")

        for policy_url in self.policy_urls:
            lines.append(f"Policy: {policy_url}")

        for opening_url in self.opening_urls:
            lines.append(f"Hiring: {opening_url}")

        return "\n".join(lines) + "\n"


def get_domain_is_wildcard(domain: str) -> bool:
    """Determine if domain is wildcard."""
    return domain.split(CHAR_LABEL)[0] == CHAR_PREFIX_WILDCARD


def parse_host_header(value: Optional[str]) -> str:
    """Parse HTTP host header."""

    # If host is empty, we can't do anything security.txt policy wise. A missing
    # host header should be handled by the server, e.g. by h11._util.RemoteProtocolError

    if not value:
        raise HTTPHostHeaderDomainEmptyError

    # The part before ':' is the host. The ':' may be absent, in which case this
    # split won't do anything

    domain = value.split(":")[0]

    # The host doesn't necessarily have to be a valid domain. This is just here
    # as a failsafe.

    if not validators.domain(domain):
        raise HTTPHostHeaderDomainInvalidError

    # Ensure domain is lowercase

    domain = domain.lower()

    return domain
