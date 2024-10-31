from abc import ABC
from copy import deepcopy
from typing import Optional


def is_blank(data: Optional[str]) -> bool:
    if data is None:
        return True

    data_str = str(data)
    if len(data_str) == 0:
        return True

    if len(data_str.strip()) == 0:
        return True

    return False



class ValidatedDataModel(ABC):
    def validate(self) -> None:
        raise NotImplementedError('validate method has not been implemented')

    def copy(self):
        return deepcopy(self)

    def json(self) -> dict:
        return vars(self)
