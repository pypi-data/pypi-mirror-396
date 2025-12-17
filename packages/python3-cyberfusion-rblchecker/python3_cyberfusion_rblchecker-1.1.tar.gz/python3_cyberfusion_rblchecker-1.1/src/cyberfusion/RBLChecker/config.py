"""Config."""

import yaml


def get_config(path: str) -> dict:
    """Get config."""
    with open(path, "r") as fh:
        return yaml.load(fh.read(), Loader=yaml.SafeLoader)
