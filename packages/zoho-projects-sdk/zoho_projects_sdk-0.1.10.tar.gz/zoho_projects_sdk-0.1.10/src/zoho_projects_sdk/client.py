"""
The main, user-facing client for interacting with the Zoho Projects API.
"""

from types import TracebackType
from typing import Optional, Type

from .api import (
    AttachmentsAPI,
    BaselinesAPI,
    BusinessHoursAPI,
    ClientsAPI,
    CommentsAPI,
    ContactsAPI,
    EventsAPI,
    IssuesAPI,
    MilestonesAPI,
    PhasesAPI,
    PortalsAPI,
    ProjectsAPI,
    RolesAPI,
    TagsAPI,
    TasklistsAPI,
    TasksAPI,
    TimelogsAPI,
    UsersAPI,
)
from .auth import ZohoOAuth2Handler
from .http_client import ApiClient


class ZohoProjects:
    """
    The primary, user-facing entry point for the Zoho Projects SDK.

    This class handles the initialization of the authentication session and
    provides access to the various API resource modules.
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        refresh_token: Optional[str] = None,
        portal_id: Optional[str] = None,
    ):
        """
        Initializes the ZohoProjects client.

        Args:
            client_id: The OAuth2 client ID.
            client_secret: The OAuth2 client secret.
            refresh_token: The OAuth2 refresh token.
            portal_id: The ID of the Zoho Projects portal.
        """
        self._auth_handler = ZohoOAuth2Handler(
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            portal_id=portal_id,
        )
        self._api_client = ApiClient(auth_handler=self._auth_handler)

    @property
    def projects(self) -> ProjectsAPI:
        """Access the Projects API."""
        return ProjectsAPI(self._api_client)

    @property
    def portals(self) -> PortalsAPI:
        """Access the Portals API."""
        return PortalsAPI(self._api_client)

    @property
    def tasks(self) -> TasksAPI:
        """Access the Tasks API."""
        return TasksAPI(self._api_client)

    @property
    def tasklists(self) -> TasklistsAPI:
        """Access the Tasklists API."""
        return TasklistsAPI(self._api_client)

    @property
    def issues(self) -> IssuesAPI:
        """Access the Issues API."""
        return IssuesAPI(self._api_client)

    @property
    def users(self) -> UsersAPI:
        """Access the Users API."""
        return UsersAPI(self._api_client)

    @property
    def timelogs(self) -> TimelogsAPI:
        """Access the Timelogs API."""
        return TimelogsAPI(self._api_client)

    @property
    def comments(self) -> CommentsAPI:
        """Access the Comments API."""
        return CommentsAPI(self._api_client)

    @property
    def events(self) -> EventsAPI:
        """Access the Events API."""
        return EventsAPI(self._api_client)

    @property
    def milestones(self) -> MilestonesAPI:
        """Access the Milestones API."""
        return MilestonesAPI(self._api_client)

    @property
    def phases(self) -> PhasesAPI:
        """Access the Phases API."""
        return PhasesAPI(self._api_client)

    @property
    def business_hours(self) -> BusinessHoursAPI:
        """Access the Business Hours API."""
        return BusinessHoursAPI(self._api_client)

    @property
    def baselines(self) -> BaselinesAPI:
        """Access the Baselines API."""
        return BaselinesAPI(self._api_client)

    @property
    def attachments(self) -> AttachmentsAPI:
        """Access the Attachments API."""
        return AttachmentsAPI(self._api_client)

    @property
    def tags(self) -> TagsAPI:
        """Access the Tags API."""
        return TagsAPI(self._api_client)

    @property
    def clients(self) -> ClientsAPI:
        """Access the Clients API."""
        return ClientsAPI(self._api_client)

    @property
    def contacts(self) -> ContactsAPI:
        """Access the Contacts API."""
        return ContactsAPI(self._api_client)

    @property
    def roles(self) -> RolesAPI:
        """Access the Roles API."""
        return RolesAPI(self._api_client)

    async def __aenter__(self) -> "ZohoProjects":
        """Enables usage as an async context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        """Closes the underlying session when exiting an async context."""
        await self.close()

    async def close(self) -> None:
        """Closes the underlying HTTP client session."""
        if self._api_client:
            await self._api_client.close()
