#! /usr/bin/env python
# -*- coding: utf-8 -*-
# tests/test_cli.py

from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
import json

import pytest
import requests
from typer.testing import CliRunner

from gladiator.cli import app
import gladiator.cli as cli_module


@pytest.fixture(autouse=True)
def _clear_login_env(monkeypatch):
    """Ensure arena login env vars never leak into tests."""
    monkeypatch.delenv("GLADIATOR_USERNAME", raising=False)
    monkeypatch.delenv("GLADIATOR_PASSWORD", raising=False)


@contextmanager
def _noop_spinner(*_args, **_kwargs):
    yield


def test_spinner_uses_console_when_tty(monkeypatch):
    events = []

    class DummyCtx:
        def __enter__(self):
            events.append("enter")
            return self

        def __exit__(self, exc_type, exc, tb):
            events.append("exit")

    def fake_status(message, spinner="dots"):
        events.append((message, spinner))
        return DummyCtx()

    monkeypatch.setattr(cli_module, "console", SimpleNamespace(status=fake_status))
    monkeypatch.setattr(
        cli_module, "sys", SimpleNamespace(stdout=SimpleNamespace(isatty=lambda: True))
    )

    with cli_module.spinner("Working"):
        events.append("body")

    assert events == [("Working", "dots"), "enter", "body", "exit"]


def test_login_cli_success(monkeypatch, tmp_path):
    runner = CliRunner()

    class DummyResponse:
        def __init__(self):
            self.headers = {"Content-Type": "application/json"}
            self._payload = {"arena_session_id": "SESSION"}
            self.text = ""

        def raise_for_status(self):
            return None

        def json(self):
            return dict(self._payload)

    class DummySession:
        def __init__(self):
            self.headers = {}
            self.post_calls = []
            self.verify = None

        def post(self, url, headers=None, json=None):
            self.post_calls.append({"url": url, "headers": headers, "json": json})
            return DummyResponse()

    dummy_session = DummySession()
    saved = {}

    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)
    monkeypatch.setattr(cli_module.requests, "Session", lambda: dummy_session)
    monkeypatch.setattr(
        cli_module, "CONFIG_PATH", tmp_path / "login.json", raising=False
    )

    def fake_save_config(data):
        saved.update(data)

    monkeypatch.setattr(cli_module, "save_config_raw", fake_save_config)

    result = runner.invoke(
        app,
        [
            "login",
            "--username",
            "user@example.com",
            "--password",
            "secret",
            "--base-url",
            "https://arena.test/api",
            "--no-verify-tls",
            "--reason",
            "Unit Test",
        ],
    )

    assert result.exit_code == 0
    assert dummy_session.post_calls
    post_call = dummy_session.post_calls[-1]
    assert post_call["url"] == "https://arena.test/api/login"
    assert post_call["json"] == {"email": "user@example.com", "password": "secret"}
    assert dummy_session.verify is False
    assert saved["arena_session_id"] == "SESSION"
    assert saved["base_url"] == "https://arena.test/api"
    assert saved["verify_tls"] is False
    assert saved["reason"] == "Unit Test"


def test_login_cli_http_error(monkeypatch):
    runner = CliRunner()

    class DummyResponse:
        def __init__(self):
            self.headers = {"Content-Type": "application/json"}
            self.text = "Unauthorized"

        def raise_for_status(self):
            raise requests.HTTPError("401 Unauthorized")

        def json(self):
            return {"error": "Unauthorized"}

    class DummySession:
        def __init__(self):
            self.headers = {}
            self.verify = None

        def post(self, *_args, **_kwargs):
            return DummyResponse()

    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)
    monkeypatch.setattr(cli_module.requests, "Session", lambda: DummySession())

    result = runner.invoke(
        app,
        [
            "login",
            "--username",
            "user@example.com",
            "--password",
            "bad",
        ],
    )

    assert result.exit_code == 2
    assert "Login failed" in result.stderr


def test_login_cli_requires_credentials_for_ci(monkeypatch):
    runner = CliRunner()
    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)

    result = runner.invoke(app, ["login", "--ci", "--username", "user@example.com"])

    assert result.exit_code == 2
    assert "Provide --username and --password" in result.stderr


def test_login_function_success(monkeypatch, tmp_path):
    class DummyResponse:
        def __init__(self):
            self.headers = {"Content-Type": "application/json"}
            self._payload = {"arena_session_id": "SESSION"}
            self.text = ""

        def raise_for_status(self):
            return None

        def json(self):
            return dict(self._payload)

    class DummySession:
        def __init__(self):
            self.headers = {}
            self.post_calls = []
            self.verify = None

        def post(self, url, headers=None, json=None):
            self.post_calls.append({"url": url, "headers": headers, "json": json})
            return DummyResponse()

    dummy_session = DummySession()
    saved = {}

    monkeypatch.setattr(cli_module, "spinner", _noop_spinner)
    monkeypatch.setattr(cli_module.requests, "Session", lambda: dummy_session)
    monkeypatch.setattr(
        cli_module, "CONFIG_PATH", tmp_path / "login.json", raising=False
    )
    monkeypatch.setattr(cli_module, "save_config_raw", lambda data: saved.update(data))

    cli_module.login(
        username="user@example.com",
        password="secret",
        base_url="https://arena.test/api",
        verify_tls=False,
        non_interactive=True,
        reason="Unit Test",
    )

    assert dummy_session.post_calls
    assert saved["arena_session_id"] == "SESSION"
    assert saved["verify_tls"] is False


def test_format_http_error_from_json(monkeypatch):
    class DummyResponse:
        def __init__(self, payload):
            self._payload = payload
            self.text = ""

        def json(self):
            return self._payload

    err = requests.HTTPError("Boom")
    err.response = DummyResponse({"message": "It failed"})

    formatted = cli_module._format_http_error(err)
    assert "It failed" in formatted


def test_format_http_error_plain_text(monkeypatch):
    class DummyResponse:
        def __init__(self, text):
            self.text = text

        def json(self):
            raise ValueError("no json")

    err = requests.HTTPError("Boom")
    err.response = DummyResponse("Some failure")

    formatted = cli_module._format_http_error(err)
    assert "Some failure" in formatted


def test_upload_weblink_truncates_edition(monkeypatch):
    runner = CliRunner()
    captured = {}

    class DummyClient:
        def upload_weblink_to_working(self, **kwargs):
            captured.update(kwargs)
            return {"ok": True}

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())

    long_edition = "x" * 40
    result = runner.invoke(
        app,
        [
            "upload-weblink",
            "510-0001",
            "https://example.com/resource",
            "--edition",
            long_edition,
        ],
    )

    assert result.exit_code == 0
    assert captured["edition"] == long_edition[:16]


def test_get_change_cli_success(monkeypatch):
    runner = CliRunner()

    class DummyChangeClient:
        def __init__(self):
            self.calls = []

        def get_change_items(self, *, change_number):
            self.calls.append(change_number)
            return {
                "count": 1,
                "results": [
                    {
                        "affectedItemRevision": {
                            "number": "510-0001",
                            "revisionNumber": "A",
                        },
                        "newRevisionNumber": "B",
                        "dispositionAttributes": [
                            {"name": "In Stock", "value": "Use"},
                            {"name": "WIP", "value": None},
                        ],
                        "notes": "Review",
                        "bomView": {"includedInThisChange": True},
                        "specsView": {"includedInThisChange": False},
                        "filesView": {"includedInThisChange": True},
                        "sourcingView": {"includedInThisChange": False},
                        "costView": {"includedInThisChange": True},
                    }
                ],
            }

    dummy = DummyChangeClient()

    monkeypatch.setattr("gladiator.cli._change_client", lambda: dummy)
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["get-change", "CCO-0006"])

    assert result.exit_code == 0
    assert dummy.calls == ["CCO-0006"]
    assert "Affected items for CCO-0006" in result.stdout
    assert "BOM" in result.stdout
    assert result.stdout.count("*") >= 3


def test_get_change_cli_json_format(monkeypatch):
    runner = CliRunner()

    class DummyChangeClient:
        def get_change_items(self, *, change_number):
            return {"count": 2, "results": []}

    monkeypatch.setattr("gladiator.cli._change_client", lambda: DummyChangeClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["get-change", "--format", "json", "CCO-0009"])

    assert result.exit_code == 0
    assert '{\n  "count": 2' in result.stdout


def test_get_change_cli_http_error(monkeypatch):
    runner = CliRunner()

    class DummyChangeClient:
        def get_change_items(self, **_kwargs):
            raise requests.HTTPError("boom")

    monkeypatch.setattr("gladiator.cli._change_client", lambda: DummyChangeClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["get-change", "CCO-0007"])

    assert result.exit_code == 2
    assert "Arena request failed" in result.stderr


def test_get_change_cli_arena_error(monkeypatch):
    runner = CliRunner()

    class DummyChangeClient:
        def get_change_items(self, **_kwargs):
            from gladiator.arena import ArenaError

            raise ArenaError("cannot fetch")

    monkeypatch.setattr("gladiator.cli._change_client", lambda: DummyChangeClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["get-change", "CCO-0008"])

    assert result.exit_code == 2
    assert "cannot fetch" in result.stderr


def test_add_to_change_cli_success(monkeypatch):
    runner = CliRunner()

    class DummyChangeClient:
        def __init__(self):
            self.add_calls = []
            self.get_calls = []

        def add_item_to_change(
            self,
            *,
            change_number,
            item_number,
            new_revision=None,
            lifecycle_phase=None,
        ):
            self.add_calls.append(
                {
                    "change": change_number,
                    "item": item_number,
                    "new_revision": new_revision,
                    "lifecycle_phase": lifecycle_phase,
                }
            )
            return {"status": "ok"}

        def get_change_items(self, *, change_number):
            self.get_calls.append(change_number)
            return {
                "results": [
                    {
                        "affectedItemRevision": {
                            "number": "510-0001",
                            "revisionNumber": "A",
                        },
                        "newRevisionNumber": "B",
                        "notes": "Added",
                        "bomView": {"includedInThisChange": True},
                        "specsView": {"includedInThisChange": False},
                        "filesView": {"includedInThisChange": True},
                        "sourcingView": {"includedInThisChange": False},
                        "costView": {"includedInThisChange": False},
                    }
                ]
            }

    dummy = DummyChangeClient()

    monkeypatch.setattr("gladiator.cli._change_client", lambda: dummy)
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        [
            "add-to-change",
            "--change",
            "CCO-0003",
            "510-0001",
        ],
    )

    assert result.exit_code == 0
    assert dummy.add_calls == [
        {
            "change": "CCO-0003",
            "item": "510-0001",
            "new_revision": None,
            "lifecycle_phase": "In Production",
        }
    ]
    assert dummy.get_calls == ["CCO-0003"]
    assert "Affected items for CCO-0003" in result.stdout
    assert "┏" in result.stdout


def test_add_to_change_cli_custom_options(monkeypatch):
    runner = CliRunner()

    class DummyChangeClient:
        def __init__(self):
            self.add_calls = []
            self.get_calls = []

        def add_item_to_change(
            self,
            *,
            change_number,
            item_number,
            new_revision=None,
            lifecycle_phase=None,
        ):
            self.add_calls.append(
                {
                    "change": change_number,
                    "item": item_number,
                    "new_revision": new_revision,
                    "lifecycle_phase": lifecycle_phase,
                }
            )
            return {"status": "ok"}

        def get_change_items(self, *, change_number):
            self.get_calls.append(change_number)
            return {"results": []}

    dummy = DummyChangeClient()

    monkeypatch.setattr("gladiator.cli._change_client", lambda: dummy)
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        [
            "add-to-change",
            "--change",
            "CCO-0010",
            "--new-revision",
            "1.2.3",
            "--lifecycle-phase",
            "Pilot",
            "510-0009",
        ],
    )

    assert result.exit_code == 0
    assert dummy.add_calls == [
        {
            "change": "CCO-0010",
            "item": "510-0009",
            "new_revision": "1.2.3",
            "lifecycle_phase": "Pilot",
        }
    ]
    assert dummy.get_calls == ["CCO-0010"]


def test_add_to_change_cli_http_error(monkeypatch):
    runner = CliRunner()

    class DummyChangeClient:
        def add_item_to_change(self, **_kwargs):
            raise requests.HTTPError("boom")

    monkeypatch.setattr("gladiator.cli._change_client", lambda: DummyChangeClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        [
            "add-to-change",
            "--change",
            "CCO-0004",
            "510-0002",
        ],
    )

    assert result.exit_code == 2
    assert "Arena request failed" in result.stderr


def test_add_to_change_cli_arena_error(monkeypatch):
    runner = CliRunner()

    class DummyChangeClient:
        def add_item_to_change(self, **_kwargs):
            from gladiator.arena import ArenaError

            raise ArenaError("cannot add")

    monkeypatch.setattr("gladiator.cli._change_client", lambda: DummyChangeClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        [
            "add-to-change",
            "--change",
            "CCO-0005",
            "510-0003",
        ],
    )

    assert result.exit_code == 2
    assert "cannot add" in result.stderr


def test_add_to_change_cli_json_format(monkeypatch):
    runner = CliRunner()

    class DummyChangeClient:
        def add_item_to_change(self, **_kwargs):
            return {"status": "ok"}

        def get_change_items(self, **_kwargs):
            raise AssertionError("should not fetch change items in json mode")

    monkeypatch.setattr("gladiator.cli._change_client", lambda: DummyChangeClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        [
            "add-to-change",
            "--change",
            "CCO-0011",
            "--format",
            "json",
            "510-0011",
        ],
    )

    assert result.exit_code == 0
    assert '"status"' in result.stdout


def test_add_to_change_cli_null_revision(monkeypatch):
    runner = CliRunner()

    class DummyChangeClient:
        def __init__(self):
            self.add_calls = []

        def add_item_to_change(
            self,
            *,
            change_number,
            item_number,
            new_revision=None,
            lifecycle_phase=None,
        ):
            self.add_calls.append(
                {
                    "change": change_number,
                    "item": item_number,
                    "new_revision": new_revision,
                    "lifecycle_phase": lifecycle_phase,
                }
            )
            return {"status": "ok"}

        def get_change_items(self, *, change_number):
            return {"results": []}

    dummy = DummyChangeClient()

    monkeypatch.setattr("gladiator.cli._change_client", lambda: dummy)
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        [
            "add-to-change",
            "--change",
            "CCO-0020",
            "--format",
            "json",
            "510-0020",
        ],
    )

    assert result.exit_code == 0
    assert dummy.add_calls == [
        {
            "change": "CCO-0020",
            "item": "510-0020",
            "new_revision": None,
            "lifecycle_phase": "In Production",
        }
    ]
    assert json.loads(result.stdout) == {"status": "ok"}


def test_add_to_bom_cli_create(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def __init__(self):
            self.calls = []

        def add_or_update_bom_line(self, **kwargs):
            self.calls.append(kwargs)
            return {
                "action": "created",
                "line": {
                    "item": {"number": kwargs["child_item_number"]},
                    "quantity": kwargs.get("quantity", 1),
                    "refDes": kwargs.get("ref_des"),
                    "notes": kwargs.get("notes"),
                },
            }

    dummy = DummyClient()

    monkeypatch.setattr("gladiator.cli._client", lambda: dummy)
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        [
            "add-to-bom",
            "ASM-100",
            "510-0001",
            "--qty",
            "2",
            "--refdes",
            "R5",
        ],
    )

    assert result.exit_code == 0
    assert dummy.calls == [
        {
            "parent_item_number": "ASM-100",
            "child_item_number": "510-0001",
            "parent_revision": "WORKING",
            "child_revision": None,
            "quantity": 2.0,
            "ref_des": "R5",
            "notes": None,
        }
    ]
    assert "BOM line created" in result.stdout
    assert "qty 2.0" in result.stdout


def test_add_to_bom_cli_json(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def __init__(self):
            self.calls = []

        def add_or_update_bom_line(self, **kwargs):
            self.calls.append(kwargs)
            return {"action": "updated", "line": {"guid": "LINE-1"}}

    dummy = DummyClient()

    monkeypatch.setattr("gladiator.cli._client", lambda: dummy)
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        [
            "add-to-bom",
            "--format",
            "json",
            "ASM-100",
            "510-0001",
        ],
    )

    assert result.exit_code == 0
    assert '"action": "updated"' in result.stdout
    assert dummy.calls[0]["quantity"] is None


def test_add_to_bom_cli_http_error(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def add_or_update_bom_line(self, **_kwargs):
            raise requests.HTTPError("boom")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["add-to-bom", "ASM-100", "510-0002"])

    assert result.exit_code == 2
    assert "Arena request failed" in result.stderr


def test_add_to_bom_cli_arena_error(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def add_or_update_bom_line(self, **_kwargs):
            from gladiator.arena import ArenaError

            raise ArenaError("cannot update BOM")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["add-to-bom", "ASM-100", "510-0003"])

    assert result.exit_code == 2
    assert "cannot update BOM" in result.stderr


def test_submit_change_cli_success(monkeypatch):
    runner = CliRunner()

    class DummyChangeClient:
        def __init__(self):
            self.calls = []

        def submit_change(
            self,
            *,
            change_number,
            status,
            comment=None,
            administrators=None,
        ):
            self.calls.append(
                {
                    "change_number": change_number,
                    "status": status,
                    "comment": comment,
                    "administrators": administrators,
                }
            )
            return {"change": {"number": change_number}, "status": "SUBMITTED"}

    dummy = DummyChangeClient()

    monkeypatch.setattr("gladiator.cli._change_client", lambda: dummy)
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        ["submit-change", "ECO-0100", "--status", "submitted", "--comment", "Ready"],
    )

    assert result.exit_code == 0
    assert dummy.calls == [
        {
            "change_number": "ECO-0100",
            "status": "submitted",
            "comment": "Ready",
            "administrators": None,
        }
    ]
    assert "Change ECO-0100 status set to SUBMITTED" in result.stdout


def test_submit_change_cli_json(monkeypatch):
    runner = CliRunner()

    class DummyChangeClient:
        def submit_change(self, **_kwargs):
            return {"ok": True}

    monkeypatch.setattr("gladiator.cli._change_client", lambda: DummyChangeClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        [
            "submit-change",
            "ECO-0101",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    assert '"ok": true' in result.stdout


def test_submit_change_cli_http_error(monkeypatch):
    runner = CliRunner()

    class DummyChangeClient:
        def submit_change(self, **_kwargs):
            raise requests.HTTPError("boom")

    monkeypatch.setattr("gladiator.cli._change_client", lambda: DummyChangeClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["submit-change", "ECO-0102"])

    assert result.exit_code == 2
    assert "Arena request failed" in result.stderr


def test_submit_change_cli_arena_error(monkeypatch):
    runner = CliRunner()

    class DummyChangeClient:
        def submit_change(self, **_kwargs):
            from gladiator.arena import ArenaError

            raise ArenaError("cannot submit")

    monkeypatch.setattr("gladiator.cli._change_client", lambda: DummyChangeClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["submit-change", "ECO-0103"])

    assert result.exit_code == 2
    assert "cannot submit" in result.stderr


def test_upload_weblink_http_error(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def upload_weblink_to_working(self, **kwargs):
            raise requests.HTTPError("boom")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        ["upload-weblink", "510-0001", "https://example.com/resource"],
    )

    assert result.exit_code == 2
    assert "Arena request failed" in result.stderr


def test_upload_weblink_arena_error(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def upload_weblink_to_working(self, **kwargs):
            from gladiator.arena import ArenaError

            raise ArenaError("web upload blocked")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        ["upload-weblink", "510-0001", "https://example.com/resource"],
    )

    assert result.exit_code == 2
    assert "web upload blocked" in result.stderr


def test_upload_file_truncates_edition(monkeypatch, tmp_path):
    runner = CliRunner()
    captured = {}

    class DummyClient:
        def upload_file_to_working(self, item, file_path, reference, **kwargs):
            captured.update(kwargs)
            return {"ok": True}

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())

    dummy = tmp_path / "firmware.bin"
    dummy.write_text("hi")

    long_edition = "ABCDEF0123456789ZYXWV"  # 21 chars
    result = runner.invoke(
        app,
        [
            "upload-file",
            "510-0001",
            str(dummy),
            "--edition",
            long_edition,
        ],
    )

    assert result.exit_code == 0
    assert captured["edition"] == long_edition[:16]


def test_upload_file_http_error(monkeypatch, tmp_path):
    runner = CliRunner()

    class DummyClient:
        def upload_file_to_working(self, *args, **kwargs):
            raise requests.HTTPError("boom")

    dummy = tmp_path / "fw.bin"
    dummy.write_text("x")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["upload-file", "510-0001", str(dummy)])

    assert result.exit_code == 2
    assert "Arena request failed" in result.stderr


def test_upload_file_arena_error(monkeypatch, tmp_path):
    runner = CliRunner()

    class DummyClient:
        def upload_file_to_working(self, *args, **kwargs):
            from gladiator.arena import ArenaError

            raise ArenaError("upload blocked")

    dummy = tmp_path / "fw.bin"
    dummy.write_text("x")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["upload-file", "510-0001", str(dummy)])

    assert result.exit_code == 2
    assert "upload blocked" in result.stderr


def test_login_success(monkeypatch):
    runner = CliRunner()
    saved = {}

    class DummyResponse:
        def __init__(self):
            self.status_code = 200
            self.text = "OK"

        def raise_for_status(self):
            return None

        def json(self):
            return {"arena_session_id": "ABC123"}

    class DummySession:
        def __init__(self):
            self.verify = None
            self.post_calls = []

        def post(self, url, headers=None, json=None):
            self.post_calls.append({"url": url, "headers": headers, "json": json})
            return DummyResponse()

    dummy_session = DummySession()

    monkeypatch.setattr("gladiator.cli.requests.Session", lambda: dummy_session)
    monkeypatch.setattr(
        "gladiator.cli.save_config_raw", lambda data: saved.update(data)
    )
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        [
            "login",
            "--username",
            "user@example.com",
            "--password",
            "s3cr3t",
            "--base-url",
            "https://arena.test/api",
            "--reason",
            "CI",
        ],
    )

    assert result.exit_code == 0
    assert dummy_session.verify is True
    assert saved["base_url"] == "https://arena.test/api"
    assert saved["reason"] == "CI"
    assert dummy_session.post_calls
    post_call = dummy_session.post_calls[0]
    assert post_call["url"] == "https://arena.test/api/login"
    assert post_call["json"] == {"email": "user@example.com", "password": "s3cr3t"}
    assert post_call["headers"]["Arena-Usage-Reason"] == "CI"
    assert "Saved session" in result.stdout


def test_login_ci_requires_credentials(monkeypatch):
    runner = CliRunner()

    class DummySession:
        def __init__(self):
            self.post_calls = []

        def post(self, *_args, **_kwargs):
            self.post_calls.append((_args, _kwargs))
            raise AssertionError("POST should not be called when credentials missing")

    dummy_session = DummySession()

    session_calls = []

    def _session_factory():
        session_calls.append(True)
        return dummy_session

    monkeypatch.setattr("gladiator.cli.requests.Session", _session_factory)
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["login", "--ci", "--password", "secret"])

    assert result.exit_code == 2
    assert "Provide --username and --password" in result.stderr
    assert not session_calls


def test_login_http_failure(monkeypatch):
    runner = CliRunner()
    saved = {}

    class DummyResponse:
        def __init__(self):
            self.text = "boom"

        def raise_for_status(self):
            raise requests.HTTPError("bad request")

        def json(self):
            return {}

    class DummySession:
        def __init__(self):
            self.verify = None
            self.post_calls = []

        def post(self, url, headers=None, json=None):
            self.post_calls.append({"url": url, "headers": headers, "json": json})
            return DummyResponse()

    monkeypatch.setattr("gladiator.cli.requests.Session", lambda: DummySession())
    monkeypatch.setattr(
        "gladiator.cli.save_config_raw", lambda data: saved.update(data)
    )
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        [
            "login",
            "--username",
            "user@example.com",
            "--password",
            "s3cr3t",
        ],
    )

    assert result.exit_code == 2
    assert "Login failed" in result.stderr
    assert saved == {}


def test_latest_approved_success(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def __init__(self):
            self.calls = []

        def get_latest_approved_revision(self, item):
            self.calls.append(item)
            return "B"

    client = DummyClient()

    monkeypatch.setattr("gladiator.cli._client", lambda: client)
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["latest-approved", "510-0001"])

    assert result.exit_code == 0
    assert client.calls == ["510-0001"]
    assert result.stdout.strip() == "B"


def test_latest_approved_json_output(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def get_latest_approved_revision(self, item):
            return "C"

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        ["latest-approved", "510-0002", "--format", "json"],
    )

    assert result.exit_code == 0
    assert result.stdout.strip() == '{\n  "article": "510-0002",\n  "revision": "C"\n}'


def test_latest_approved_json_missing_revision(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def get_latest_approved_revision(self, item):
            from gladiator.arena import ArenaError

            raise ArenaError(f"No approved/released revisions for item {item}")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        ["latest-approved", "510-0005", "--format", "json"],
    )

    assert result.exit_code == 0
    assert (
        result.stdout.strip()
        == '{\n  "article": "510-0005",\n  "revision": null,\n  "status": "missing"\n}'
    )
    assert "No approved/released revisions for item 510-0005" in result.stderr


def test_latest_approved_http_error(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def get_latest_approved_revision(self, item):
            raise requests.HTTPError("boom")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["latest-approved", "510-0003"])

    assert result.exit_code == 2
    assert "Arena request failed" in result.stderr


def test_latest_approved_arena_error(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def get_latest_approved_revision(self, item):
            from gladiator.arena import ArenaError

            raise ArenaError("no revision")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["latest-approved", "510-0004"])

    assert result.exit_code == 2
    assert "no revision" in result.stderr


def test_latest_approved_missing_revision_text(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def get_latest_approved_revision(self, item):
            from gladiator.arena import ArenaError

            raise ArenaError(f"No approved/released revisions for item {item}")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["latest-approved", "510-0006"])

    assert result.exit_code == 0
    assert "No approved/released revisions for item 510-0006" in result.stdout


def test_list_files_success(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def __init__(self):
            self.calls = []

        def list_files(self, item, revision):
            self.calls.append((item, revision))
            return [
                {
                    "title": "Firmware",
                    "name": "fw.bin",
                    "size": 1024,
                    "edition": "A",
                    "storageMethodName": "FILE",
                    "location": None,
                }
            ]

    client = DummyClient()

    monkeypatch.setattr("gladiator.cli._client", lambda: client)
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["list-files", "510-0005"])

    assert result.exit_code == 0
    assert client.calls == [("510-0005", None)]
    assert "fw.bin" in result.stdout
    assert "1024" in result.stdout


def test_list_files_json(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def list_files(self, item, revision):
            return [{"name": "fw.bin"}]

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        ["list-files", "510-0006", "--rev", "WORKING", "--format", "json"],
    )

    assert result.exit_code == 0
    assert (
        result.stdout.strip()
        == '{\n  "article": "510-0006",\n  "revision": "WORKING",\n  "files": [\n    {\n      "name": "fw.bin"\n    }\n  ]\n}'
    )


def test_list_files_http_error(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def list_files(self, item, revision):
            raise requests.HTTPError("boom")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["list-files", "510-0007"])

    assert result.exit_code == 2
    assert "Arena request failed" in result.stderr


def test_list_files_arena_error(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def list_files(self, item, revision):
            from gladiator.arena import ArenaError

            raise ArenaError("no files")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["list-files", "510-0008"])

    assert result.exit_code == 2
    assert "no files" in result.stderr


def test_info_cli_success(monkeypatch):
    runner = CliRunner()
    captured = {}

    class DummyClient:
        def get_item_summary(self, item, revision):
            captured["args"] = (item, revision)
            return {
                "number": item,
                "revision": "C",
                "name": "Widget",
                "description": "Widget description",
                "category": "Assembly",
                "lifecyclePhase": "Production",
                "revisionStatus": "EFFECTIVE",
                "appUrl": "https://app.test/items/510-0100",
            }

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["info", "510-0100"])

    assert result.exit_code == 0
    assert captured["args"] == ("510-0100", None)
    assert "Widget" in result.stdout
    assert "Lifecycle Phase" in result.stdout
    assert "Item URL" in result.stdout
    assert "https://app.test/items/510-0100" in result.stdout


def test_info_cli_json_format(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def get_item_summary(self, item, revision):
            return {
                "number": item,
                "revision": "B",
                "name": "Widget",
                "category": "Electronics",
                "appUrl": "https://app.test/items/510-0101",
            }

    client = DummyClient()

    monkeypatch.setattr("gladiator.cli._client", lambda: client)
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        ["info", "--rev", "b2", "--format", "json", "510-0101"],
    )

    assert result.exit_code == 0
    assert '"number": "510-0101"' in result.stdout
    assert '"selector": "b2"' in result.stdout
    assert '"appUrl": "https://app.test/items/510-0101"' in result.stdout


def test_info_cli_arena_error(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def get_item_summary(self, *_args, **_kwargs):
            from gladiator.arena import ArenaError

            raise ArenaError("item missing")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["info", "510-0102"])

    assert result.exit_code == 2
    assert "item missing" in result.stderr


def test_info_cli_picture_downloads_file(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def __init__(self):
            self.summary_calls = []
            self.picture_calls = []

        def get_item_summary(self, item, revision):
            self.summary_calls.append((item, revision))
            return {
                "number": item,
                "revision": "D",
                "name": "Widget",
                "category": "Assembly",
            }

        def download_item_picture(self, item, revision, dest_dir=None):
            self.picture_calls.append((item, revision, dest_dir))
            out = Path(dest_dir or ".") / f"{item}.png"
            out.write_bytes(b"img")
            return out

    client = DummyClient()

    monkeypatch.setattr("gladiator.cli._client", lambda: client)
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    with runner.isolated_filesystem():
        result = runner.invoke(app, ["info", "--picture", "510-0103"])

        assert result.exit_code == 0
        assert client.summary_calls == [("510-0103", None)]
        assert client.picture_calls and client.picture_calls[0][0] == "510-0103"
        assert Path("510-0103.png").exists()
        assert "Picture Path" in result.stdout


def test_info_cli_picture_json_handles_null(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def get_item_summary(self, item, revision):
            return {
                "number": item,
                "revision": "E",
                "name": "Widget",
                "category": "Electronics",
            }

        def download_item_picture(self, *_args, **_kwargs):
            return None

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        ["info", "--picture", "--format", "json", "510-0104"],
    )

    assert result.exit_code == 0
    assert '"picturePath": null' in result.stdout


def test_bom_table(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def get_bom(self, item, revision, recursive, max_depth):
            assert recursive is False
            assert max_depth is None
            return [
                {
                    "lineNumber": 1,
                    "quantity": 2,
                    "itemNumber": "510-CH-A",
                    "itemName": "Child A",
                    "refDes": "R1",
                    "level": 0,
                }
            ]

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["get-bom", "510-0009"])

    assert result.exit_code == 0
    assert "510-CH-A" in result.stdout
    assert "Child A" in result.stdout


def test_bom_json(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def get_bom(self, item, revision, recursive, max_depth):
            assert recursive is True
            assert max_depth == 2
            return []

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        [
            "get-bom",
            "510-0010",
            "--rev",
            "WORKING",
            "--output",
            "json",
            "--recursive",
            "--max-depth",
            "2",
        ],
    )

    assert result.exit_code == 0
    assert result.stdout.strip() == '{\n  "count": 0,\n  "results": []\n}'


def test_bom_http_error(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def get_bom(self, item, revision, recursive, max_depth):
            raise requests.HTTPError("boom")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["get-bom", "510-0011"])

    assert result.exit_code == 2
    assert "Arena request failed" in result.stderr


def test_bom_arena_error(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def get_bom(self, item, revision, recursive, max_depth):
            from gladiator.arena import ArenaError

            raise ArenaError("bad bom")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["get-bom", "510-0012"])

    assert result.exit_code == 2
    assert "bad bom" in result.stderr


def test_get_files_default(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def __init__(self):
            self.calls = []

        def download_files(self, item, revision, out_dir):
            self.calls.append((item, revision, out_dir))
            return [out_dir / "fw.bin"]

    client = DummyClient()

    monkeypatch.setattr("gladiator.cli._client", lambda: client)
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["get-files", "510-0013"])

    assert result.exit_code == 0
    assert client.calls == [("510-0013", None, Path("510-0013"))]
    assert result.stdout.strip() == str(Path("510-0013") / "fw.bin")


def test_get_files_recursive(monkeypatch, tmp_path):
    runner = CliRunner()

    class DummyClient:
        def __init__(self):
            self.recursive_calls = []

        def download_files_recursive(self, item, revision, out_dir, max_depth):
            self.recursive_calls.append((item, revision, out_dir, max_depth))
            return [out_dir / "fw.bin"]

        def download_files(self, *args, **kwargs):
            raise AssertionError("Expected recursive path")

    client = DummyClient()
    target_dir = tmp_path / "artifacts"

    monkeypatch.setattr("gladiator.cli._client", lambda: client)
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        [
            "get-files",
            "510-0014",
            "--rev",
            "WORKING",
            "--out",
            str(target_dir),
            "--recursive",
            "--max-depth",
            "2",
        ],
    )

    assert result.exit_code == 0
    assert client.recursive_calls == [("510-0014", "WORKING", target_dir, 2)]
    assert result.stdout.strip() == str(target_dir / "fw.bin")


def test_get_files_http_error(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def download_files(self, item, revision, out_dir):
            raise requests.HTTPError("boom")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["get-files", "510-0015"])

    assert result.exit_code == 2
    assert "Arena request failed" in result.stderr


def test_get_files_arena_error(monkeypatch):
    runner = CliRunner()

    class DummyClient:
        def download_files(self, item, revision, out_dir):
            from gladiator.arena import ArenaError

            raise ArenaError("download blocked")

    monkeypatch.setattr("gladiator.cli._client", lambda: DummyClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["get-files", "510-0016"])

    assert result.exit_code == 2
    assert "download blocked" in result.stderr


def test_create_change_cli_success(monkeypatch):
    runner = CliRunner()
    captured = {}

    class DummyChangeClient:
        def __init__(self):
            self.resolved = []

        def resolve_change_category_guid(self, name):
            self.resolved.append(name)
            return "DOC-GUID"

        def create_change(self, **kwargs):
            captured.update(kwargs)
            return {"guid": "CHG-1", "number": "ECO-0001"}

    dummy = DummyChangeClient()

    monkeypatch.setattr("gladiator.cli._change_client", lambda: dummy)
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        [
            "create-change",
            "--category",
            "Documentation Change Order",
            "--title",
            "ECO Title",
            "--description",
            "Desc",
            "--effectivity-type",
            "permanent_on_date",
            "--planned-date",
            "2025-01-01T00:00:00Z",
            "--approval-deadline",
            "2025-01-10T00:00:00Z",
            "--enforce-deadline",
        ],
    )

    assert result.exit_code == 0
    assert dummy.resolved == ["Documentation Change Order"]
    assert captured["category_guid"] == "DOC-GUID"
    assert captured["effectivity_type"] == "permanent_on_date"
    assert "number_sequence_prefix" not in captured
    assert "routings" not in captured
    assert "additional_attributes" not in captured
    assert captured["enforce_approval_deadline"] is True
    assert "Created change" in result.stdout
    assert "ECO-0001" in result.stdout


def test_create_change_cli_uses_default_category(monkeypatch):
    runner = CliRunner()
    captured = {}

    class DummyChangeClient:
        def __init__(self):
            self.resolved = []

        def resolve_change_category_guid(self, name):
            self.resolved.append(name)
            return "COMP-GUID"

        def create_change(self, **kwargs):
            captured.update(kwargs)
            return {"guid": "CHG-2"}

    dummy = DummyChangeClient()

    monkeypatch.setattr("gladiator.cli._change_client", lambda: dummy)
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(app, ["create-change", "--title", "Default Title"])

    assert result.exit_code == 0
    assert dummy.resolved == ["Engineering Change Order"]
    assert captured["category_guid"] == "COMP-GUID"
    assert "number_sequence_prefix" not in captured
    assert "routings" not in captured
    assert "additional_attributes" not in captured
    assert "Created change" in result.stdout


def test_create_change_cli_json_format(monkeypatch):
    runner = CliRunner()

    class DummyChangeClient:
        def resolve_change_category_guid(self, name):
            return "CAT"

        def create_change(self, **kwargs):
            return {"guid": "CHG-JSON", "number": "ECO-0099"}

    monkeypatch.setattr("gladiator.cli._change_client", lambda: DummyChangeClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        [
            "create-change",
            "--title",
            "JSON Change",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    assert '{\n  "guid": "CHG-JSON"' in result.stdout


def test_create_change_cli_http_error(monkeypatch):
    runner = CliRunner()

    class DummyChangeClient:
        def resolve_change_category_guid(self, name):
            return "CAT"

        def create_change(self, **kwargs):
            raise requests.HTTPError("boom")

    monkeypatch.setattr("gladiator.cli._change_client", lambda: DummyChangeClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        [
            "create-change",
            "--title",
            "ECO",
        ],
    )

    assert result.exit_code == 2
    assert "Arena request failed" in result.stderr


def test_create_change_cli_arena_error(monkeypatch):
    runner = CliRunner()

    class DummyChangeClient:
        def resolve_change_category_guid(self, name):
            return "CAT"

        def create_change(self, **kwargs):
            from gladiator.arena import ArenaError

            raise ArenaError("bad change")

    monkeypatch.setattr("gladiator.cli._change_client", lambda: DummyChangeClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        [
            "create-change",
            "--title",
            "ECO",
        ],
    )

    assert result.exit_code == 2
    assert "bad change" in result.stderr


def test_create_change_cli_category_lookup_error(monkeypatch):
    runner = CliRunner()

    class DummyChangeClient:
        def resolve_change_category_guid(self, name):
            from gladiator.arena import ArenaError

            raise ArenaError("category missing")

        def create_change(self, **kwargs):
            raise AssertionError("create_change should not be called")

    monkeypatch.setattr("gladiator.cli._change_client", lambda: DummyChangeClient())
    monkeypatch.setattr("gladiator.cli.spinner", _noop_spinner)

    result = runner.invoke(
        app,
        [
            "create-change",
            "--category",
            "Missing",
            "--title",
            "ECO",
        ],
    )

    assert result.exit_code == 2
    assert "category missing" in result.stderr
