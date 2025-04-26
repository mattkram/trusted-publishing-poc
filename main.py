from typing import Any, Optional

import httpx
from jose import jwt

from fastapi import FastAPI, Header, HTTPException, status

OIDC_CONFIG_URL = (
    "https://token.actions.githubusercontent.com/.well-known/openid-configuration"
)

app = FastAPI()


@app.get("/")
async def home() -> dict:
    return {"hello": "world"}


async def get_jwks():
    async with httpx.AsyncClient() as client:
        response = await client.get(OIDC_CONFIG_URL)
        openid_config = response.json()
        print(f"{openid_config=}")

        jwks_uri = openid_config["jwks_uri"]
        print(f"{jwks_uri=}")

        response = await client.get(jwks_uri)
        print(f"{response=}")

        token_keys = response.json()
        print(f"{token_keys=}")

        return token_keys


def get_key_for_token(kid: str, jwks: dict[str, Any]) -> dict[str, Any]:
    """Get the specific key based on the `kid` (key ID) field."""
    for key in jwks["keys"]:
        if key["kid"] == kid:
            return key

    raise ValueError(f"Key with ID {kid} not found in JWKs")


async def decode_token(token: str) -> dict[str, Any] | None:
    """Validate the JWT token against the public keys (JWKs)."""
    jwks = await get_jwks()
    print(f"{jwks=}")

    headers = jwt.get_unverified_header(token)
    kid = headers.get("kid")
    algorithm = headers.get("alg", ["RS256"])

    key = get_key_for_token(kid, jwks)
    print(f"{key=}")

    try:
        return jwt.decode(token, key, algorithms=algorithm, audience="account")
    except Exception as e:
        print("Token validation failed: %s", e)
        return None


async def grant_access_token(id_token: str) -> str:
    data = await decode_token(id_token)
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid workflow",
        )
    return "super-secret-token"


@app.get("/token")
async def get_token(
    authorization: Optional[str] = Header(default=None),
) -> dict:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Must provide a valid id token",
        )

    _, id_token = authorization.split()
    access_token = await grant_access_token(id_token)
    return {"access_token": access_token}
