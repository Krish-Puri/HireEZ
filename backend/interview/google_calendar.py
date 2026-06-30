"""
Google Calendar Service

Creates calendar events with Google Meet links for interviews.
"""

import datetime
import uuid
from typing import Optional

import httpx

from backend.config import config


class GoogleCalendarService:

    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token
        self.base_url = "https://www.googleapis.com/calendar/v3"
        self.client_id = config.GOOGLE_CLIENT_ID
        self.client_secret = config.GOOGLE_CLIENT_SECRET

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    async def create_meet_link(self) -> str:
        """
        Create a Google Meet link.
        If access_token is configured, uses Google Calendar API for a real link.
        Otherwise, generates a valid-format placeholder ID (demo mode).
        """
        if not self.access_token or self.access_token in ("your-client-id.apps.googleusercontent.com", ""):
            # Dev/demo mode — generate a valid Google Meet ID format
            # Google Meet IDs: 3 segments of 4-9 lowercase alphanumeric chars
            import random, string
            chars = string.ascii_lowercase + string.digits
            seg = lambda: ''.join(random.choices(chars, k=random.randint(8, 10)))
            meet_id = f"{seg()}-{seg()}-{seg()}"
            return f"https://meet.google.com/{meet_id}"

        # Create a minimal calendar event with conferenceData to generate a Meet link
        event = {
            "summary": "HireEZ Interview",
            "conferenceData": {
                "createRequest": {
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                    "requestId": uuid.uuid4().hex,
                }
            },
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/calendars/primary/events",
                headers=self._headers(),
                json=event,
                params={"conferenceDataVersion": "1"},
            )

        if response.status_code == 200:
            data = response.json()
            return data.get("hangoutLink", data.get("conferenceData", {}).get("entryPoints", [{}])[0].get("uri", ""))
        else:
            raise Exception(f"Failed to create Meet link: {response.text}")

    async def create_interview_event(
        self,
        candidate_email: str,
        candidate_name: str,
        job_title: Optional[str],
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        meet_link: Optional[str] = None,
    ) -> dict:
        """
        Create a calendar event for the interview.
        If meet_link is not provided, creates one automatically.
        Returns the event details including meet_link.
        """
        if not meet_link:
            meet_link = await self.create_meet_link()

        event = {
            "summary": f"Interview: {candidate_name} — {job_title or 'Position'}",
            "description": f"Candidate: {candidate_name}\nEmail: {candidate_email}\n\nScheduled via HireEZ",
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "UTC",
            },
            "attendees": [
                {"email": candidate_email},
            ],
            "conferenceData": {
                "createRequest": {
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                    "requestId": uuid.uuid4().hex,
                }
            } if not meet_link or "meet.google.com" in meet_link else {},
        }

        if self.access_token:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/calendars/primary/events",
                    headers=self._headers(),
                    json=event,
                    params={"conferenceDataVersion": "1"},
                )
            if response.status_code != 200:
                raise Exception(f"Failed to create calendar event: {response.text}")
            data = response.json()
            return {
                "meet_link": data.get("hangoutLink", meet_link),
                "event_id": data.get("id"),
                "start": data.get("start", {}).get("dateTime"),
                "end": data.get("end", {}).get("dateTime"),
            }

        # Dev mode
        return {
            "meet_link": meet_link,
            "event_id": uuid.uuid4().hex,
            "start": start_time.isoformat(),
            "end": end_time.isoformat(),
        }


google_calendar_service = GoogleCalendarService()
