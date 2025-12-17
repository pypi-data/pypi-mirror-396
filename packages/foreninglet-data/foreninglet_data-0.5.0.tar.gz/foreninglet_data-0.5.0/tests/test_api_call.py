import time
from unittest.mock import MagicMock, patch

import pytest
import requests
import vcr

from foreninglet_data import api


@pytest.mark.xfail
def test_api_call_fail_on_no_username():
    """Tests the API call to ForeningLet failing when no username has been provided"""

    fl_cls = api.ForeningLet()
    fl_cls.api_username = ""
    assert fl_cls.check_api_responds() is True


@pytest.mark.xfail
def test_api_call_fail_on_no_password():
    """Tests the API call to ForeningLet failing when no password has been provided"""

    fl_cls = api.ForeningLet()
    fl_cls.api_password = ""
    assert fl_cls.check_api_responds() is True


@vcr.use_cassette("tests/cassettes/test_data_fl_api_get_anon.yaml")
@pytest.mark.vcr()
def test_api_call_succeed():
    """Tests the API call to ForeningLet succeeding when credentials has been provided"""

    fl_cls = api.ForeningLet()
    assert fl_cls.check_api_responds() == 200


@vcr.use_cassette("tests/cassettes/test_data_fl_api_get_anon.yaml")
@pytest.mark.vcr()
def test_get_memberlist():
    """Test the list of members being returned"""
    fl_cls = api.ForeningLet()
    memberlist = fl_cls.get_memberlist()
    assert isinstance(memberlist, list)


def test_get_mocked_memberlist(mocked_memberlist):
    """
    Test getting a mocked memberlist
    """
    memberlist = mocked_memberlist(10, 0)
    assert isinstance(memberlist, list)


def test_get_mocked_memberlist_json(mocked_memberlist):
    """
    Test getting a mocked memberlist in JSON
    """
    memberlist = mocked_memberlist(2, 0)
    assert len(memberlist) == 2


def test_api_retry_on_timeout():
    """
    Test that the API retries on timeout and eventually succeeds
    """
    fl_cls = api.ForeningLet()

    # Mock response that will succeed on the 3rd attempt
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.text = "[]"

    call_count = 0

    def mock_get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            # Fail first two attempts with timeout
            raise requests.exceptions.Timeout("Connection timeout")
        else:
            # Succeed on third attempt
            return mock_response

    with patch("requests.get", side_effect=mock_get):
        start_time = time.time()
        response = fl_cls.fl_api_get("http://test-url.com")
        end_time = time.time()

        # Should have made 3 attempts
        assert call_count == 3
        # Should have some delay due to retries (at least 1 second for first retry)
        assert end_time - start_time >= 1.0
        # Should eventually succeed
        assert response == mock_response


def test_api_retry_on_connection_error():
    """
    Test that the API retries on connection errors
    """
    fl_cls = api.ForeningLet()

    call_count = 0

    def mock_get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            # Fail first attempt with connection error
            raise requests.exceptions.ConnectionError("Connection failed")
        else:
            # Succeed on second attempt
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            return mock_response

    with patch("requests.get", side_effect=mock_get):
        response = fl_cls.fl_api_get("http://test-url.com")

        # Should have made 2 attempts
        assert call_count == 2


def test_api_retry_exhaustion():
    """
    Test that the API eventually gives up after max retries and raises the exception
    """
    fl_cls = api.ForeningLet()

    call_count = 0

    def mock_get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        # Always fail with timeout
        raise requests.exceptions.Timeout("Connection timeout")

    with patch("requests.get", side_effect=mock_get):
        with pytest.raises(requests.exceptions.Timeout):
            fl_cls.fl_api_get("http://test-url.com")

        # Should have made 3 attempts (the configured max)
        assert call_count == 3


def test_api_http_error_retry():
    """
    Test that the API retries on HTTP errors (500, 502, etc.)
    """
    fl_cls = api.ForeningLet()

    call_count = 0

    def mock_get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            # Fail first attempt with HTTP error
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
                "500 Server Error"
            )
            return mock_response
        else:
            # Succeed on second attempt
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            return mock_response

    with patch("requests.get", side_effect=mock_get):
        response = fl_cls.fl_api_get("http://test-url.com")

        # Should have made 2 attempts
        assert call_count == 2


def test_api_timeout_configuration():
    """
    Test that the API uses the correct timeout value
    """
    fl_cls = api.ForeningLet()

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        fl_cls.fl_api_get("http://test-url.com")

        # Verify requests.get was called with timeout=60
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs["timeout"] == 60
