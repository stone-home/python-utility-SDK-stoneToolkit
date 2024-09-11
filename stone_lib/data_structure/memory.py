from abc import ABC, abstractmethod
from typing import Union


class MemoryBlock(ABC):
    @abstractmethod
    @property
    def bytes(self) -> int:
        pass

    @abstractmethod
    @property
    def address(self) -> str:
        pass

    @abstractmethod
    @property
    def alloc_time(self) -> Union[int, float]:
        pass

    @abstractmethod
    @property
    def free_time(self) -> Union[int, float]:
        pass

    @abstractmethod
    @property
    def duration(self) -> Union[int, float]:
        pass

    def __repr__(self):
        return f"Memory({self.address}): {self.bytes} bytes, start: {self.alloc_time}, end: {self.free_time}, duration: {self.duration}"
