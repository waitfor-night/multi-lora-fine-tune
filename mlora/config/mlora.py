import yaml

from typing import Dict, List

from .dispatcher import DispatcherConfig
from .dataset import DatasetConfig
from .adapter import AdapterConfig, ADAPTERCONFIG_CLASS
from .task import TaskConfig


class MLoRAConfig:
    dispather_: DispatcherConfig = None
    tasks_: List[TaskConfig] = []
    __datasets_: Dict[str, DatasetConfig] = {}
    __adapters_: Dict[str, AdapterConfig] = {}

    def __init_datasets(self, config: List[Dict[str, any]]):
        for item in config:
            name = item["name"]
            self.__datasets_[name] = DatasetConfig(item)

    def __init_adapters(self, config: List[Dict[str, any]]):
        for item in config:
            name = item["name"]
            atype = item["type"]
            self.__adapters_[name] = ADAPTERCONFIG_CLASS[atype](item)

    def __init_tasks(self, config: List[Dict[str, any]]):
        for item in config:
            adapter_name = item["adapter"]
            dataset_name = item["dataset"]
            self.tasks_.append(TaskConfig(item, self.__adapters_[
                               adapter_name], self.__datasets_[dataset_name]))

    def __init__(self, path: str):
        with open(path) as fp:
            config = yaml.safe_load(fp)

        self.dispather_ = DispatcherConfig(config["dispatcher"])

        # must ensure the adapter and datasets init before the task
        self.__init_datasets(config["datasets"])
        self.__init_adapters(config["adapters"])

        self.__init_tasks(config["tasks"])