from abc import ABC, abstractmethod


class CfgProvider(ABC):

    @abstractmethod
    def provide_cfg(self):
        pass
