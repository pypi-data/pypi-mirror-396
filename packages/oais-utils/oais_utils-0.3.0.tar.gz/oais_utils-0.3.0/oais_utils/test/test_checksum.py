import os
import tempfile
from unittest.mock import MagicMock, patch
from zlib import adler32

import pytest

from oais_utils.validate import _adler32sum, compute_hash


def write_temp_file(content: bytes):
    """Helper: create a temporary file with given content."""
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.write(content)
    tmp.close()
    return tmp.name


# ---------------------------------------------------------
# _adler32sum tests
# ---------------------------------------------------------


def test_adler32sum_empty_file():
    filename = write_temp_file(b"")
    expected = hex(adler32(b"", 1))[2:10].zfill(8).lower()
    assert _adler32sum(filename) == expected
    os.remove(filename)


def test_adler32sum_small_file():
    data = b"hello world"
    filename = write_temp_file(data)
    expected = hex(adler32(data, 1))[2:10].zfill(8).lower()
    assert _adler32sum(filename) == expected
    os.remove(filename)


# ---------------------------------------------------------
# compute_hash tests
# ---------------------------------------------------------


def test_compute_hash_adler32_calls_local_function():
    expected_result = "foo_bar"
    with patch(
        "oais_utils.validate._adler32sum", return_value=expected_result
    ) as mock_sum:
        result = compute_hash("dummyfile", alg="adler32")

    mock_sum.assert_called_once_with("dummyfile")
    assert result == expected_result


def test_compute_hash_other_alg_uses_open_fs_hash():

    fake_fs = MagicMock()
    fake_fs.hash.return_value = "md5hashvalue"

    with patch("oais_utils.validate.open_fs", return_value=fake_fs) as mock_open:
        result = compute_hash("dummyfile", alg="md5")

    mock_open.assert_called_once_with("/")
    fake_fs.hash.assert_called_once_with("dummyfile", "md5")
    assert result == "md5hashvalue"
