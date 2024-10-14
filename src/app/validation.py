from abc import ABC
from copy import deepcopy


class ValidatedDataModel(ABC):
    def validate(self) -> None:
        raise NotImplementedError('validate method has not been implemented')
    def copy(self):
        return deepcopy(self)
    def json(self) -> dict:
        return vars(self)
