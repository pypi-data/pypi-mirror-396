import sys

from raga import spinner, INVALID_RESPONSE_DATA, HTTPClient


class Project():
    def __init__(self, project_name, username, password, api_host):
        spinner.start()
        self.project_name = project_name
        self.username = username
        self.password = password
        self.api_host = api_host
        self.http_client = HTTPClient(self.api_host)
        spinner.stop()

    def authenticate_user(self, username, password):
        try:
            res_data = self.http_client.post(
                "api/authenticate",
                {"username": username, "password": password}
            )
            return res_data.get("token")
        except:
            print("Wrong username or password")
            sys.exit(1)

    def create_project(self):
        token = self.authenticate_user(self.username, self.password)
        res_data = self.http_client.post(
            "api/projects",
            {"name": self.project_name},
            {"Authorization": f'Bearer {token}'},
        )
        project_id = res_data.get("data", {}).get("id")
        if res_data.get("data") is None:
            print(res_data.get("message"))
            sys.exit(1)
        if not project_id:
            raise KeyError(INVALID_RESPONSE_DATA)
