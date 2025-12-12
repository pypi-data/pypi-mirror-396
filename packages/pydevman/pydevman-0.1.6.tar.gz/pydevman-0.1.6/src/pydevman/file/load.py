import configparser
import json
from pathlib import Path

import tomli
import yaml
from omegaconf import OmegaConf

from pydevman.file.common import assert_path_exist_and_is_file


def load_config_file(path):
    assert_path_exist_and_is_file(path)
    _path = Path(path)
    _suffix = _path.suffix
    if _suffix == ".json":
        return _parse_json(path)
    if _suffix in (".yaml", ".yml"):
        return _parse_yaml(path)
    if _suffix == ".toml":
        return _parse_toml(path)
    if _suffix == ".ini":
        return _parse_ini(path)
    raise TypeError("文件类型错误")


def _parse_json(_path):
    with open(_path, encoding="utf-8") as stream:
        return json.load(stream)


def _parse_yaml(_path):
    with open(_path, encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def _parse_toml(_path):
    with open(_path, "rb") as stream:
        return tomli.load(stream)


def _parse_ini(_path):
    parser = configparser.ConfigParser()
    parser.read(_path, encoding="utf8")

    data = {section: dict(parser[section]) for section in parser.sections()}
    return OmegaConf.create(data)
