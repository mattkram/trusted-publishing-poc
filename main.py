from typing import Optional

from fastapi import FastAPI, Header, HTTPException, status

OIDC_CONFIG_URL = (
    "https://token.actions.githubusercontent.com/.well-known/openid-configuration"
)

app = FastAPI()


@app.get("/")
async def home() -> dict:
    return {"hello": "world"}


async def grant_access_token(id_token: str) -> str:
    return "super-secret-token"
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid workflow",
    )


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
