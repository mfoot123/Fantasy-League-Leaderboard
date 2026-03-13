import os
import sys

import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from App import get_current_nfl_week  # noqa: E402


def test_get_current_nfl_week_returns_int(monkeypatch):
    class MockResponse:
        status_code = 200

        def json(self):
            return {"week": 8, "season_type": "regular"}

    def mock_get(url):
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)

    week = get_current_nfl_week()
    assert isinstance(week, int)
    assert week == 8
