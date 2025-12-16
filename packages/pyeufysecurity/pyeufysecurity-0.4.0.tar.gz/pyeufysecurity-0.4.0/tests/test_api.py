"""Define tests for the API module."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from eufy_security.api import API, DEFAULT_HEADERS, SERVER_PUBLIC_KEY
from eufy_security.device import Camera
from eufy_security.errors import EufySecurityError

from .common import TEST_EMAIL, TEST_PASSWORD, load_json_fixture


class TestAPIInitialization:
    """Tests for API initialization."""

    def test_api_init_basic(self):
        """Test API initializes with basic parameters."""
        session = MagicMock()
        api = API(TEST_EMAIL, TEST_PASSWORD, session)

        assert api._email == TEST_EMAIL
        assert api._password == TEST_PASSWORD
        assert api._session is session
        assert api._country == "US"
        assert api._token is None
        assert api._api_base is None
        assert api.cameras == {}
        assert api.stations == {}

    def test_api_init_with_country(self):
        """Test API initializes with custom country."""
        session = MagicMock()
        api = API(TEST_EMAIL, TEST_PASSWORD, session, country="DE")

        assert api._country == "DE"

    def test_api_generates_ecdh_keys(self):
        """Test API generates ECDH key pair on init."""
        session = MagicMock()
        api = API(TEST_EMAIL, TEST_PASSWORD, session)

        # Should have private and public keys
        assert api._private_key is not None
        assert api._public_key is not None
        assert api._client_public_bytes is not None

        # Public key should be 65 bytes (uncompressed point format)
        assert len(api._client_public_bytes) == 65

    def test_api_computes_login_shared_secret(self):
        """Test API computes shared secret with server public key."""
        session = MagicMock()
        api = API(TEST_EMAIL, TEST_PASSWORD, session)

        # Should have computed shared secret for login
        assert api._login_shared_secret is not None
        assert len(api._login_shared_secret) == 32  # 256-bit shared secret

    def test_api_response_shared_secret_initially_none(self):
        """Test response shared secret is None until login."""
        session = MagicMock()
        api = API(TEST_EMAIL, TEST_PASSWORD, session)

        assert api._response_shared_secret is None
        assert api._server_public_key_hex is None


class TestServerPublicKey:
    """Tests for server public key constant."""

    def test_server_public_key_length(self):
        """Test server public key is correct length."""
        # Uncompressed EC point: 1 byte prefix + 32 bytes X + 32 bytes Y = 65 bytes
        assert len(SERVER_PUBLIC_KEY) == 65

    def test_server_public_key_starts_with_04(self):
        """Test server public key has uncompressed point prefix."""
        # 0x04 indicates uncompressed point format
        assert SERVER_PUBLIC_KEY[0] == 0x04


class TestDefaultHeaders:
    """Tests for default headers."""

    def test_default_headers_has_required_fields(self):
        """Test default headers contain required fields."""
        required = ["App_version", "Os_type", "Os_version", "Language"]
        for field in required:
            assert field in DEFAULT_HEADERS

    def test_default_headers_android(self):
        """Test default headers mimic Android app."""
        assert DEFAULT_HEADERS["Os_type"] == "android"


class TestCameraFromFixture:
    """Tests for creating Camera objects from fixture data."""

    def test_camera_from_devices_list(self):
        """Test creating Camera from devices list fixture."""
        fixture = load_json_fixture("devices_list_response.json")
        device_info = fixture["data"][0]

        api = MagicMock()
        camera = Camera(api=api, camera_info=device_info)

        assert camera.serial == "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx1"
        assert camera.name == "Driveway"
        assert camera.model == "T8111"
        assert camera.hardware_version == "HAIYI-IMX323"
        assert camera.software_version == "1.9.3"
        assert camera.last_camera_image_url == "https://path/to/image.jpg"

    def test_multiple_cameras_from_fixture(self):
        """Test creating multiple cameras from fixture."""
        fixture = load_json_fixture("devices_list_response.json")
        api = MagicMock()

        cameras = {}
        for device_info in fixture["data"]:
            camera = Camera(api=api, camera_info=device_info)
            cameras[camera.serial] = camera

        assert len(cameras) == 2
        assert "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx1" in cameras
        assert "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx2" in cameras
        assert cameras["xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx1"].name == "Driveway"
        assert cameras["xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx2"].name == "Patio"


class TestErrorResponses:
    """Tests for error response handling using fixtures."""

    def test_invalid_email_response(self):
        """Test invalid email response fixture has correct format."""
        fixture = load_json_fixture("login_failure_invalid_email_response.json")
        assert fixture["code"] == 26006
        assert "email" in fixture["msg"].lower()

    def test_invalid_password_response(self):
        """Test invalid password response fixture has correct format."""
        fixture = load_json_fixture("login_failure_invalid_password_response.json")
        assert fixture["code"] == 26006
        assert "password" in fixture["msg"].lower() or "incorrect" in fixture["msg"].lower()

    def test_empty_response(self):
        """Test empty response fixture is empty dict."""
        fixture = load_json_fixture("empty_response.json")
        assert fixture == {} or fixture.get("data") is None


class TestStreamResponses:
    """Tests for stream response fixtures."""

    def test_start_stream_response(self):
        """Test start stream response has URL."""
        fixture = load_json_fixture("start_stream_response.json")
        assert fixture["code"] == 0
        assert "url" in fixture.get("data", {})

    def test_stop_stream_response(self):
        """Test stop stream response is success."""
        fixture = load_json_fixture("stop_stream_response.json")
        assert fixture["code"] == 0


class TestAPIProperties:
    """Tests for API property accessors."""

    def test_token_property(self):
        """Test token property."""
        session = MagicMock()
        api = API(TEST_EMAIL, TEST_PASSWORD, session)

        assert api.token is None

        api._token = "test-token"
        assert api.token == "test-token"

    def test_token_expiration_property(self):
        """Test token_expiration property."""
        session = MagicMock()
        api = API(TEST_EMAIL, TEST_PASSWORD, session)

        assert api.token_expiration is None

        expiration = datetime.now() + timedelta(days=1)
        api._token_expiration = expiration
        assert api.token_expiration == expiration

    def test_api_base_property(self):
        """Test api_base property."""
        session = MagicMock()
        api = API(TEST_EMAIL, TEST_PASSWORD, session)

        assert api.api_base is None

        api._api_base = "https://api.eufy.com"
        assert api.api_base == "https://api.eufy.com"

    def test_set_token(self):
        """Test set_token method."""
        session = MagicMock()
        api = API(TEST_EMAIL, TEST_PASSWORD, session)

        expiration = datetime.now() + timedelta(days=1)
        api.set_token("my-token", expiration, "https://api.eufy.com")

        assert api.token == "my-token"
        assert api.token_expiration == expiration
        assert api.api_base == "https://api.eufy.com"


class TestAPICryptoState:
    """Tests for API crypto state serialization."""

    def test_get_crypto_state(self):
        """Test getting crypto state for serialization."""
        session = MagicMock()
        api = API(TEST_EMAIL, TEST_PASSWORD, session)

        crypto_state = api.get_crypto_state()

        assert "private_key" in crypto_state
        assert "server_public_key" in crypto_state
        # Private key should be hex-encoded
        assert len(crypto_state["private_key"]) > 0
        # Server public key is empty initially
        assert crypto_state["server_public_key"] == ""

    def test_restore_crypto_state_empty_keys(self):
        """Test restore_crypto_state returns False for empty keys."""
        session = MagicMock()
        api = API(TEST_EMAIL, TEST_PASSWORD, session)

        assert api.restore_crypto_state("", "") is False
        assert api.restore_crypto_state("abc", "") is False
        assert api.restore_crypto_state("", "abc") is False

    def test_restore_crypto_state_invalid_keys(self):
        """Test restore_crypto_state returns False for invalid keys."""
        session = MagicMock()
        api = API(TEST_EMAIL, TEST_PASSWORD, session)

        # Invalid hex
        assert api.restore_crypto_state("not-hex", "also-not-hex") is False

        # Valid hex but invalid key format
        assert api.restore_crypto_state("abcd", "1234") is False

    def test_restore_crypto_state_valid_keys(self):
        """Test restore_crypto_state works with valid keys."""
        session = MagicMock()
        api = API(TEST_EMAIL, TEST_PASSWORD, session)

        # Get current crypto state
        original_state = api.get_crypto_state()
        private_key_hex = original_state["private_key"]

        # Use the hardcoded server public key
        server_public_key_hex = SERVER_PUBLIC_KEY.hex()

        # Restore with valid keys
        result = api.restore_crypto_state(private_key_hex, server_public_key_hex)

        assert result is True


class TestCameraStreaming:
    """Tests for Camera streaming methods."""

    @pytest.mark.asyncio
    async def test_start_stream_local_rtsp(self):
        """Test starting stream with local RTSP credentials."""
        api = MagicMock()
        camera = Camera(
            api=api,
            camera_info={"ip_addr": "192.168.1.100", "device_sn": "ABC", "station_sn": "XYZ"},
            rtsp_username="admin",
            rtsp_password="secret123",
        )

        url = await camera.async_start_stream()

        assert url == "rtsp://admin:secret123@192.168.1.100:554/live0"

    @pytest.mark.asyncio
    async def test_start_stream_url_encodes_credentials(self):
        """Test that RTSP credentials are URL-encoded."""
        api = MagicMock()
        camera = Camera(
            api=api,
            camera_info={"ip_addr": "192.168.1.100", "device_sn": "ABC", "station_sn": "XYZ"},
            rtsp_username="user@home",
            rtsp_password="pass:word/test",
        )

        url = await camera.async_start_stream()

        # Special characters should be URL-encoded
        assert "user%40home" in url
        assert "pass%3Aword%2Ftest" in url

    @pytest.mark.asyncio
    async def test_start_stream_cloud_fallback(self):
        """Test fallback to cloud streaming when no RTSP credentials."""
        api = MagicMock()
        api.request = AsyncMock(return_value={"data": {"url": "rtsp://cloud.eufy.com/stream"}})

        camera = Camera(
            api=api,
            camera_info={"device_sn": "ABC", "station_sn": "XYZ"},
        )

        url = await camera.async_start_stream()

        assert url == "rtsp://cloud.eufy.com/stream"
        api.request.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_stream_cloud_failure(self):
        """Test handling of cloud stream failure."""
        api = MagicMock()
        api.request = AsyncMock(side_effect=EufySecurityError("API error"))

        camera = Camera(
            api=api,
            camera_info={"device_sn": "ABC", "station_sn": "XYZ"},
        )

        url = await camera.async_start_stream()

        assert url is None

    @pytest.mark.asyncio
    async def test_stop_stream(self):
        """Test stopping camera stream."""
        api = MagicMock()
        api.request = AsyncMock()

        camera = Camera(
            api=api,
            camera_info={"device_sn": "ABC123", "station_sn": "XYZ789"},
        )

        await camera.async_stop_stream()

        api.request.assert_called_once_with(
            "post",
            "v1/web/equipment/stop_stream",
            json={
                "device_sn": "ABC123",
                "station_sn": "XYZ789",
                "proto": 2,
            },
        )

    @pytest.mark.asyncio
    async def test_stop_stream_failure_handled(self):
        """Test that stop stream failure is handled gracefully."""
        api = MagicMock()
        api.request = AsyncMock(side_effect=EufySecurityError("API error"))

        camera = Camera(
            api=api,
            camera_info={"device_sn": "ABC", "station_sn": "XYZ"},
        )

        # Should not raise, just log warning
        await camera.async_stop_stream()
