"""API methods for interacting with Zoho Projects."""

from typing import TYPE_CHECKING, List

from ..models.project_models import Project

if TYPE_CHECKING:
    from ..http_client import ApiClient


class ProjectsAPI:
    """Helpers for Zoho Projects endpoints."""

    def __init__(self, client: "ApiClient"):
        self._client = client

    @property
    def _portal_id(self) -> str:
        portal_id = self._client.portal_id
        if portal_id is None:
            raise ValueError("Portal ID is not configured on the API client")
        return portal_id

    async def get_all(self, page: int = 1, per_page: int = 20) -> List[Project]:
        """
        Fetches all projects with pagination support.

        Args:
            page: The page number to retrieve (starting from 1)
            per_page: The number of records per page (default 20, max usually 100)
        """
        endpoint = f"/portal/{self._portal_id}/projects"

        params = {"page": page, "per_page": per_page}

        response_data = await self._client.get(endpoint, params=params)

        # Handle both list and dict response formats
        if isinstance(response_data, list):
            projects_data = response_data
        else:
            projects_data = response_data.get("projects", [])

        return [Project.model_validate(p) for p in projects_data]

    async def get(self, project_id: int) -> Project:
        """
        Fetches a single project by its ID.
        """
        endpoint = f"/portal/{self._portal_id}/projects/{project_id}"

        response_data = await self._client.get(endpoint)
        # The API returns a list even for a single project fetch
        if isinstance(response_data, list):
            projects_list = response_data
        else:
            projects_list = response_data.get("projects", [])
        if projects_list:
            return Project.model_validate(projects_list[0])
        # Return an empty Project instance when no project is found
        return Project.model_construct(id=0, name="", status="active")

    async def create(self, project_data: Project) -> Project:
        """
        Creates a new project.
        """
        endpoint = f"/portal/{self._portal_id}/projects"

        response_data = await self._client.post(
            endpoint, json=project_data.model_dump(by_alias=True, exclude_none=True)
        )
        project_data = response_data.get("project", {})

        return Project.model_validate(project_data)

    async def update(self, project_id: int, project_data: Project) -> Project:
        """
        Updates an existing project.
        """
        endpoint = f"/portal/{self._portal_id}/projects/{project_id}"

        response_data = await self._client.patch(
            endpoint, json=project_data.model_dump(by_alias=True, exclude_none=True)
        )
        project_data = response_data.get("project", {})

        return Project.model_validate(project_data)

    async def delete(self, project_id: int) -> bool:
        """
        Deletes a project by its ID.
        """
        endpoint = f"/portal/{self._portal_id}/projects/{project_id}"

        await self._client.delete(endpoint)
        return True
