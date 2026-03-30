import os
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import App  # noqa: E402
from User import User  # noqa: E402


@pytest.fixture(autouse=True)
def reset_globals():
    App.users_dict.clear()
    App.roster_id_lookup_table.clear()
    yield
    App.users_dict.clear()
    App.roster_id_lookup_table.clear()


@pytest.fixture
def client():
    with App.app.test_client() as client:
        yield client


def test_get_users_current_populates_when_cache_empty(monkeypatch, client):
    """Week=current should fetch users, build cache, and return rankings."""

    payload = [
        {"display_name": "Alpha", "user_id": "u1", "metadata": {"team_name": "Team A"}},
        {"display_name": "Beta", "user_id": "u2", "metadata": {"team_name": "Team B"}},
    ]

    call_log = {"http_calls": 0}

    def fake_http_get(url, timeout=10):
        call_log["http_calls"] += 1
        call_log["users_url"] = url
        return SimpleNamespace(json=lambda: payload, status_code=200, ok=True)

    def fake_create_user_dictionary(users):
        call_log["created_with"] = users
        for entry in users:
            App.users_dict[entry["user_id"]] = User(
                entry["display_name"],
                entry["user_id"],
                entry["metadata"]["team_name"],
                App.LEAGUE_ID,
            )

    def fake_determine_user_roster_numbers():
        call_log["rosters_called"] = True

    def fake_set_current_week_rankings(target_dict):
        call_log["ranked_ids"] = set(target_dict.keys())
        for idx, user in enumerate(target_dict.values()):
            user.wins = idx
            user.losses = len(target_dict) - idx - 1

    monkeypatch.setattr(App.http, "get", fake_http_get)
    monkeypatch.setattr(App, "create_user_dictionary", fake_create_user_dictionary)
    monkeypatch.setattr(App, "determine_user_roster_numbers", fake_determine_user_roster_numbers)
    monkeypatch.setattr(App, "set_current_week_rankings", fake_set_current_week_rankings)

    resp = client.get("/users?week=current")

    assert resp.status_code == 200
    assert call_log["http_calls"] == 1
    assert call_log["users_url"].endswith(f"/league/{App.LEAGUE_ID}/users")
    assert call_log["created_with"] == payload
    assert call_log.get("rosters_called") is True
    assert call_log["ranked_ids"] == {"u1", "u2"}
    assert resp.get_json() == {
        "Alpha": {"wins": 0, "losses": 1},
        "Beta": {"wins": 1, "losses": 0},
    }
