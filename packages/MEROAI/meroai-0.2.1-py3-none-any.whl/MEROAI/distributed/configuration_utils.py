import copy
import json
import os
from dataclasses import dataclass
from typing import Any, Union
@dataclass
class DistributedConfig:
    enable_expert_parallel: bool = False
    @classmethod
    def from_dict(cls, config_dict, **kwargs):
        config = cls(**config_dict)
        to_remove = []
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
                to_remove.append(key)
        for key in to_remove:
            kwargs.pop(key, None)
        return config
    def to_json_file(self, json_file_path: Union[str, os.PathLike]):
        with open(json_file_path, "w", encoding="utf-8") as writer:
            config_dict = self.to_dict()
            json_string = json.dumps(config_dict, indent=2, sort_keys=True) + "\n"
            writer.write(json_string)
    def to_dict(self) -> dict[str, Any]:
        return copy.deepcopy(self.__dict__)
    def __iter__(self):
        for attr, value in copy.deepcopy(self.__dict__).items():
            yield attr, value
    def __repr__(self):
        return f"{self.__class__.__name__} {self.to_json_string()}"
    def to_json_string(self):
        return json.dumps(self.__dict__, indent=2) + "\n"
    def update(self, **kwargs):
        to_remove = []
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                to_remove.append(key)
        unused_kwargs = {key: value for key, value in kwargs.items() if key not in to_remove}
        return unused_kwargs