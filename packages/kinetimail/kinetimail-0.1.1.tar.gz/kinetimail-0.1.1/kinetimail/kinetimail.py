import requests

class KinetiMailError(Exception):
    """Exception for KinetiMail errors."""
    pass

class KinetiMailConfigError(KinetiMailError):
    """Exception for KinetiMail configuration errors."""
    pass

class KinetiMailAPIError(KinetiMailError):
    """Exception for KinetiMail API errors."""
    def __init__(self, message, response=None):
        super().__init__(message)
        self.response = response
        self.status_code = getattr(response, 'status_code', None)
        self.error_message = message

class KinetiMail:

    def __init__(self, api_key: str, base_url: str = "https://api.kinetimail.com"):
        if not api_key or len(api_key) < 10:
            raise KinetiMailConfigError("API key must be at least 10 characters long.")
        if not (isinstance(base_url, str) and base_url.startswith("https://") and len(base_url) > len("https://")):
            raise KinetiMailConfigError("base_url must be a valid https URL.")
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
        except requests.RequestException as e:
            raise KinetiMailError(f"Request failed: {e}")

        if not (200 <= response.status_code < 300):
            try:
                error_data = response.json()
                error_message = error_data.get("message") or error_data.get("error") or str(error_data)
            except Exception:
                error_message = response.text
            raise KinetiMailAPIError(f"API Error {response.status_code}: {error_message}", response=response)

        try:
            return response.json()
        except Exception as e:
            raise KinetiMailError(f"Failed to parse JSON response: {e}")

    def get_message(self, inbox_id: str, message_id: str) -> dict:
        """Retrieve a specific message by ID in an inbox."""
        return self._request("GET", f"/inboxes/{inbox_id}/messages/{message_id}")

    def list_messages(self, inbox_id: str, page: int = None, limit: int = None, unread_only: bool = None) -> dict:
        """List messages in the specified inbox. Supports pagination and unread filter."""
        params = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if unread_only is not None:
            params["unread_only"] = str(unread_only).lower()
        return self._request("GET", f"/inboxes/{inbox_id}/messages", params=params if params else None)

    def send_message(self, from_address: str, to_address: str, subject: str, body: str) -> dict:
        """Send a message from the specified inbox."""
        payload = {
            "from": from_address,
            "to": to_address,
            "subject": subject,
            "body": body
        }
        return self._request("POST", f"/inboxes/{from_address}/messages", json=payload)

    def create_inbox(self, email: str, name: str, description: str = None) -> dict:
        """Create a new inbox. 'email' is used as inbox_id."""
        payload = {"email": email, "name": name}
        if description:
            payload["description"] = description
        return self._request("POST", "/inboxes", json=payload)
    
    def get_inbox(self, inbox_id: str) -> dict:
        """Retrieve a specific inbox by ID."""
        return self._request("GET", f"/inboxes/{inbox_id}")
    
    def list_inboxes(self, page: int = None, limit: int = None) -> dict:
        """List all inboxes. Supports optional pagination."""
        params = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        return self._request("GET", "/inboxes", params=params if params else None)

