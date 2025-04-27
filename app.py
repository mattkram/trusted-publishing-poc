from typing import Any, Optional

import httpx
from jose import jwt

from fastapi import FastAPI, Header, HTTPException, status

OIDC_CONFIG_URL = (
    "https://token.actions.githubusercontent.com/.well-known/openid-configuration"
)

# The workflow submitting a token request must match these parameters.
# In a real scenario, these would be configured by the user and stored
# in the database.
ALLOWED_REPO = "mattkram/trusted-publishing-poc"
ALLOWED_BRANCH = "refs/heads/main"
ALLOWED_WORKFLOW = "publish-good.yaml"

app = FastAPI()


@app.get("/")
async def home() -> dict:
    return {"hello": "world"}


async def get_jwks() -> dict[str, Any]:
    """Return the JWKs available via the OIDC configuration."""
    async with httpx.AsyncClient() as client:
        # First, we load the OpenID configuration
        response = await client.get(OIDC_CONFIG_URL)
        openid_config = response.json()

        # Then, we load the JWKs, via the URI embedded in the OpenID configuration
        jwks_uri = openid_config["jwks_uri"]
        response = await client.get(jwks_uri)
        return response.json()


def get_key_for_token(kid: str, jwks: dict[str, Any]) -> dict[str, Any]:
    """Get the specific key based on the `kid` (key ID) field."""
    for key in jwks["keys"]:
        if key["kid"] == kid:
            return key

    raise ValueError(f"Key with ID {kid} not found in JWKs")


async def decode_token(token: str) -> dict[str, Any] | None:
    """Validate the JWT token against the public keys (JWKs)."""
    # Load the JWKs and find the public key referenced in the token
    jwks = await get_jwks()
    headers = jwt.get_unverified_header(token)
    kid = headers.get("kid")
    algorithm = headers.get("alg", ["RS256"])
    key = get_key_for_token(kid, jwks)

    # Attempt to decode the token by validating against the public key
    # We don't verify the audience, since that is user-specific
    try:
        return jwt.decode(token, key, algorithms=algorithm)
    except Exception as e:
        print(f"Token validation failed: {e}")
        return None


async def grant_access_token(id_token: str) -> str:
    """Grant a new access token, if the ID token provided matches the specification."""
    data = await decode_token(id_token)

    if data is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid ID token",
        )

    subject = data.get("sub", "")
    if subject != f"repo:{ALLOWED_REPO}:ref:{ALLOWED_BRANCH}":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid repository",
        )

    workflow_ref = data.get("workflow_ref", "")
    if (
        workflow_ref
        != f"{ALLOWED_REPO}/.github/workflows/{ALLOWED_WORKFLOW}@{ALLOWED_BRANCH}"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid workflow",
        )

    return "super-secret-token"


@app.get("/token")
async def get_token(
    authorization: Optional[str] = Header(default=None),
) -> dict:
    """Retrieve a new "access token" if the submitting workflow is trusted."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Must provide a valid id token",
        )

    _, id_token = authorization.split()
    access_token = await grant_access_token(id_token)
    return {"access_token": access_token}
