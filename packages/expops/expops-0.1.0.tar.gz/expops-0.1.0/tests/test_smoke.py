import sys

import pytest


def test_import_mlops():
    import mlops  # noqa: F401


def test_cli_help_exits_zero(monkeypatch):
    from mlops.main import main

    monkeypatch.setattr(sys, "argv", ["mlops", "--help"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0


