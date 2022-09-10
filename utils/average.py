from typing import Union

def average(values: list) -> Union[int, float]:
    if len(values) == 0:
        return 0.0
    return sum(values) / len(values)
