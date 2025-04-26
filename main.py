from typing import Optional

from fastapi import FastAPI, Header

OIDC_CONFIG_URL = (
    "https://token.actions.githubusercontent.com/.well-known/openid-configuration"
)

app = FastAPI()


@app.get("/")
async def home() -> dict:
    return {"hello": "world"}


@app.get("/token")
async def get_token(
    id_token: Optional[str] = Header(default=None, alias="authorization"),
) -> dict:
    return {
        "access_token": "super-secret-token",
        "received_header": " ".join(id_token),
    }
