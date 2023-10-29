import asyncio
import os.path
import sys

from httpx import HTTPStatusError

from xbox.webapi.api.client import XboxLiveClient
from xbox.webapi.authentication.manager import AuthenticationManager
from xbox.webapi.authentication.models import OAuth2TokenResponse
from xbox.webapi.common.signed_session import SignedSession
from xbox.webapi.scripts import CLIENT_ID, CLIENT_SECRET, TOKENS_FILE

"""
This uses the global default client identification by OpenXbox
You can supply your own parameters here if you are permitted to create
new Microsoft OAuth Apps and know what you are doing
"""
client_id = "7cc88370-21c2-43c6-bf9d-06f224740c0a"
client_secret = "o.A8Q~_b-5KDCxiSyvAxc59-qsjsTk~KztXwac5y"
tokens_file = "D:\\Coding\\valheim_synchronizer\\xbox_tokens.json"

"""
For doing authentication, see xbox/webapi/scripts/authenticate.py
"""


async def async_main():
    # Create a HTTP client session
    async with SignedSession() as session:
        """
        Initialize with global OAUTH parameters from above
        """
        auth_mgr = AuthenticationManager(session, client_id, client_secret, "")

        """
        Read in tokens that you received from the `xbox-authenticate`-script previously
        See `xbox/webapi/scripts/authenticate.py`
        """
        try:
            with open(tokens_file) as f:
                tokens = f.read()
            # Assign gathered tokens
            auth_mgr.oauth = OAuth2TokenResponse.parse_raw(tokens)
        except FileNotFoundError as e:
            print(
                f"File {tokens_file} isn`t found or it doesn`t contain tokens! err={e}"
            )
            sys.exit(-1)

        """
        Refresh tokens, just in case
        You could also manually check the token lifetimes and just refresh them
        if they are close to expiry
        """
        try:
            await auth_mgr.refresh_tokens()
        except HTTPStatusError as e:
            print(
                f"""
                Could not refresh tokens from {tokens_file}, err={e}\n
                You might have to delete the tokens file and re-authenticate 
                if refresh token is expired
            """
            )
            sys.exit(-1)

        # Save the refreshed/updated tokens
        with open(tokens_file, mode="w") as f:
            f.write(auth_mgr.oauth.json())
        print(f"Refreshed tokens in {tokens_file}!")

        """
        Construct the Xbox API client from AuthenticationManager instance
        """
        xbl_client = XboxLiveClient(auth_mgr)

        """
        Some example API calls
        """
        # Get friendslist
        friendslist = await xbl_client.people.get_friends_own()
        print(f"Your friends: {friendslist}\n")


asyncio.run(async_main())
