import os
from pathlib import Path
from shutil import make_archive, unpack_archive
from tempfile import TemporaryDirectory
from typing import Callable, Iterable, Optional, Tuple, Union

from hmd_cli_tools.okta_tools import get_auth_token
from hmd_graphql_client.hmd_rest_client import RestClient
from hmd_lib_librarian_client.hmd_lib_librarian_client import HmdLibrarianClient

ARTIFACT_NAME_TEMPLATE = "{name}_{version}_{type}.zip"


def get_artifact_librarian_client(
    hmd_customer_code: str, hmd_region: str, auth_token: Optional[str] = None
) -> HmdLibrarianClient:
    librarian_url = os.environ.get("HMD_ARTIFACT_LIBRARIAN_URL")
    librarian_api_key = os.environ.get("HMD_ARTIFACT_LIBRARIAN_API_KEY")

    if not auth_token:
        auth_token = get_auth_token()
    assert (
        librarian_api_key or auth_token
    ), 'A valid auth token or an API key must be provided for the artifact librarian (ENV_VAR, "HMD_ARTIFACT_LIBRARIAN_API_KEY").'

    if not librarian_url:
        librarian_url = f"https://artifact-aaa-{hmd_region}.{hmd_customer_code}-admin-neuronsphere.io"

    base_client = RestClient(librarian_url, None, librarian_api_key, auth_token)
    return HmdLibrarianClient(base_client=base_client)


def zip_and_archive(
    hmd_customer_code: str,
    hmd_region: str,
    content_item_path: str,
    content_item_type: str,
    path: Union[str, Path],
    max_part_size: int = 100000000,
    number_of_threads: int = 2,
    number_of_tries: int = 3,
    seconds_between_retries: int = 30,
    status_callback: Callable = None,
    auth_token: str = None,
):

    if not os.path.exists(path):
        raise Exception(f"Specified path, {path}, does not exist.")
    if not os.path.isdir(path):
        raise Exception(f"Specified path, {path}, is not a directory.")

    with TemporaryDirectory() as tmpdir:
        artifact_path = os.path.join(tmpdir, "tmp_file")
        make_archive(artifact_path, "zip", path)

        # Add the ".zip" suffix...
        artifact_path = f"{artifact_path}.zip"
        client = get_artifact_librarian_client(
            hmd_customer_code, hmd_region, auth_token
        )
        return client.put_file(
            content_path=content_item_path,
            file_name=artifact_path,
            content_item_type=content_item_type,
            max_part_size=max_part_size,
            number_of_threads=number_of_threads,
            number_of_tries=number_of_tries,
            seconds_between_retries=seconds_between_retries,
            status_callback=status_callback,
        )


def retrieve_and_unzip(
    hmd_customer_code: str,
    hmd_region: str,
    content_item_path: str,
    paths: Union[Union[Path, str], Iterable[Union[Path, str]]],
    auth_token: str = None,
):
    """
    Retrieve a zipped artifact file from the artifacts librarian and unzip it on the local
    filesystem in one or more specified locations.

    :param hmd_customer_code: The HMD customer code.
    :param hmd_region: The HMD region code.
    :param content_item_path: The complete content item path of the content item to retrieve.
    :param paths: The local disk location(s) in which to extract the downloaded file.
    :return: None
    """
    if not isinstance(paths, list):
        paths = [paths]

    paths = set(paths)
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)

        if not os.path.isdir(path):
            raise Exception(f"Specified path, {path}, is not a directory.")

    with TemporaryDirectory() as tmpdir:

        tmpfile = os.path.join(tmpdir, "tmpfile.zip")
        client = get_artifact_librarian_client(
            hmd_customer_code, hmd_region, auth_token
        )
        client.get_file(
            content_path=content_item_path, file_name=tmpfile, force_overwrite=True
        )
        for path in paths:
            unpack_archive(tmpfile, path, "zip")


def content_item_path_from_parts(
    repo_name: str, repo_version: str, item_type: str, path_root: str = "repository"
) -> str:
    artifact_name = ARTIFACT_NAME_TEMPLATE.format(
        **{"name": repo_name, "version": repo_version, "type": item_type}
    )
    return f"{path_root}:/{repo_name}/{repo_version}/{artifact_name}"


def content_item_path_from_spec(
    content_item_path_spec: str,
) -> Tuple[str, Optional[str]]:
    """Parse a spec string and return the content item path and file specifier.

    Path specs are of the form: <name>@<version>:<item_type>{:<file_part>}

    :param content_item_path_spec:
    :type content_item_path_spec:
    :return:
    :rtype:
    """
    parts = content_item_path_spec.split(":")
    assert (
        2 <= len(parts) <= 3
    ), f"File spec of form: <name>@<version>:<item_type>{{:<file_part>}} expected. Was {content_item_path_spec}"
    name_version = parts[0]
    repo_name, version = name_version.split("@")
    item_type = parts[1]
    file_spec = None
    if len(parts) > 2:
        file_spec = parts[2]

    name = ARTIFACT_NAME_TEMPLATE.format(
        **{"name": repo_name, "version": version, "type": item_type}
    )
    return f"repository:/{repo_name}/{version}/{name}", file_spec
