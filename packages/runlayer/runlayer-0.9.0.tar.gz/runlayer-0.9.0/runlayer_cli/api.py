import datetime
from typing import Any

import httpx
from pydantic import BaseModel
import typer

from runlayer_cli.models import (
    ServerDetails,
    LocalCapabilities,
    PreRequest,
    PostRequest,
)

USER_AGENT = "Runlayer CLI"
API_KEY_HEADER_NAME = "x-runlayer-api-key"


class DeploymentPublic(BaseModel):
    """Public deployment model matching backend schema."""

    id: str
    name: str
    configuration: dict[str, Any]
    deployment_outputs: dict[str, Any] | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    template_yaml: str | None = None  # Always present for new deployments
    deletion_status: str | None = None  # "deleted", "deleting", or None (active)
    connected_servers: list[dict[str, Any]] = []  # List of connected MCP servers


class ValidateYAMLResponse(BaseModel):
    """Response from YAML validation endpoint."""

    valid: bool
    error: str | None = None
    parsed_config: dict[str, Any] | None = None


class ECRCredentials(BaseModel):
    """ECR credentials response."""

    username: str
    password: str
    registry_url: str
    repository_url: str
    expires_at: datetime.datetime


class DeploymentTriggerResponse(BaseModel):
    """Deployment trigger response."""

    deployment_id: str
    request_id: str
    status: str
    history_id: str


class RunlayerClient:
    def __init__(self, hostname: str, secret: str):
        self.headers = {
            "User-Agent": USER_AGENT,
            API_KEY_HEADER_NAME: secret,
        }
        self.base_url = hostname

    def _handle_deployment_response(self, response: httpx.Response) -> None:
        """
        Handle deployment API response and provide user-friendly error messages.

        Args:
            response: HTTP response from deployment endpoint

        Raises:
            typer.Exit: If deployment feature is not available (404)
            httpx.HTTPStatusError: For other HTTP errors
        """
        if response.status_code == 404:
            try:
                error_data = response.json()
                if "Deployment feature not available" in error_data.get("detail", ""):
                    typer.secho(
                        "\n✗ Deployment feature is not enabled on this Runlayer instance.",
                        fg=typer.colors.RED,
                        bold=True,
                        err=True,
                    )
                    typer.echo(
                        "Please contact your administrator to enable deployment support.",
                        err=True,
                    )
                    raise typer.Exit(1)
            except (ValueError, KeyError):
                pass

        response.raise_for_status()

    def get_server_details(self, server_id: str) -> ServerDetails:
        with httpx.Client(headers=self.headers) as client:
            response = client.get(f"{self.base_url}/api/v1/local/{server_id}")
            response.raise_for_status()
            return ServerDetails.model_validate(response.json())

    def update_capabilities(self, server_id: str, capabilities: LocalCapabilities):
        with httpx.Client(headers=self.headers) as client:
            response = client.post(
                f"{self.base_url}/api/v1/local/{server_id}/capabilities",
                json=capabilities.model_dump(mode="json"),
            )
            return response

    def pre(self, server_id: str, request: PreRequest) -> httpx.Response:
        with httpx.Client(headers=self.headers) as client:
            response = client.post(
                f"{self.base_url}/api/v1/local/{server_id}/pre",
                json=request.model_dump(),
            )
            return response

    def post(self, server_id: str, request: PostRequest) -> httpx.Response:
        with httpx.Client(headers=self.headers) as client:
            response = client.post(
                f"{self.base_url}/api/v1/local/{server_id}/post",
                json=request.model_dump(),
            )
            return response

    def get_deployment(self, deployment_id: str) -> DeploymentPublic:
        """Get a deployment by ID."""
        with httpx.Client(headers=self.headers) as client:
            response = client.get(
                f"{self.base_url}/api/v1/deployments/{deployment_id}",
            )
            self._handle_deployment_response(response)
            return DeploymentPublic.model_validate(response.json())

    def create_deployment(self, name: str) -> DeploymentPublic:
        """
        Create a new deployment with just a name.

        The backend always generates and returns a default template YAML.

        Args:
            name: Deployment name

        Returns:
            DeploymentPublic with template_yaml field
        """
        with httpx.Client(headers=self.headers) as client:
            response = client.post(
                f"{self.base_url}/api/v1/deployments/",
                json={"name": name},
            )
            self._handle_deployment_response(response)
            return DeploymentPublic.model_validate(response.json())

    def update_deployment(
        self,
        deployment_id: str,
        configuration: dict[str, Any] | None = None,
        yaml_content: str | None = None,
        docker_image: str | None = None,
    ) -> DeploymentPublic:
        """
        Update deployment configuration.

        Args:
            deployment_id: UUID of deployment
            configuration: Legacy configuration dict (deprecated, use yaml_content)
            yaml_content: Raw YAML string to send to backend for validation
            docker_image: Docker image URI (passed separately, not in YAML)

        Returns:
            Updated deployment

        Note: If yaml_content is provided, it takes precedence over configuration.
        """
        payload: dict[str, Any] = {}

        if configuration is not None:
            payload["configuration"] = configuration

        # Send yaml_content and docker_image in request body
        if yaml_content is not None:
            payload["yaml_content"] = yaml_content
        if docker_image is not None:
            payload["docker_image"] = docker_image

        with httpx.Client(headers=self.headers) as client:
            response = client.put(
                f"{self.base_url}/api/v1/deployments/{deployment_id}",
                json=payload,
            )
            self._handle_deployment_response(response)
            return DeploymentPublic.model_validate(response.json())

    def get_ecr_credentials(self) -> ECRCredentials:
        """Get temporary ECR credentials for pushing images."""
        with httpx.Client(headers=self.headers) as client:
            response = client.post(
                f"{self.base_url}/api/v1/deployments/ecr-credentials",
            )
            self._handle_deployment_response(response)
            return ECRCredentials.model_validate(response.json())

    def trigger_deployment(self, deployment_id: str) -> DeploymentTriggerResponse:
        """Trigger a deployment."""
        with httpx.Client(headers=self.headers) as client:
            response = client.post(
                f"{self.base_url}/api/v1/deployments/{deployment_id}/trigger",
            )
            self._handle_deployment_response(response)
            return DeploymentTriggerResponse.model_validate(response.json())

    def validate_yaml(self, yaml_content: str) -> ValidateYAMLResponse:
        """
        Validate YAML configuration without creating a deployment.

        This calls the backend validation endpoint to check the YAML structure.
        No local validation is performed - this is a pure pass-through to backend.

        Args:
            yaml_content: Raw YAML string to validate

        Returns:
            Validation result with any errors from backend
        """
        with httpx.Client(headers=self.headers) as client:
            response = client.post(
                f"{self.base_url}/api/v1/deployments/validate-yaml",
                json={"yaml_content": yaml_content},
            )
            self._handle_deployment_response(response)
            return ValidateYAMLResponse.model_validate(response.json())

    def get_deployment_status(self, deployment_id: str) -> dict[str, Any]:
        """Get deployment status."""
        with httpx.Client(headers=self.headers) as client:
            response = client.get(
                f"{self.base_url}/api/v1/deployments/{deployment_id}/status",
            )
            self._handle_deployment_response(response)
            return response.json()

    def get_deployment_logs(self, history_id: str) -> str | None:
        """
        Get deployment logs for a specific history entry.

        Args:
            history_id: UUID of the deployment history entry

        Returns:
            Logs string or None if no logs available
        """
        with httpx.Client(headers=self.headers) as client:
            response = client.get(
                f"{self.base_url}/api/v1/deployments/history/{history_id}/logs",
            )
            self._handle_deployment_response(response)
            data = response.json()
            return data.get("logs")

    def get_deployment_history(
        self, deployment_id: str, limit: int = 100
    ) -> dict[str, Any]:
        """
        Get deployment history for a deployment.

        Args:
            deployment_id: UUID of the deployment
            limit: Maximum number of history entries to return

        Returns:
            Dictionary with 'data' (list of history entries) and 'count'
        """
        with httpx.Client(headers=self.headers) as client:
            response = client.get(
                f"{self.base_url}/api/v1/deployments/{deployment_id}/history",
                params={"limit": limit},
            )
            self._handle_deployment_response(response)
            return response.json()

    def delete_deployment(self, deployment_id: str) -> None:
        """
        Delete a deployment and trigger infrastructure destruction.

        Args:
            deployment_id: UUID of the deployment to delete

        Raises:
            typer.Exit: If deployment feature is not available or deletion fails
            httpx.HTTPStatusError: For other HTTP errors
        """
        with httpx.Client(headers=self.headers) as client:
            response = client.delete(
                f"{self.base_url}/api/v1/deployments/{deployment_id}",
            )
            self._handle_deployment_response(response)

    def export_deployment_yaml(self, deployment_id: str) -> str:
        """
        Export deployment configuration as YAML string.

        Args:
            deployment_id: UUID of the deployment to export

        Returns:
            YAML configuration string

        Raises:
            typer.Exit: If deployment feature is not available or export fails
            httpx.HTTPStatusError: For other HTTP errors
            ValueError: If the response is missing or contains empty yaml_content
        """
        with httpx.Client(headers=self.headers) as client:
            response = client.get(
                f"{self.base_url}/api/v1/deployments/{deployment_id}/export-yaml",
            )
            self._handle_deployment_response(response)
            data = response.json()
            yaml_content = data.get("yaml_content", "")
            if not yaml_content or not yaml_content.strip():
                raise ValueError(
                    "Server returned empty YAML content. "
                    "This may indicate an API response issue or schema mismatch."
                )
            return yaml_content

    def submit_mcp_watch_scan(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Submit MCP Watch scan results to the backend.

        Args:
            payload: Scan payload with device info and configurations

        Returns:
            Response with scan_id, servers_processed, shadow_servers_found, etc.

        Raises:
            typer.Exit: If MCP Watch feature is not available (404)
            httpx.HTTPStatusError: If the request fails
        """
        with httpx.Client(headers=self.headers) as client:
            response = client.post(
                f"{self.base_url}/api/v1/mcp-watch/scan",
                json=payload,
            )

            # Handle 404 - endpoint doesn't exist in older versions
            if response.status_code == 404:
                typer.secho(
                    "\n✗ MCP Watch is not supported by this Runlayer server.",
                    fg=typer.colors.RED,
                    bold=True,
                    err=True,
                )
                typer.echo(
                    "Please upgrade to the latest version of Runlayer to use this feature.",
                    err=True,
                )
                raise typer.Exit(1)

            response.raise_for_status()
            return response.json()
