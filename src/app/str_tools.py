from typing import Optional


def isBlank(data: Optional[str]) -> bool:
    if data is None:
        return True

    data_str = str(data)
    if len(data_str) == 0:
        return True

    if len(data_str.strip()) == 0:
        return True

    return False
