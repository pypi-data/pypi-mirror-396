"""Test for functions."""

# Authors: Synchon Mandal <s.mandal@fz-juelich.de>
# License: AGPL

import shutil
from pathlib import Path

import pytest

from julio import create


def test_create(tmp_path: Path) -> None:
    """Test registry creation.

    Parameters
    ----------
    tmp_path : Path
        Pytest fixture that provides a temporary directory.

    """
    registry_path = tmp_path / "test_registry"
    create(registry_path)
    config_path = registry_path / "registry-config.yml"
    assert config_path.is_file()
    with pytest.raises(RuntimeError):
        create(registry_path)
    shutil.rmtree(registry_path)
