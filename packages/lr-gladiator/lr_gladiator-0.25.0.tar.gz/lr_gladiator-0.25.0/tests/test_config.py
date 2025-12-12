#! /usr/bin/env python
# -*- coding: utf-8 -*-
# tests/test_config.py

import json
import os

import pytest

from gladiator.config import LoginConfig, load_config, save_config, save_config_raw


@pytest.fixture
def temp_config_dir(tmp_path, monkeypatch):
    config_dir = tmp_path / "conf"
    config_dir.mkdir()
    cfg_file = config_dir / "login.json"
    monkeypatch.setattr("gladiator.config.CONFIG_HOME", config_dir)
    monkeypatch.setattr("gladiator.config.CONFIG_PATH", cfg_file)
    monkeypatch.setenv("GLADIATOR_CONFIG_HOME", str(config_dir))
    monkeypatch.setenv("GLADIATOR_CONFIG", str(cfg_file))
    return cfg_file


def test_save_config_raw_writes_file_with_permissions(temp_config_dir):
    data = {"arenaSessionId": "abc123", "username": "user"}

    save_config_raw(data, path=temp_config_dir)

    assert temp_config_dir.exists()
    assert json.loads(temp_config_dir.read_text()) == data
    mode = os.stat(temp_config_dir).st_mode & 0o777
    assert mode in {0o600, 0o644}


def test_save_config_serializes_model(temp_config_dir):
    cfg = LoginConfig(username="user@example.com", password="pw")

    save_config(cfg, path=temp_config_dir)

    payload = json.loads(temp_config_dir.read_text())

    assert payload["username"] == "user@example.com"
    assert payload["password"] == "pw"
    assert payload["arenaSessionId"] is None


def test_load_config_roundtrip(temp_config_dir):
    cfg = {
        "base_url": "https://arena.test/v1",
        "verify_tls": False,
        "username": "user@example.com",
        "arenaSessionId": "ABC",
        "workspaceId": 123,
    }
    temp_config_dir.write_text(json.dumps(cfg))

    loaded = load_config(path=temp_config_dir)

    assert loaded.base_url == "https://arena.test/v1"
    assert loaded.verify_tls is False
    assert loaded.username == "user@example.com"
    assert loaded.arena_session_id == "ABC"
    assert loaded.workspace_id == 123
