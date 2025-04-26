from main import grant_access_token

TEST_TOKEN = "TEST_TOKEN"


async def test_grant_access_token():
    access_token = await grant_access_token(TEST_TOKEN)

    assert access_token == "super-secret-token"
