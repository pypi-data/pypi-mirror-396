"""Custom Starlette endpoints."""

from typing import Union

from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse

from cyberfusion.SecurityTXTPolicyServer import settings


class SecurityTXTPolicy(HTTPEndpoint):
    """security.txt policy endpoint."""

    async def get(self, request: Request) -> Union[PlainTextResponse, JSONResponse]:
        """Implement GET method."""
        if request.state.security_txt_policy_error:
            return JSONResponse(
                {"detail": request.state.security_txt_policy_error.detail},
                status_code=request.state.security_txt_policy_error.status_code,
            )

        return PlainTextResponse(
            request.state.security_txt_policy_information.text,
            headers={"X-Powered-By": settings.APP_NAME},
        )
