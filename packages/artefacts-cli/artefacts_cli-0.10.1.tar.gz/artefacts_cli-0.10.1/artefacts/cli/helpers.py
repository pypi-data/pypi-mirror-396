import configparser
import os
from typing import Any, Optional

import click
import requests

from artefacts.cli.constants import CONFIG_PATH, CONFIG_DIR
from artefacts.cli.errors import InvalidAPIKey


def is_valid_api_key(value: Any) -> bool:
    """
    Valid means non-empty string object.
    """
    try:
        return value and len(value) > 0
    except TypeError:
        return False


def get_conf_from_file():
    config = configparser.ConfigParser()
    if not os.path.isfile(CONFIG_PATH):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        config["DEFAULT"] = {}
        with open(CONFIG_PATH, "w") as f:
            config.write(f)
    config.read(CONFIG_PATH)
    return config


def set_global_property(key: str, value: Any) -> None:
    config = get_conf_from_file()
    config.set("global", key, value)
    with open(CONFIG_PATH, "w") as f:
        config.write(f)


def get_global_property(key: str, default: Optional[Any] = None) -> Optional[Any]:
    config = get_conf_from_file()
    return config.get("global", key, fallback=default)


def get_artefacts_api_url(project_profile):
    return os.environ.get(
        "ARTEFACTS_API_URL",
        project_profile.get(
            "ApiUrl",
            "https://app.artefacts.com/api",
        ),
    )


def add_key_to_conf(project_name: str, api_key: str) -> None:
    """
    Add a valid key to the configuration file.
    """
    if is_valid_api_key(api_key):
        config = get_conf_from_file()
        config[project_name] = {"ApiKey": api_key}
        with open(CONFIG_PATH, "w") as f:
            config.write(f)
    else:
        raise InvalidAPIKey()


def endpoint_exists(url: str) -> bool:
    """
    Simplistic confirmation of the existance of an endpoint.

    Under discussion: Use of HEAD verbs, etc.
    """
    access_test = requests.get(url)
    return access_test.status_code < 400


def ask_for_non_empty_string(message: str, secret: bool = False) -> str:
    """
    Wrapper around click.prompt to check for None and empty strings.
    """

    def non_empty_str(value):
        if value:
            vs = str(value)
            if len(vs) > 0:
                return vs
        raise InvalidAPIKey()

    return click.prompt(message, type=str, hide_input=secret, value_proc=non_empty_str)
