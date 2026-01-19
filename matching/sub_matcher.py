from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


class SubMatcher(ABC):

    @dataclass
    class Parameters(ABC):
        pass

    @dataclass
    class Result(ABC):
        matches: List[List[bool]]

    def __init__subclass__(cls, **_) -> None:  # type: ignore
        super().__init_subclass__()
        parameters_class = getattr(cls, "Parameters", None) 
        assert isinstance(parameters_class, type)
        assert issubclass(parameters_class, SubMatcher.Parameters)
        result_class = getattr(cls, "Result", None) 
        assert isinstance(result_class, type)
        assert issubclass(result_class, SubMatcher.Result)

    @abstractmethod
    def match(self, keywords: List[str], texts: List[str], parameters: SubMatcher.Parameters) -> Result:
        raise NotImplementedError("@abstractmethod")
    