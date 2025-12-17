"""JSON database functions."""

import json
from typing import Dict, Optional, Tuple

from cyberfusion.SecurityTXTPolicyServer import settings
from cyberfusion.SecurityTXTPolicyServer.exceptions.database import DomainNotExistsError
from cyberfusion.SecurityTXTPolicyServer.utilities import (
    CHAR_LABEL,
    SecurityTXTPolicy,
    get_domain_is_wildcard,
)


class SecurityTXTPolicyInformation:
    """Represents security.txt policy information."""

    def __init__(self, security_txt_policy: SecurityTXTPolicy, text: str) -> None:
        """Set attributes."""
        self.email_contacts = security_txt_policy.email_contacts
        self.url_contacts = security_txt_policy.url_contacts
        self.expires_timestamp = security_txt_policy.expires_timestamp
        self.encryption_key_urls = security_txt_policy.encryption_key_urls
        self.acknowledgment_urls = security_txt_policy.acknowledgment_urls
        self.preferred_languages = security_txt_policy.preferred_languages
        self.policy_urls = security_txt_policy.policy_urls
        self.opening_urls = security_txt_policy.opening_urls
        self.domains = security_txt_policy.domains
        self.text = text


class Database:
    """Represents JSON database."""

    def __init__(self) -> None:
        """Initialise database."""
        self.load()

    def load(self) -> None:
        """Load security.txt policies from database.

        Turns JSON objects into Python objects.
        """
        self.security_txt_policies: Dict[str, Tuple[SecurityTXTPolicy, str]] = {}

        # Load security.txt policies from file

        with open(settings.DATABASE_PATH, "r") as f:
            _contents = json.loads(f.read())

        # Add SecurityTXTPolicy objects

        for _security_txt_policy in _contents["security_txt_policies"]:
            security_txt_policy = SecurityTXTPolicy(**_security_txt_policy)
            text = str(security_txt_policy)

            for domain in security_txt_policy.domains:
                domain = domain.lower()  # Should be case-insensitive

                self.security_txt_policies[domain] = (
                    security_txt_policy,
                    text,
                )

    def _get_security_txt_policy_by_literal_domain(
        self, domain: str
    ) -> Optional[Tuple[SecurityTXTPolicy, str]]:
        """Get security.txt policies from database by literal domain."""
        try:
            return self.security_txt_policies[domain]
        except KeyError:
            # Not in database

            return None

    def _get_security_txt_policy_by_wildcard_domain(
        self, domain: str
    ) -> Optional[Tuple[SecurityTXTPolicy, str]]:
        """Get security.txt policy from database by wildcard domain."""
        for _domain, security_txt_policy in self.security_txt_policies.items():
            # This can't match if the _domain is not a wildcard

            if not get_domain_is_wildcard(_domain):
                continue

            # When we get here, we know '_domain[1:]' is '*'. If we remove both
            # first parts, and they are the same, domain is covered by the
            # wildcard _domain

            if domain.split(CHAR_LABEL)[1:] != _domain.split(CHAR_LABEL)[1:]:
                continue

            return security_txt_policy

        return None

    def get_security_txt_policy_information(
        self, domain: str
    ) -> SecurityTXTPolicyInformation:
        """Get security.txt policy information for domain.

        There are two cases in which a domain can be matched to a security.txt policy:

        - When a security.txt policy for the literal domain exists (preferred).
        - When a security.txt policy for a wildcard domain exists.
        """

        # Get security.txt policy by literal domain (prefer over wildcard)

        _security_txt_policy_by_literal_domain = (
            self._get_security_txt_policy_by_literal_domain(domain)
        )

        if _security_txt_policy_by_literal_domain:
            security_txt_policy, text = _security_txt_policy_by_literal_domain

            return SecurityTXTPolicyInformation(security_txt_policy, text)

        # Get security.txt policy by wildcard domain

        _security_txt_policy_by_wildcard_domain = (
            self._get_security_txt_policy_by_wildcard_domain(domain)
        )

        if _security_txt_policy_by_wildcard_domain:
            security_txt_policy, text = _security_txt_policy_by_wildcard_domain

            return SecurityTXTPolicyInformation(security_txt_policy, text)

        # At this point, there is no match for either a literal domain or
        # wildcard domain

        raise DomainNotExistsError
