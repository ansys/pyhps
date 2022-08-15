import argparse
import asyncio
import threading
import time
import webbrowser

from authlib.integrations.httpx_client import AsyncOAuth2Client
from authlib.jose import jwt
import httpx

"""
Links:
- Setting up google auth:
http://www.mastertheboss.com/keycloak/google-social-login-with-keycloak/
- Setting up MS auth:
https://www.grebintegration.dk/2021/03/07/
microsoft-azure-active-directory-as-keycloak-identity-provider/
"""

client_id = "rep-cli"
scope = "openid"
base_url = "https://localhost:8443/rep/auth/realms/rep"
authorization_endpoint = f"{base_url}/protocol/openid-connect/auth"
token_endpoint = f"{base_url}/protocol/openid-connect/token"


async def get_token_info(authorization_response):
    d = {}
    # token = loop.run_until_complete(
    #    client.fetch_token(
    #      token_endpoint, authorization_response=authorization_response, redirect_uri=redirect_uri
    #    )
    # )
    token = await client.fetch_token(
        token_endpoint, authorization_response=authorization_response, redirect_uri=redirect_uri
    )
    d["token"] = {}
    for k, v in token.items():
        d["token"][k] = v
        # print(f"- {k} : {str(v)[:60]}")

    # https://stackoverflow.com/questions/54884938/generate-jwt-token-in-keycloak-and-get-public-key-to-verify-the-jwt-token-on-a-t
    # To retrieve groups an extra mapper needs to be added:
    # https://stackoverflow.com/questions/56362197/keycloak-oidc-retrieve-user-groups-attributes
    response = httpx.get(base_url, verify=False)
    public_key = response.json()["public_key"]
    # print(f"Public key: {str(public_key)[:60]} ...")
    public_key = f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"

    data = jwt.decode(token["access_token"], public_key)
    d["access_token"] = {}
    for k, v in data.items():
        # print(f"- {k} : {str(v)[:60]}")
        d["access_token"][k] = v

    data = jwt.decode(token["id_token"], public_key)
    d["id_token"] = {}
    for k, v in data.items():
        # print(f"- {k} : {str(v)[:60]}")
        d["id_token"][k] = v

    d["user"] = {"id": data["sub"]}
    return d


def run_server():
    import falcon.asgi
    import uvicorn

    class TokenInfo:
        async def on_get(self, req, resp):
            d = await get_token_info(req.url)
            lines = [
                "<h1>By 'eck chief! It works!</h1>",
            ]
            for grp, data in d.items():
                grp_name = grp.replace("_", " ").title()
                lines.append(f"<h3>{grp_name}</h3>")
                lines.append("<table>")
                lines.append("<tr>")
                lines.append("<th>Key</th>")
                lines.append("<th>Value</th>")
                lines.append("</tr>")
                for k, v in data.items():
                    lines.append("<tr>")
                    lines.append(f"<td>{k}</td>")
                    lines.append(f"<td>{str(v)}</td>")
                    lines.append("</tr>")
                lines.append("</table>")

            resp.status = falcon.HTTP_200
            resp.content_type = "text/html"
            resp.text = "\n".join(lines)

    app = falcon.asgi.App()
    app.add_route("/token-info", TokenInfo())

    uv_config = {
        "host": "localhost",
        "port": 9999,
        "log_level": "debug",
        "log_config": None,
    }

    uvicorn.run(app, **uv_config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build and test")
    parser.add_argument("mode", default="web", choices=["web", "cli"])

    args = parser.parse_args()

    if args.mode == "web":
        redirect_uri = "http://localhost:9999/token-info"
    else:
        redirect_uri = "https://localhost:8443/rep/jms/api/v1"

    client = AsyncOAuth2Client(client_id, scope=scope, verify=False)
    uri, state = client.create_authorization_url(authorization_endpoint, redirect_uri=redirect_uri)
    print(f"Auth URL: {uri}")
    webbrowser.open(uri)

    if args.mode == "web":
        server = threading.Thread(target=run_server, daemon=True)
        server.start()
        while True:
            time.sleep(1)
    else:
        authorization_response = input("Auth response URL:")
        loop = asyncio.get_event_loop()
        d = loop.run_until_complete(get_token_info(authorization_response))
        for grp, data in d.items():
            print(grp.replace("_", " ").title())
            for k, v in data.items():
                print(f"  - {k}: {str(v)[:60]}")
