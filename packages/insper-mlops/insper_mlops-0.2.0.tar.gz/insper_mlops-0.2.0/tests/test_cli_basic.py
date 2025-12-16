from typer.testing import CliRunner
from mlopstemplate.cli import app

runner = CliRunner()

def test_app_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Ferramenta de linha de comando para padronizar" in result.stdout

def test_start_help():
    result = runner.invoke(app, ["start", "--help"])
    assert result.exit_code == 0
    assert "Starts the interactive setup process" in result.stdout
