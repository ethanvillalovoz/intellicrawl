import json

import pytest

import intellicrawl.cli as cli_module
from intellicrawl.cli import build_parser, main


def test_cli_requires_a_subcommand() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args([])


def test_demo_can_print_and_export(tmp_path, capsys) -> None:
    assert main(["demo", "--format", "json"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["mode"] == "demo"

    output = tmp_path / "report.md"
    assert main(["demo", "--format", "markdown", "--output", str(output)]) == 0
    assert output.read_text().startswith("# vector databases")


def test_live_mode_reports_missing_configuration(monkeypatch, capsys) -> None:
    monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert main(["research", "vector databases"]) == 2
    assert "missing required" in capsys.readouterr().err


def test_keyboard_interrupt_has_shell_exit_code(monkeypatch, capsys) -> None:
    async def interrupted(args):
        raise KeyboardInterrupt

    monkeypatch.setattr(cli_module, "_run", interrupted)
    assert main(["demo"]) == 130
    assert "interrupted" in capsys.readouterr().err
