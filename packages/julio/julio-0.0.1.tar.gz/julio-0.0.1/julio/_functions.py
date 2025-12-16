"""Functions for julio."""

# Authors: Synchon Mandal <s.mandal@fz-juelich.de>
# License: AGPL

from pathlib import Path

import datalad.api as dl
import structlog
from datalad.support.exceptions import IncompleteResultsError


__all__ = ["create"]


logger = structlog.get_logger()


def create(registry_path: Path):
    """Create a registry at `registry_path`.

    Parameters
    ----------
    registry_path : pathlib.Path
        Path to the registry.

    Raises
    ------
    RuntimeError
        If there is a problem creating the registry.

    """
    try:
        ds = dl.create(
            path=registry_path,
            cfg_proc="text2git",
            on_failure="stop",
            result_renderer="disabled",
        )
    except IncompleteResultsError as e:
        raise RuntimeError(f"Failed to create dataset: {e.failed}") from e
    else:
        logger.debug(
            "Registry created successfully",
            cmd="create",
            path=str(registry_path.resolve()),
        )
    # Add config file
    conf_path = Path(ds.path) / "registry-config.yml"
    conf_path.touch()
    ds.save(
        conf_path,
        message="[julio] add registry configuration",
        on_failure="stop",
        result_renderer="disabled",
    )
