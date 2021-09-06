from inspect import currentframe
from typing import Optional as _Optional


def name_of_caller() -> _Optional[str]:
    """
    Returns caller's name
    """
    return (cf := currentframe()) and (bf := cf.f_back) and (bfc := bf.f_code) and bfc.co_name
