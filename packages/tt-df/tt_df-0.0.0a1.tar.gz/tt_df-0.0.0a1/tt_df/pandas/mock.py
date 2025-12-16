from __future__ import annotations
import importlib
import pkgutil
import types
from unittest.mock import DEFAULT, _Call, MagicMock, _patch, call, patch, _set_signature
import pandas as pd
from typing import Any, Dict, Generator, List
from functools import partial

SUPPORTED_IO_TYPES = [
    "orc",
    "parquet",
    "pickle",
    "csv",
]


class _CompareDF:
    def __init__(self, value: Any):
        self.value = value

    def __eq__(self, other: _CompareDF) -> bool:
        if not isinstance(other, _CompareDF):
            return False

        # Catch dataframes on either side
        if isinstance(self.value, pd.DataFrame):
            return self.value.equals(other.value)
        elif isinstance(other.value, pd.DataFrame):
            return other.value.equals(self.value)

        # If not a dataframe just do normal equality
        return self.value == other.value

    def __repr__(self):
        return self.value.__repr__()


def _rewrite_df_params(*args, **kwargs):
    # Is this overkill? Can we just convert some params?
    args = [_CompareDF(arg) for arg in args]
    kwargs = {k: _CompareDF(v) for k, v in kwargs.items()}

    return args, kwargs


def _rewrite_df_call(c: _Call) -> _Call:
    args, kwargs = c._get_call_arguments()
    args, kwargs = _rewrite_df_params(*args, **kwargs)
    return call(*args, **kwargs)


class DF_Mock(MagicMock):
    # TODO: assert_any_call
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def assert_called_with(self, *args, **kwargs):
        # Here we intercept the `assert_called_with` (which is used by other assertion methods) and rewrite any DataFrame arguments to avoid pandas' "The truth value of a DataFrame is ambiguous." message.
        args, kwargs = _rewrite_df_params(*args, **kwargs)
        # Convert the call args too
        self.call_args = _rewrite_df_call(self.call_args)

        return super().assert_called_with(*args, **kwargs)

    def assert_has_calls(self, calls: List[_Call], any_order: bool = False):
        # Similar to above, rewrite both call lists
        calls = [_rewrite_df_call(c) for c in calls]
        self.mock_calls = [_rewrite_df_call(c) for c in self.mock_calls]

        # Note: I have very little idea why but calls=calls does NOT work here, and causes an IndexError... ???
        return super().assert_has_calls(calls, any_order=any_order)


class FakeDF_IO:
    def __init__(self):
        self._read_paths: Dict[str, Dict[str, pd.DataFrame]] = {}
        self._patchers: List[_patch] = []

    def add_read_path(
        self, io_type: str, path: str, fake_df: pd.DataFrame
    ) -> FakeDF_IO:
        assert io_type in SUPPORTED_IO_TYPES, (
            f"Unsupported IO type: {io_type}. Supported types: {SUPPORTED_IO_TYPES}"
        )

        io_read_paths = self._read_paths.setdefault(io_type, {})
        io_read_paths[path] = fake_df

        return self

    def _read(
        self, original_func: callable, io_type: str, path: str, **kwargs
    ) -> pd.DataFrame:
        io_read_paths = self._read_paths.get(io_type, {})
        if path not in io_read_paths:
            # Be a passthrough if user has not mocked this path
            return original_func(path, **kwargs)

        assert path in io_read_paths, (
            f"Attempted to read path which has not been mocked: {path}"
        )

        return io_read_paths[path]

    def _validate_pd_target(self, target: str):
        # This lookup logic is based on the `unittest.mock` source code for patching. Specifically the helper method `_get_target`, since it is private we clone that logic here.
        # Ref: https://github.com/python/cpython/blob/726e8e8defc487c55ade9f6015aaf2bae6cec3f3/Lib/unittest/mock.py#L1677
        try:
            target, attribute = target.rsplit(".", 1)
        except (TypeError, ValueError, AttributeError):
            raise ValueError(f"Need a valid target to patch, you supplied: '{target}'")
        target_obj = pkgutil.resolve_name(target)

        # This logic comes from where the above target an attribute are used. Note for comprehension that although it is not relivent to this use case, the `local` is used in the patcher `__exit__` to decide if mocks should be deleted or restored to an original value.
        # Ref: https://github.com/python/cpython/blob/726e8e8defc487c55ade9f6015aaf2bae6cec3f3/Lib/unittest/mock.py#L1462
        # Ref: https://github.com/python/cpython/blob/726e8e8defc487c55ade9f6015aaf2bae6cec3f3/Lib/unittest/mock.py#L1638
        try:
            original = target_obj.__dict__[attribute]
        except (AttributeError, KeyError):
            original = getattr(target_obj, attribute, DEFAULT)

        if original == DEFAULT:
            raise ValueError(
                f"Found no existing attribute '{attribute}' on '{target}'. The 'patch_pd_io()' is designed to patching a subset of IO functions on a pandas module. Since many attributes do not get patched, the target should specify a module which has pandas functionality already present."
            )
        assert isinstance(original, types.ModuleType), (
            "The patch target does not appear to be a module (expected pandas module)."
        )

        # Smoke test to see if this is actually pandas
        missing_attributes = []
        for io_type in SUPPORTED_IO_TYPES:
            read_func = f"read_{io_type}"
            write_method = f"to_{io_type}"
            if not hasattr(original, read_func):
                missing_attributes.append(read_func)
            if not hasattr(getattr(original, "DataFrame", None), write_method):
                missing_attributes.append(f"DataFrame.{write_method}")

        if len(missing_attributes) != 0:
            raise ValueError(
                f"Specified target does not appear to be a pandas module, it is missing the following attributes: {missing_attributes}"
            )

    def patch_pd_io(
        self,
        target: str,
    ) -> Dict[str, DF_Mock]:
        self._validate_pd_target(target)

        mocks: Dict[str, DF_Mock] = {}
        for io_type in SUPPORTED_IO_TYPES:
            # Mock read!
            read_func = f"read_{io_type}"
            mock = DF_Mock(
                side_effect=partial(
                    self._read,
                    # Not getting this from the module since this would be more complicated
                    getattr(pd, read_func),
                    io_type,
                )
            )
            p = patch(f"{target}.{read_func}", new=mock)
            p.start()

            self._patchers.append(p)
            mocks[read_func] = mock

            # Mock write!
            write_method = f"to_{io_type}"
            mock = DF_Mock()
            mock = _set_signature(mock, getattr(pd.DataFrame, write_method))
            p = patch(
                f"{target}.DataFrame.{write_method}",
                new=mock,
            )
            p.start()

            self._patchers.append(p)
            mocks[write_method] = mock

        return mocks

    def stop_all(self):
        for p in self._patchers:
            p.stop()
        self._patchers = []


def _pd_patch_with_reload():
    # This is used primarily for testing purposes
    reloaded_pd = importlib.reload(pd)

    import pandas.core.frame

    reloaded_frame = importlib.reload(pandas.core.frame)

    for io_type in SUPPORTED_IO_TYPES:
        read_func = f"read_{io_type}"
        setattr(pd, read_func, getattr(reloaded_pd, read_func))

        write_method = f"to_{io_type}"
        setattr(
            pd.DataFrame, write_method, getattr(reloaded_frame.DataFrame, write_method)
        )


def _fake_df_io(pytestconfig: Any) -> Generator[FakeDF_IO, None, None]:
    """
    Used as a pytest below, if present.
    """
    fake_df_io = FakeDF_IO()
    yield fake_df_io
    fake_df_io.stop_all()


try:
    import pytest
except ImportError:
    pass
else:
    fake_df_io = pytest.fixture()(_fake_df_io)
