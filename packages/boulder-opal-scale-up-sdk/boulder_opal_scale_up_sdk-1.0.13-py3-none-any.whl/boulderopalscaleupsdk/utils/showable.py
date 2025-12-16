from abc import abstractmethod
from typing import Protocol, _ProtocolMeta, runtime_checkable

from pydantic import BaseModel
from pydantic._internal._model_construction import ModelMetaclass


@runtime_checkable
class Showable(Protocol):
    @abstractmethod
    def show(self) -> str: ...


# Metaclass inheriting from both BaseModel and Protocol metaclasses.
class _ShowableMeta(ModelMetaclass, _ProtocolMeta): ...


class ShowableBaseModel(BaseModel, Showable, metaclass=_ShowableMeta): ...
