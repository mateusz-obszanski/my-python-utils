from pytest import raises
from control_flow import (
    run_for_args_and_kwargs_sequence,
    InvalidValueError,
    ArgumentTypeError,
    run_if,
)


class Test_run_for_args_and_kwargs_sequence:
    def test_raises_return_option(self):
        with raises(InvalidValueError):
            run_for_args_and_kwargs_sequence(print, (), {}, return_option="Di$c@rD")

    def test_discard(self):
        result = run_for_args_and_kwargs_sequence(pow, [(2, 3)], return_option="discard")
        assert result is None

    def test_last(self):
        result = run_for_args_and_kwargs_sequence(pow, [(2, 3), (2, 4)], return_option="last")
        assert result == pow(2, 4)

    def test_all(self):
        args = [(2, 3), (2, 4)]
        result = run_for_args_and_kwargs_sequence(pow, args, return_option="all")
        assert result == [pow(b, e) for b, e in args]

    def test_all_with_kwargs(self):
        args = [(2, 3), (2, 4)]
        kwargs = [{"mod": 7}, {"mod": 14}]
        result = run_for_args_and_kwargs_sequence(pow, args, kwargs, return_option="all")
        assert result == [pow(b, e, mod=kw["mod"]) for (b, e), kw in zip(args, kwargs)]

    def test_fill_value(self):
        args = [(2, 3), (2, 4)]
        kwargs = [{"mod": 2}]
        fill_value = {"mod": 3}
        result = run_for_args_and_kwargs_sequence(
            pow, args, kwargs, until_longer=True, fill_value=fill_value
        )
        assert result == [0, 1]


class Test_run_if:
    def test_raises_pred_neither_bool_nor_callable(self):
        with raises(ArgumentTypeError):
            run_if(print, 42)  # type: ignore

    def test_bool(self):
        assert run_if(pow, False, (2, 3)) is None
        assert run_if(pow, True, (2, 3)) == 8
