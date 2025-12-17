"""Unit tests for drivers."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from vibelab.drivers.base import ExecutionContext, RunOutput
from vibelab.drivers.local import LocalDriver
from vibelab.models.scenario import CodeType, GitHubCodeRef, LocalCodeRef, Scenario
from vibelab.models.executor import ExecutorSpec
from datetime import datetime, timezone


@pytest.fixture
def sample_scenario_github():
    """Sample GitHub scenario."""
    return Scenario(
        id=1,
        code_type=CodeType.GITHUB,
        code_ref=GitHubCodeRef(owner="test", repo="test-repo", commit_sha="abc123"),
        prompt="Test prompt",
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_scenario_local():
    """Sample local scenario."""
    return Scenario(
        id=2,
        code_type=CodeType.LOCAL,
        code_ref=LocalCodeRef(path="/tmp/test"),
        prompt="Test prompt",
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_scenario_empty():
    """Sample empty scenario."""
    return Scenario(
        id=3,
        code_type=CodeType.EMPTY,
        code_ref=None,
        prompt="Test prompt",
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_harness():
    """Mock harness."""
    harness = Mock()
    harness.id = "test-harness"
    harness.name = "Test Harness"
    harness.supported_providers = ["test"]
    harness.preferred_driver = None
    harness.get_container_image.return_value = None
    return harness


@pytest.fixture
def execution_context(sample_scenario_github, mock_harness):
    """Sample execution context."""
    return ExecutionContext(
        result_id="123",
        scenario=sample_scenario_github,
        harness=mock_harness,
        provider="test",
        model="test-model",
        timeout_seconds=1800,
    )


class TestLocalDriver:
    """Tests for LocalDriver."""

    def test_local_driver_id(self):
        """Test LocalDriver has correct ID."""
        driver = LocalDriver()
        assert driver.id == "local"

    def test_local_driver_setup_github(self, execution_context, tmp_path):
        """Test LocalDriver setup with GitHub scenario."""
        with patch("vibelab.drivers.local.get_vibelab_home", return_value=tmp_path):
            with patch("vibelab.drivers.local.subprocess.run") as mock_run:
                mock_run.return_value = Mock(returncode=0)
                driver = LocalDriver()
                driver.setup(execution_context)
                assert execution_context.workdir is not None

    def test_local_driver_setup_empty(self, sample_scenario_empty, mock_harness, tmp_path):
        """Test LocalDriver setup with empty scenario."""
        ctx = ExecutionContext(
            result_id="123",
            scenario=sample_scenario_empty,
            harness=mock_harness,
            provider="test",
            model="test-model",
            timeout_seconds=1800,
        )
        with patch("vibelab.drivers.local.get_vibelab_home", return_value=tmp_path):
            with patch("vibelab.drivers.local.subprocess.run") as mock_run:
                mock_run.return_value = Mock(returncode=0)
                driver = LocalDriver()
                driver.setup(ctx)
                assert ctx.workdir is not None


# class TestDockerDriver:
#     """Tests for DockerDriver."""

#     @pytest.mark.skipif(
#         True, reason="Requires Docker SDK and Docker daemon"
#     )  # Skip by default, enable for integration tests
#     def test_docker_driver_id(self):
#         """Test DockerDriver has correct ID."""
#         from vibelab.drivers.docker import DockerDriver

#         driver = DockerDriver()
#         assert driver.id == "docker"

#     def test_docker_driver_import_error(self):
#         """Test DockerDriver raises ImportError when docker not installed."""
#         with patch.dict("sys.modules", {"docker": None}):
#             with pytest.raises(ImportError):
#                 from vibelab.drivers.docker import DockerDriver

#                 DockerDriver()


# class TestOrbStackDriver:
#     """Tests for OrbStackDriver."""

#     def test_orbstack_driver_import_error(self):
#         """Test OrbStackDriver raises ImportError when docker not installed."""
#         with patch.dict("sys.modules", {"vibelab.drivers.docker": None}):
#             with pytest.raises(ImportError):
#                 from vibelab.drivers.orbstack import OrbStackDriver

#                 OrbStackDriver()


# class TestModalDriver:
#     """Tests for ModalDriver."""

#     def test_modal_driver_import_error(self):
#         """Test ModalDriver raises ImportError when modal not installed."""
#         with patch.dict("sys.modules", {"modal": None}):
#             with pytest.raises(ImportError):
#                 from vibelab.drivers.modal import ModalDriver

#                 ModalDriver()

#     def test_modal_driver_id(self):
#         """Test ModalDriver has correct ID when available."""
#         # This will fail if modal not installed, which is expected
#         try:
#             from vibelab.drivers.modal import ModalDriver

#             # If we can import, check ID
#             # Note: This will fail if Modal not configured, which is OK for unit tests
#             pass
#         except (ImportError, RuntimeError):
#             # Expected if Modal not installed/configured
#             pass


# class TestDriverRegistry:
#     """Tests for driver registry."""

#     def test_local_driver_registered(self):
#         """Test that local driver is always registered."""
#         from vibelab.drivers import DRIVERS

#         assert "local" in DRIVERS
#         assert DRIVERS["local"].id == "local"

#     def test_docker_driver_conditionally_registered(self):
#         """Test that Docker driver is conditionally registered."""
#         from vibelab.drivers import DRIVERS

#         # Docker driver may or may not be registered depending on availability
#         # Just check that local is always there
#         assert "local" in DRIVERS

#     def test_driver_registry_types(self):
#         """Test that registered drivers implement Driver protocol."""
#         from vibelab.drivers import DRIVERS, Driver

#         for driver_id, driver in DRIVERS.items():
#             assert hasattr(driver, "id")
#             assert hasattr(driver, "setup")
#             assert hasattr(driver, "execute")
#             assert hasattr(driver, "cleanup")
#             assert driver.id == driver_id

