from typing import Mapping as _Mapping, Any as _Any


def textified_kwargs(kwargs: _Mapping[str, _Any], /) -> str:
    try:
        return ", ".join(f"{key}={val}" for key, val in kwargs.items())
    except AttributeError:
        # generic Mapping might not implement items method
        return ", ".join(f"{key}={kwargs[key]}" for key in kwargs.keys())
