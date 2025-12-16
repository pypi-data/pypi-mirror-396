"""Define tests for device module."""

from unittest.mock import MagicMock

from eufy_security.device import Camera, Station


class TestCamera:
    """Tests for Camera dataclass."""

    def test_camera_serial(self):
        """Test camera serial property."""
        api = MagicMock()
        camera = Camera(api=api, camera_info={"device_sn": "ABC123"})
        assert camera.serial == "ABC123"

    def test_camera_serial_missing(self):
        """Test camera serial when missing returns empty string."""
        api = MagicMock()
        camera = Camera(api=api, camera_info={})
        assert camera.serial == ""

    def test_camera_name(self):
        """Test camera name property."""
        api = MagicMock()
        camera = Camera(api=api, camera_info={"device_name": "Front Door"})
        assert camera.name == "Front Door"

    def test_camera_name_missing(self):
        """Test camera name when missing returns Unknown."""
        api = MagicMock()
        camera = Camera(api=api, camera_info={})
        assert camera.name == "Unknown"

    def test_camera_model(self):
        """Test camera model property."""
        api = MagicMock()
        camera = Camera(api=api, camera_info={"device_model": "T8111"})
        assert camera.model == "T8111"

    def test_camera_model_missing(self):
        """Test camera model when missing returns Unknown."""
        api = MagicMock()
        camera = Camera(api=api, camera_info={})
        assert camera.model == "Unknown"

    def test_camera_station_serial(self):
        """Test camera station_serial property."""
        api = MagicMock()
        camera = Camera(api=api, camera_info={"station_sn": "STATION123"})
        assert camera.station_serial == "STATION123"

    def test_camera_hardware_version(self):
        """Test camera hardware_version property."""
        api = MagicMock()
        camera = Camera(api=api, camera_info={"main_hw_version": "2.0"})
        assert camera.hardware_version == "2.0"

    def test_camera_software_version(self):
        """Test camera software_version property."""
        api = MagicMock()
        camera = Camera(api=api, camera_info={"main_sw_version": "1.5.3"})
        assert camera.software_version == "1.5.3"

    def test_camera_ip_address(self):
        """Test camera ip_address property."""
        api = MagicMock()
        camera = Camera(api=api, camera_info={"ip_addr": "192.168.1.100"})
        assert camera.ip_address == "192.168.1.100"

    def test_camera_ip_address_empty(self):
        """Test camera ip_address when empty returns None."""
        api = MagicMock()
        camera = Camera(api=api, camera_info={"ip_addr": ""})
        assert camera.ip_address is None

    def test_camera_ip_address_missing(self):
        """Test camera ip_address when missing returns None."""
        api = MagicMock()
        camera = Camera(api=api, camera_info={})
        assert camera.ip_address is None

    def test_camera_last_image_url_from_cover_path(self):
        """Test last_camera_image_url from cover_path."""
        api = MagicMock()
        camera = Camera(
            api=api, camera_info={"cover_path": "https://example.com/image.jpg"}
        )
        assert camera.last_camera_image_url == "https://example.com/image.jpg"

    def test_camera_last_image_url_from_event_data(self):
        """Test last_camera_image_url prefers event data."""
        api = MagicMock()
        camera = Camera(
            api=api, camera_info={"cover_path": "https://example.com/old.jpg"}
        )
        camera.update_event_data({"pic_url": "https://example.com/new.jpg"})
        assert camera.last_camera_image_url == "https://example.com/new.jpg"

    def test_camera_last_image_url_missing(self):
        """Test last_camera_image_url when missing returns None."""
        api = MagicMock()
        camera = Camera(api=api, camera_info={})
        assert camera.last_camera_image_url is None

    def test_camera_update_event_data(self):
        """Test update_event_data method."""
        api = MagicMock()
        camera = Camera(api=api, camera_info={})
        camera.update_event_data({"pic_url": "https://example.com/thumb.jpg"})
        assert camera._event_data == {"pic_url": "https://example.com/thumb.jpg"}

    def test_camera_rtsp_credentials(self):
        """Test camera RTSP credentials."""
        api = MagicMock()
        camera = Camera(
            api=api,
            camera_info={},
            rtsp_username="admin",
            rtsp_password="secret123",
        )
        assert camera.rtsp_username == "admin"
        assert camera.rtsp_password == "secret123"

    def test_camera_rtsp_credentials_default(self):
        """Test camera RTSP credentials default to None."""
        api = MagicMock()
        camera = Camera(api=api, camera_info={})
        assert camera.rtsp_username is None
        assert camera.rtsp_password is None

    def test_camera_full_info(self):
        """Test camera with full device info."""
        api = MagicMock()
        camera_info = {
            "device_sn": "T8111H12183909C4",
            "device_name": "Driveway",
            "device_model": "T8111",
            "station_sn": "T8010P12345678",
            "main_hw_version": "HAIYI-IMX323",
            "main_sw_version": "1.9.3",
            "ip_addr": "192.168.1.50",
            "cover_path": "https://example.com/thumb.jpg",
        }
        camera = Camera(api=api, camera_info=camera_info)

        assert camera.serial == "T8111H12183909C4"
        assert camera.name == "Driveway"
        assert camera.model == "T8111"
        assert camera.station_serial == "T8010P12345678"
        assert camera.hardware_version == "HAIYI-IMX323"
        assert camera.software_version == "1.9.3"
        assert camera.ip_address == "192.168.1.50"
        assert camera.last_camera_image_url == "https://example.com/thumb.jpg"


class TestStation:
    """Tests for Station dataclass."""

    def test_station_creation(self):
        """Test creating a Station."""
        station = Station(serial="T8010P12345678", name="Home Base", model="T8010")
        assert station.serial == "T8010P12345678"
        assert station.name == "Home Base"
        assert station.model == "T8010"

    def test_station_equality(self):
        """Test Station equality based on attributes."""
        station1 = Station(serial="ABC", name="Test", model="T8010")
        station2 = Station(serial="ABC", name="Test", model="T8010")
        assert station1 == station2

    def test_station_inequality(self):
        """Test Station inequality."""
        station1 = Station(serial="ABC", name="Test", model="T8010")
        station2 = Station(serial="XYZ", name="Test", model="T8010")
        assert station1 != station2
