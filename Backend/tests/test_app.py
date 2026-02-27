import pytest
import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app import get_current_nfl_week


def test_get_current_nfl_week_returns_int(monkeypatch):
    class MockResponse:
        status_code = 200

        def json(self):
            return {"week": 8}

    def mock_get(url):
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)

    week = get_current_nfl_week()
    assert isinstance(week, int)
    assert week == 8