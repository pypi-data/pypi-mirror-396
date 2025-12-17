"""
HTTP client for Slotix API.
"""
import os
from typing import Any, Optional
import httpx


class SlotixClient:
    """HTTP client for communicating with Slotix API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None
    ):
        self.api_key = api_key or os.environ.get("SLOTIX_API_KEY")
        self.api_url = (api_url or os.environ.get("SLOTIX_API_URL", "https://api.slotix.it")).rstrip("/")

        if not self.api_key:
            raise ValueError(
                "API key is required. Set SLOTIX_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self._client = httpx.AsyncClient(
            base_url=f"{self.api_url}/v1/mcp",
            headers={
                "X-API-Key": self.api_key,
                "Content-Type": "application/json",
            },
            timeout=30.0
        )

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        json: Optional[dict] = None
    ) -> dict[str, Any]:
        """Make an HTTP request to the Slotix API."""
        response = await self._client.request(
            method=method,
            url=path,
            params=params,
            json=json
        )

        if response.status_code == 401:
            raise ValueError("Invalid API key. Please check your SLOTIX_API_KEY.")

        if response.status_code == 403:
            raise ValueError("Access forbidden. Your account may be inactive.")

        if response.status_code == 404:
            raise ValueError(f"Resource not found: {path}")

        if response.status_code >= 400:
            try:
                error = response.json()
                detail = error.get("detail", str(error))
            except Exception:
                detail = response.text
            raise ValueError(f"API error ({response.status_code}): {detail}")

        if response.status_code == 204:
            return {"success": True}

        return response.json()

    # Profile
    async def get_profile(self) -> dict:
        """Get professional profile."""
        return await self._request("GET", "/profile")

    # Appointments
    async def get_appointments(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        status: Optional[str] = None
    ) -> dict:
        """Get appointments."""
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if status:
            params["status"] = status
        return await self._request("GET", "/appointments", params=params)

    async def get_today_appointments(self) -> dict:
        """Get today's appointments."""
        return await self._request("GET", "/appointments/today")

    async def get_week_appointments(self) -> dict:
        """Get this week's appointments."""
        return await self._request("GET", "/appointments/week")

    async def get_appointment(self, appointment_id: int) -> dict:
        """Get a specific appointment."""
        return await self._request("GET", f"/appointments/{appointment_id}")

    async def create_appointment(
        self,
        client_name: str,
        start_datetime: str,
        duration_minutes: int = 30,
        client_contact: Optional[str] = None,
        client_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> dict:
        """Create a new appointment."""
        data = {
            "client_name": client_name,
            "start_datetime": start_datetime,
            "duration_minutes": duration_minutes,
        }
        if client_contact:
            data["client_contact"] = client_contact
        if client_id:
            data["client_id"] = client_id
        if notes:
            data["notes"] = notes
        return await self._request("POST", "/appointments", json=data)

    async def update_appointment(
        self,
        appointment_id: int,
        start_datetime: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        status: Optional[str] = None,
        notes: Optional[str] = None
    ) -> dict:
        """Update an appointment."""
        data = {}
        if start_datetime:
            data["start_datetime"] = start_datetime
        if duration_minutes:
            data["duration_minutes"] = duration_minutes
        if status:
            data["status"] = status
        if notes is not None:
            data["notes"] = notes
        return await self._request("PUT", f"/appointments/{appointment_id}", json=data)

    async def cancel_appointment(self, appointment_id: int) -> dict:
        """Cancel an appointment."""
        return await self._request("DELETE", f"/appointments/{appointment_id}")

    # Clients
    async def get_clients(
        self,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> dict:
        """Get clients."""
        params = {"limit": limit, "offset": offset}
        if search:
            params["search"] = search
        return await self._request("GET", "/clients", params=params)

    async def get_client(self, client_id: int) -> dict:
        """Get a specific client."""
        return await self._request("GET", f"/clients/{client_id}")

    # Availability
    async def get_availability(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> list:
        """Get available slots."""
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return await self._request("GET", "/availability", params=params)

    # Stats
    async def get_stats(self, period: str = "month") -> dict:
        """Get business statistics."""
        return await self._request("GET", "/stats", params={"period": period})

    # Notifications
    async def send_notification(
        self,
        client_id: int,
        message: str,
        channel: str = "auto"
    ) -> dict:
        """Send a notification to a client."""
        return await self._request(
            "POST",
            "/notifications/send",
            json={
                "client_id": client_id,
                "message": message,
                "channel": channel
            }
        )
