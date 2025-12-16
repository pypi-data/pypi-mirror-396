from pathlib import Path
from typing import Callable, Dict, Optional, Tuple

from hmd_graphql_client import BaseClient
from hmd_graphql_client.hmd_rest_client import RestClient
from requests import request
from awscrt import checksums
from base64 import b64encode

from .file_uploader import upload
from . import InvalidPathEntityError, InvalidPathMissingEntityError


class NoSuchContentItemException(Exception):
    pass


class FileExistsException(Exception):
    pass


class HmdLibrarianClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        base_client: Optional[BaseClient] = None,
        auth_token: Optional[str] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        client_certs: Optional[Tuple[str, str]] = None,
    ):
        assert not (
            base_client and (base_url or (api_key or auth_token or client_certs))
        ), f"Expected either 'base_client' or ('base_url' and ('api_key' or 'auth_token' or 'client_certs'))"
        if base_client:
            self.base_client = base_client
        else:
            self.base_client = RestClient(
                base_url,
                None,
                api_key,
                auth_token=auth_token,
                extra_headers=extra_headers,
                client_certs=client_certs,
            )

    def calculate_checksum(self, filename: str):
        with open(filename, "rb") as file_:
            file_bytes = file_.read()

            return b64encode(
                checksums.crc64nvme(file_bytes, 0).to_bytes(8, byteorder="big")
            ).decode("utf-8")

    def _put(self, manifest):
        return self.base_client.invoke_custom_operation("put", manifest)

    def _close(self, data):
        return self.base_client.invoke_custom_operation("close", data)

    def _search(self, data):
        return self.base_client.invoke_custom_operation("search", data)

    def _get(self, data):
        return self.base_client.invoke_custom_operation("get", data)

    def _get_by_nid(self, data):
        return self.base_client.invoke_custom_operation("get_by_nid", data)

    def put_file(
        self,
        content_path: str,
        file_name: str,
        content_item_type: str = None,
        status_callback: Callable = None,
        max_part_size: int = 100000000,
        number_of_threads: int = 2,
        number_of_tries: int = 3,
        seconds_between_retries: int = 30,
        checksum: Dict = None,
        resume_upload: bool = False,
    ):
        """Upload a file to an HMD librarian.

        Upload a file to an HMD librarian. For large files, this method
        supports multipart uploads on multiple threads.

        The ``max_part_size`` parameter specifies the maximum size of each part.

        The ``number_of_threads`` parameter specifies the number of threads
        to use to upload parts.

        The ``number_of_tries`` parameter specifies the number of times to
        retry a part upload on failure.

        The ``status_callback`` parameter is an optional method that will be called
        each time a file part has been uploaded. The callback method should take
        a single parameter the value of which will be of the form:
            {
                "total_parts": 5,
                "parts_complete": 1,
                "parts_percent": 0.20,
                "total_bytes": 100000000,
                "bytes_complete": 20000000,
                "bytes_percent": 0.20,
                "parts": [
                    {
                        "bytes_total": 20000000,
                        "bytes_uploaded": 20000000,
                        "etag": "b7cb500c5e3a928811c356bc8ab4782d",
                        "part_number": 1,
                        "tries": 1
                    },
                ]
            }



        :param content_path: The librarian content path to which to upload the file.
        :param file_name: The name of the file to upload.
        :param content_item_type: The librarian content_item_type.
        :param status_callback: An optional status callback to monitor the upload process.
        :param max_part_size: The maximum file size before creating a multi-part upload.
        :param number_of_threads: The number of threads to use to do a multi-part upload.
        :param number_of_tries: The number of times to retry a part upload on failure.
        :param seconds_between_retries: The number of seconds to wait between retries in the event of an upload failure.
        :param: checksum: Dictionary to send file checksum on close call

        :return:
        """
        path = Path(file_name)
        file_size = path.stat().st_size
        file_parts = []
        part_number = 1
        bytes_left = file_size
        while bytes_left > 0:
            part_size = bytes_left if bytes_left < max_part_size else max_part_size
            file_parts.append({"part_number": part_number, "part_size": part_size})
            part_number += 1
            bytes_left -= part_size

        payload = {"content_item_path": content_path}
        payload["file_parts"] = file_parts
        if resume_upload:
            payload["resume_upload"] = resume_upload

        if content_item_type:
            payload["content_item_type"] = content_item_type

        if checksum is not None:
            assert isinstance(
                checksum, dict
            ), "Provided checksum must be dictionary, {{ 'value': '', 'algorithm': 'CRC64NVME'}}"
            assert "value" in checksum, "Checksum dictionary must have 'value' property"
            assert checksum["value"] is not None, "Checksum value must not be empty"
            checksum["value"] = str(checksum["value"])
            assert (
                "algorithm" in checksum
            ), "Checksum dictionary must have 'algorithm' property"
            valid_algos = ["CRC64NVME"]
            assert (
                checksum["algorithm"] in valid_algos
            ), f"Invalid checksum algorithm, {checksum['algorithm']}, must be one of {valid_algos}"
            assert (
                self.calculate_checksum(file_name) == checksum["value"]
            ), "Checksum does not match file"

            payload["checksum"] = checksum
        put_result = self._put([payload])

        for result in put_result:
            if result.get("status", None) == "invalid_path_missing_entity":
                raise InvalidPathMissingEntityError(content_path)
            if result.get("status", None) == "invalid_path_entity":
                raise InvalidPathEntityError(content_path)

        results = upload(
            filename=file_name,
            upload_specs=put_result[0]["upload_specs"],
            number_of_threads=number_of_threads,
            status_callback=status_callback,
            number_of_tries=number_of_tries,
            seconds_between_retries=seconds_between_retries,
            checksum=checksum,
        )

        close_data = {
            "content_item_path": content_path,
            "upload_results": results,
        }
        if checksum is not None:
            close_data["checksum"] = checksum
        if "nid" in put_result[0]:
            close_data["nid"] = put_result[0]["nid"]

        close_result = self._close([close_data])

        if close_result[0]["status"] != "success":
            raise Exception(f"Close failed: {close_result[0]['message']}")

        return close_result[0]

    def get_file(self, content_path: str, file_name: str, force_overwrite=False):
        """Retrieve a file from a librarian based on the content path.

        :param content_path: The content path used to add the content to the librarian.
        :param file_name: The name of the file into which to store the file.
        :param force_overwrite: A flag indicating whether to overwrite an existing file.
        :return: None
        """

        file_path = Path(file_name)
        if file_path.is_dir():
            raise Exception(f"Path, {file_name}, is a directory.")

        if file_path.exists() and not force_overwrite:
            raise FileExistsException(f"File, {file_path}, exists.")

        get_result = self._get(
            {"attribute": "content_item_path", "operator": "=", "value": content_path}
        )

        if len(get_result) == 0:
            raise NoSuchContentItemException(
                f"Content item not found for path: {content_path}"
            )

        assert len(get_result) == 1, f"Multiple content items for path: {content_path}"

        self.download_file_from_url(get_result, file_path)

    def get_file_by_nid(self, nid: str, file_name: str, force_overwrite=False):
        """Retrieve a file from a librarian based on the global unique ID.

        :param nid: The global unique ID for the content item.
        :param file_name: The name of the file into which to store the file.
        :param force_overwrite: A flag indicating whether to overwrite an existing file.
        :return: None
        """

        file_path = Path(file_name)
        if file_path.is_dir():
            raise Exception(f"Path, {file_name}, is a directory.")

        if file_path.exists() and not force_overwrite:
            raise FileExistsException(f"File, {file_path}, exists.")

        nids = {"nids": [nid]}
        get_result = self._get_by_nid(nids)

        if len(get_result) == 0:
            raise NoSuchContentItemException(f"Content item not found for id: {nid}")

        assert len(get_result) == 1, f"Multiple content items for nid: {nid}"
        self.download_file_from_url(get_result, file_path)

    def download_file_from_url(self, ci_urls: list, dest_path: Path):
        with request("GET", ci_urls[0]["download_url"], stream=True) as r:
            r.raise_for_status()
            with open(dest_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=None):
                    if chunk:
                        f.write(chunk)

    def search_by_named_query(self, query_name: str, parameters: Dict):
        data = {"query_name": query_name, "query_params": parameters}
        return self.base_client.invoke_custom_operation("search_by_graph_query", data)

    def get_by_named_query(self, query_name: str, parameters: Dict):
        data = {"query_name": query_name, "query_params": parameters}
        return self.base_client.invoke_custom_operation("get_by_graph_query", data)

    def get_queryable_schemas(self):
        return self.base_client.invoke_custom_operation(
            "get_queryable_schemas", {}, http_method="GET"
        )

    def search_librarian(self, query_filter: Dict):
        return self.base_client.invoke_custom_operation(
            "search_librarian", query_filter
        )

    def add_tags(self, nid: str, tags: Dict[str, str]):
        return self.base_client.invoke_custom_operation(f"add_tags/{nid}", tags, "PUT")
