import requests

from typing import Dict, Any
from ..utils import ApiRequestHandler


class WebhookService:
    """Webhook service implementation."""

    def __init__(self, api_domain: str, token: str, verify_ssl: bool = True):
        """Initialize the conversation service.

        Args:
            api_domain: Base URL for the API
            token: Authentication token
            verify_ssl: Whether to verify SSL certificates
        """
        self._api = ApiRequestHandler(api_domain, token, verify_ssl)

    def trigger(
        self, webhook_id: str, data: Dict[str, Any] = None
    ) -> requests.Response:
        """Trigger a webhook by sending a POST request with the provided data.

        Args:
            webhook_id: Webhook ID to trigger
            data: Request body data. Defaults to {"test": "data"} if not provided

        Returns:
            Response object from requests library
        """
        if data is None:
            data = {"test": "data"}

        return self._api.post(
            f"/v1/webhooks/{webhook_id}",
            response_model=requests.Response,
            json_data=data,
            wrap_response=False,
            raise_on_error=False,
        )
