# Fake Docker client

from dataclasses import dataclass, asdict
import hashlib
from random import randint

from docker import DockerClient, APIClient
from docker.constants import DEFAULT_DOCKER_API_VERSION


@dataclass
class SimpleImage:
    Id: str
    Created: str
    Repository: str
    RepoTags: list


class TestDockerAPIClient(APIClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake_server_db = {}
        self.fake_image_id_base = hashlib.new("sha256")

    def reset(self) -> None:
        self.fake_server_db = {}
        self.fake_image_id_base = hashlib.new("sha256")

    def build(self, *args, **kwargs):
        if kwargs["tag"] in self.fake_server_db:
            original = self.fake_server_db[kwargs["tag"]]
            for img in original:
                # Mimick what Docker seems to be doing
                img.Repository = ""
                img.RepoTags = []
        else:
            original = []

        # Generate a random yet compliant image ID
        # Note the use of update, to ensure calling many times will be on different input (so unique IDs).
        self.fake_image_id_base.update(bytes(randint(0, 100)))
        iid = "sha256:" + self.fake_image_id_base.hexdigest()

        new_collection = [
            SimpleImage(
                **{
                    "Id": iid,
                    "Created": "1 min ago",
                    "Repository": kwargs["tag"],
                    "RepoTags": [kwargs["tag"] + ":latest"],
                }
            )
        ]
        # Ensure the new entry is in the first place
        new_collection.extend(original)
        self.fake_server_db[kwargs["tag"]] = new_collection

        return [b'"fake"', b'"test"', b'"logs"']

    def images(self, *args, **kwargs):
        if kwargs.get("name", None):
            return self.fake_server_db.get(kwargs["name"])
        else:
            return [v for vs in self.fake_server_db.values() for v in vs]

    def get_image(self, name):
        # Index 0 is the latest
        return self.fake_server_db.get(name)[0]

    def inspect_image(self, name):
        return asdict(self.get_image(name))


class TestDockerClient(DockerClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = TestDockerAPIClient(version=kwargs["version"])


def make_fake_api_client():
    """
    Incomplete fake API client.
    """
    return TestDockerAPIClient(version=DEFAULT_DOCKER_API_VERSION)


def make_fake_client():
    """
    Test client with a fake API client.
    """
    return TestDockerClient(version=DEFAULT_DOCKER_API_VERSION)
