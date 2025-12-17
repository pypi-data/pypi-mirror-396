"""Custom Starlette middleware."""

from typing import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from cyberfusion.SecurityTXTPolicyServer.exceptions.database import DatabaseError
from cyberfusion.SecurityTXTPolicyServer.exceptions.http_host_header import (
    HTTPHostHeaderError,
)
from cyberfusion.SecurityTXTPolicyServer.utilities import parse_host_header


class InjectSecurityTXTPolicyMiddleware(BaseHTTPMiddleware):
    """Middleware to add security.txt policy to request."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Add security.txt policy information to request."""

        # Parse domain from host header (= 'request.url.hostname')

        parsed_domain = None

        try:
            parsed_domain = parse_host_header(request.url.hostname)
        except HTTPHostHeaderError as e:
            request.state.security_txt_policy_error = e
            request.state.security_txt_policy_information = None

        # If the domain is parsed, get security.txt policy from database

        if parsed_domain:
            try:
                request.state.security_txt_policy_information = (
                    request.app.state.database.get_security_txt_policy_information(
                        parsed_domain
                    )
                )

                request.state.security_txt_policy_error = None
            except DatabaseError as e:
                request.state.security_txt_policy_error = e
                request.state.security_txt_policy_information = None

        response = await call_next(request)

        return response
