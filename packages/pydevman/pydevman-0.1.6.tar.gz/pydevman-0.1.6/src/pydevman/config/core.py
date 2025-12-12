from os import PathLike
from typing import Dict, Union

from omegaconf import OmegaConf

from pydevman.file.load import load_config_file


# 对于配置，建议开启环境，关闭 merge
def create_config(arg: Union[Dict, PathLike]) -> OmegaConf:
    """单文件配置导入，可以导入 json,toml,yaml 等文件"""
    _arg = arg
    if isinstance(arg, PathLike):
        _arg = load_config_file(arg)
    return OmegaConf.create(_arg)


def merge_config(config: OmegaConf, arg) -> None:
    """从路径中合并配置"""
    _config = create_config(arg)
    config.merge_with(_config)
