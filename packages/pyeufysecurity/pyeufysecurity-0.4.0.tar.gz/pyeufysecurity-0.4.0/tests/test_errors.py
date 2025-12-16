"""Define tests for errors module."""

import pytest

from eufy_security.errors import (
    CannotConnectError,
    CaptchaRequiredError,
    ConnectError,
    EufySecurityError,
    InvalidCaptchaError,
    InvalidCredentialsError,
    NeedVerifyCodeError,
    NetworkError,
    PhoneNoneSupportError,
    RequestError,
    ServerError,
    VerifyCodeError,
    VerifyCodeExpiredError,
    VerifyCodeMaxError,
    VerifyCodeNoneMatchError,
    VerifyCodePasswordError,
    raise_error,
)


def test_base_error():
    """Test base EufySecurityError."""
    err = EufySecurityError("test message")
    assert str(err) == "test message"
    assert isinstance(err, Exception)


def test_error_inheritance():
    """Test all errors inherit from EufySecurityError."""
    errors = [
        CannotConnectError,
        ConnectError,
        InvalidCredentialsError,
        RequestError,
        InvalidCaptchaError,
        NeedVerifyCodeError,
        NetworkError,
        PhoneNoneSupportError,
        ServerError,
        VerifyCodeError,
        VerifyCodeExpiredError,
        VerifyCodeMaxError,
        VerifyCodeNoneMatchError,
        VerifyCodePasswordError,
    ]
    for error_cls in errors:
        err = error_cls("test")
        assert isinstance(err, EufySecurityError)


def test_captcha_required_error():
    """Test CaptchaRequiredError with attributes."""
    err = CaptchaRequiredError(
        message="CAPTCHA required",
        captcha_id="abc123",
        captcha_image="base64data",
        api=None,
    )
    assert str(err) == "CAPTCHA required"
    assert err.captcha_id == "abc123"
    assert err.captcha_image == "base64data"
    assert err.api is None


def test_captcha_required_error_minimal():
    """Test CaptchaRequiredError with minimal args."""
    err = CaptchaRequiredError("CAPTCHA required", "abc123")
    assert err.captcha_id == "abc123"
    assert err.captcha_image is None
    assert err.api is None


def test_raise_error_success():
    """Test raise_error does nothing on success."""
    raise_error({"code": 0, "msg": "Succeed."})


def test_raise_error_invalid_credentials():
    """Test raise_error raises InvalidCredentialsError."""
    with pytest.raises(InvalidCredentialsError):
        raise_error({"code": 26006, "msg": "Invalid credentials"})


def test_raise_error_wrong_password():
    """Test raise_error raises InvalidCredentialsError for wrong password."""
    with pytest.raises(InvalidCredentialsError):
        raise_error({"code": 26050, "msg": "Wrong password"})


def test_raise_error_connect_error():
    """Test raise_error raises ConnectError."""
    with pytest.raises(ConnectError):
        raise_error({"code": 997, "msg": "Connection failed"})


def test_raise_error_network_error():
    """Test raise_error raises NetworkError."""
    with pytest.raises(NetworkError):
        raise_error({"code": 998, "msg": "Network error"})


def test_raise_error_server_error():
    """Test raise_error raises ServerError."""
    with pytest.raises(ServerError):
        raise_error({"code": 999, "msg": "Server error"})


def test_raise_error_verify_code_expired():
    """Test raise_error raises VerifyCodeExpiredError."""
    with pytest.raises(VerifyCodeExpiredError):
        raise_error({"code": 26051, "msg": "Code expired"})


def test_raise_error_need_verify_code():
    """Test raise_error raises NeedVerifyCodeError."""
    with pytest.raises(NeedVerifyCodeError):
        raise_error({"code": 26052, "msg": "Need verification"})


def test_raise_error_verify_code_max():
    """Test raise_error raises VerifyCodeMaxError."""
    with pytest.raises(VerifyCodeMaxError):
        raise_error({"code": 26053, "msg": "Max attempts"})


def test_raise_error_invalid_captcha():
    """Test raise_error raises InvalidCaptchaError."""
    with pytest.raises(InvalidCaptchaError):
        raise_error({"code": 100033, "msg": "Wrong CAPTCHA"})


def test_raise_error_unknown_code():
    """Test raise_error raises base EufySecurityError for unknown codes."""
    with pytest.raises(EufySecurityError) as exc_info:
        raise_error({"code": 99999, "msg": "Unknown error"})
    assert "Unknown error" in str(exc_info.value)


def test_raise_error_missing_msg():
    """Test raise_error handles missing msg field."""
    with pytest.raises(EufySecurityError) as exc_info:
        raise_error({"code": 99999})
    assert "Unknown error (code 99999)" in str(exc_info.value)
