import logging
from bw_essentials.constants.services import Services
from bw_essentials.services.api_client import ApiClient


logger = logging.getLogger(__name__)


class Compliance(ApiClient):
    """
    Compliance service integration class.

    This class facilitates communication with the compliance service.
    """

    def __init__(self, user, tenant_id: str = None):
        """
        Initialize the Compliance service wrapper.

        :param user: The user initiating the request.
        """
        super().__init__(user)
        self.base_url = self.get_base_url(Services.COMPLIANCE.value)
        self.name = Services.COMPLIANCE.value
        self.tenant_id = tenant_id
        self.urls = {
            "kra_data": "kra/data"
        }
        logger.info("Compliance service initialized.")

    def _headers(self):
        """
        Construct headers for compliance service requests.

        :return: Dictionary of headers.
        """
        return {
            'Content-Type': 'application/json',
            **({'X-Tenant-ID': self.tenant_id} if self.tenant_id else {})
        }

    def get_kra_data(self, payload):
        """
        Fetches KRA details by calling API.

        This method prepares the request headers, constructs the API endpoint,
        sends a POST request with the provided payload, and returns the
        parsed KRA data received from the compliance service.


        Args:
            payload (dict):
                Dictionary containing the required fields for KRA lookup.
                Example:
                    {
                        "pan": "ABCDE1234F",
                        "dob": "1985-05-12"
                    }

        Returns:
            dict:
                Parsed KRA data dictionary returned by the Compliance Service.
                Returns an empty dictionary if `data` is missing from the response.

                Example:
                    {
                        "kra_status": "KYC_REGISTERED",
                        "name": "John Doe",
                        "dob": "1985-05-12",
                        ...
                    }
        """
        logger.info(f"In get_kra_data {payload =}")
        url = f"{self.base_url}"
        self.headers = self._headers()
        kra_data = self._post(url=url, endpoint=self.urls.get('kra_data'), json=payload)
        logger.info(f"Out get_kra_data {kra_data =}")
        return kra_data.get('data', {})