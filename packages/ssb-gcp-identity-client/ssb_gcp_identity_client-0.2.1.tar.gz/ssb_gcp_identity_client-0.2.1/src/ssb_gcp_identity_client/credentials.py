from typing import Any

from google.auth import identity_pool
from google.auth.transport.requests import Request

STS_TOKEN_URL = "https://sts.googleapis.com/v1/token"
SUBJECT_TOKEN_TYPE_JWT = "urn:ietf:params:oauth:token-type:jwt"
AUDIENCE_TEMPLATE = "//iam.googleapis.com/projects/{project_number}/locations/global/workloadIdentityPools/{pool_id}/providers/{provider_id}"
DEFAULT_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]


class _StaticTokenSupplier(identity_pool.SubjectTokenSupplier):
    """Internal class for providing a static Maskinporten-token to identity_pool.Credentials."""

    def __init__(self, token: str) -> None:
        self.token = token

    def get_subject_token(self, _context: Any, _request: Any) -> str:
        return self.token


def get_federated_credentials(
    project_number: str,
    workload_identity_pool_id: str,
    provider_id: str,
    maskinporten_token: str,
) -> identity_pool.Credentials:
    """Creates Workload Identity Federation credentials using a Maskinporten token.

    These credentials can be used to authenticate to Google Cloud services
    from environments outside Google Cloud (e.g., on-premise or other clouds)
    via Workload Identity Federation.

    Args:
        project_number: The numeric ID of the Google Cloud project which contains the Workload Identity Pool.
        workload_identity_pool_id: The Workload Identity Pool ID.
        provider_id: The Workload Identity Pool Provider ID.
        maskinporten_token: String containing a Maskinporten JWT.

    Returns:
        `identity_pool.Credentials`: Federated credentials which can be used to create Google Cloud clients.

    Raises:
        google.auth.exceptions.RefreshError: If the token exchange fails due to authentication or configuration issues.

    Example:
        .. code-block:: python

            from google.cloud import storage
            from ssb_gcp_identity_client import get_federated_credentials

            creds = get_federated_credentials(
                project_number="1234567890",
                workload_identity_pool_id="my-pool",
                provider_id="maskinporten-provider",
                maskinporten_token=token_as_string
            )

            # Create a GCS client using these credentials
            client = storage.Client(credentials=creds)

            # List buckets in the project
            for bucket in client.list_buckets():
                print(bucket.name)
    """
    token_supplier = _StaticTokenSupplier(maskinporten_token)

    audience = AUDIENCE_TEMPLATE.format(
        project_number=project_number,
        pool_id=workload_identity_pool_id,
        provider_id=provider_id,
    )

    creds = identity_pool.Credentials(  # type: ignore[no-untyped-call]
        audience=audience,
        subject_token_type=SUBJECT_TOKEN_TYPE_JWT,
        token_url=STS_TOKEN_URL,
        subject_token_supplier=token_supplier,
        scopes=DEFAULT_SCOPES,
    )

    # This will call the STS token exchange. It raises RefreshError on failure.
    creds.refresh(Request())  # type: ignore[no-untyped-call]

    return creds
