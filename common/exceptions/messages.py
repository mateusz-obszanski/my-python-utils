from typing import Optional as __Optional, Sequence as __Sequence, Union as __Union
from ..format import _pluralize as __pluralize


__VALUE_ERROR_POSITIONAL_MSG_FMT = (
    "{f_name}() expected {expected_n} positional argument{plural_suffix}, but {n} were given"
)
__VALUE_ERROR_KEYWORD_MSG_FMT = "{f_name}() got unexpected keyword argument{suffix} {keys}"


def value_error_positional_msg(
    f_name: str, expected_n: __Union[int, str], args: __Optional[__Sequence] = None
) -> str:
    args_len = 0 if args is None else len(args)
    return __VALUE_ERROR_POSITIONAL_MSG_FMT.format(
        f_name=f_name,
        expected_n=expected_n,
        plural_suffix=__pluralize((args_len)),
        n=args_len,
    )


def value_error_keyword_msg(f_name: str, keys: __Union[str, __Sequence[str]]) -> str:
    if isinstance(keys, str):
        keys = (keys,)

    return __VALUE_ERROR_KEYWORD_MSG_FMT.format(
        f_name=f_name, suffix=__pluralize(len(keys)), keys=", ".join(repr(keys))
    )
