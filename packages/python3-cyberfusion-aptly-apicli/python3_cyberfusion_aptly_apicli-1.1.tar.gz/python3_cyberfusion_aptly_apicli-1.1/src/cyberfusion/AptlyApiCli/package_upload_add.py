"""Script to upload package and add to repository."""

import sys

from cyberfusion.AptlyApiCli import AptlyApiRequest
from cyberfusion.Common import generate_random_string


def upload_temporary_file(
    request: AptlyApiRequest, *, directory_name: str, path: str
) -> str:
    """Upload temporary file to add to repository later."""
    with open(path, "rb") as f:
        request.POST(f"/api/files/{directory_name}", data={}, files={"file": f})

        return request.execute()[0]  # List of uploaded files; only uploaded one


def add_package(
    request: AptlyApiRequest, *, repository_name: str, temporary_file_path: str
) -> None:
    """Add package to repository from already uploaded temporary file."""
    request.POST(f"/api/repos/{repository_name}/file/{temporary_file_path}", data={})
    request.execute()


def main() -> None:
    """Spawn relevant class for CLI function."""
    request = AptlyApiRequest()

    repository_name = sys.argv[1]
    paths = sys.argv[2:]

    for path in paths:
        directory_name = generate_random_string()

        temporary_file_path = upload_temporary_file(
            request, directory_name=directory_name, path=path
        )
        add_package(
            request,
            repository_name=repository_name,
            temporary_file_path=temporary_file_path,
        )

        print(f"Processed '{path}'")
