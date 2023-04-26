from unittest.mock import Mock, patch

import pytest
from can_explorer import app, can_bus, plotting


@pytest.fixture
def mock_buffer():
    with patch("can_explorer.can_bus.PayloadBuffer", autospec=True) as mock:
        yield mock


@pytest.fixture
def mock_listener():
    with patch("can_explorer.can_bus._Listener", autospec=True) as mock:
        yield mock


@pytest.fixture
def mock_notifier():
    with patch("can_explorer.can_bus.Notifier", autospec=True) as mock:
        yield mock


@pytest.fixture
def fake_recorder(mock_listener, mock_notifier):
    recorder = can_bus.Recorder()

    with patch("can_explorer.can_bus.Recorder") as mock:
        mock.return_value = recorder

        yield recorder


@pytest.fixture
def fake_manager():
    with patch("can_explorer.plotting.Row"):
        manager = plotting.PlotManager()

        with patch("can_explorer.plotting.PlotManager") as mock:
            mock.return_value = manager

            yield manager


@pytest.fixture
def fake_app(fake_manager, fake_recorder):
    main_app = app.MainApp()
    main_app.plot_manager = fake_manager
    main_app.can_recorder = fake_recorder
    main_app.set_bus(Mock())
    yield main_app
