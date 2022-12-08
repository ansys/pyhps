import logging
from pathlib import Path
from typing import Callable, List

from ansys.rep.client.client import Client
from ansys.rep.client.exceptions import ClientError

log = logging.getLogger(__name__)


class FsApi(object):
    """Wraps around the REP File Storage Gateway endpoints.

    Parameters
    ----------
    client : Client
        A REP client object.

    """

    def __init__(self, client: Client):
        self.client = client

    @property
    def url(self) -> str:
        """Returns the API url"""
        return f"{self.client.rep_url}/fs/api/v1"

    def get_api_info(self):
        """Return info like version, build date etc of the FS API the client is connected to"""
        r = self.client.session.get(self.url)
        return r.json()

    def download_file(
        self,
        bucket: str,
        name: str,
        target_path: str,
        progress_handler: Callable[[int], None] = None,
        stream: bool = True,
    ) -> None:

        Path(target_path).mkdir(parents=True, exist_ok=True)
        download_link = f"{self.url}/{bucket}/{name}"

        with self.client.session.get(download_link, stream=stream) as r, open(
            target_path, "wb"
        ) as f:
            for chunk in r.iter_content(chunk_size=None):
                f.write(chunk)
                if progress_handler is not None:
                    progress_handler(len(chunk))

    def upload_file(self, source_path, bucket, name) -> str:
        with open(source_path, "rb") as file_content:
            r = self.client.session.post(
                f"{self.url}/{bucket}/{name}",
                data=file_content,
                headers={"content-type": "application/octet-stream"},
            )
        return r.json()["checksum"]

    def delete_file(self, bucket: str, name: str):
        r = self.client.session.put(f"{self.url}/remove/{bucket}/{name}")

    def delete_bucket(self, bucket: str):
        r = self.client.session.put(f"{self.url}/remove/{bucket}")

    def file_exists(self, bucket: str, name: str) -> bool:

        try:
            r = self.client.session.get(f"{self.url}/exists/{bucket}/{name}")
        except ClientError as e:
            if e.response.status_code == 404:
                return False
            else:
                raise e
        return True

    def bucket_exists(self, bucket: str) -> bool:

        try:
            r = self.client.session.get(f"{self.url}/exists/{bucket}")
        except ClientError as e:
            if e.response.status_code == 404:
                return False
            else:
                raise e
        return True

    def get_files(self, bucket=None) -> List[str]:
        """
        This returns something like
        [
            'ansfs://02rkHkcHaPIcmkohb4nekQ/02rkHnlx3tzdwkdYg8Mt1E_inp',
            'ansfs://02rkHkcHaPIcmkohb4nekQ/02rkHmBSayvhlPbTkjEe8h_d3plot',
            ...
        ]
        """
        url = f"{self.url}/list"
        if bucket:
            url += f"/{bucket}"
        r = self.client.session.get(url)
        return r.json()["file_list"]
