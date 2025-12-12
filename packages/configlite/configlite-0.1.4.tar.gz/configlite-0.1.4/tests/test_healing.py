import os
from pathlib import Path
from typing import Any

import yaml
from configlite.config import BaseConfig


class ConfigTest(BaseConfig):
    foo: str = "foo"
    val: int = 10


def verify_variable(file: Path, name: str, value: Any) -> bool:
    with file.open() as o:
        data = yaml.safe_load(o)

    return data.get(name, None) == value


def test_restore_file(capsys):
    file = Path("test.yaml")

    config = ConfigTest(file)

    with file.open("w+") as o:
        o.write("")  # create an empty file

    assert config.foo == "foo"
    assert config.val == 10

    assert os.path.exists(f"{file}.bk")
    assert "WARNING" in capsys.readouterr().out


def test_mangled_file(capsys):
    file = Path("test.yaml")

    config = ConfigTest(file)

    with file.open("w+") as o:
        o.write("foo")  # create a broken file

    assert config.foo == "foo"
    assert config.val == 10

    assert os.path.exists(f"{file}.bk")
    assert "WARNING" in capsys.readouterr().out


def test_delete_variable():
    file = Path("test.yaml")

    config = ConfigTest(file)

    assert config.foo == "foo"
    assert config.val == 10

    # get the file content for modification
    with file.open() as o:
        data = yaml.safe_load(o)
        assert data["foo"] == "foo"
    # delete foo and write the changes
    del data["foo"]
    with file.open("w+") as o:
        yaml.dump(data, o)
    # make sure it's gone
    assert not verify_variable(file, "foo", "foo")
    # we should still have the default value
    assert config.foo == "foo"
    # check that it's been added back to the config
    assert verify_variable(file, "foo", "foo")
