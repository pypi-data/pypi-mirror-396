import subprocess
import sys

def test_cli_entry_graphviz():
    result = subprocess.run(
        [sys.executable, "-m", "ovm_erd", "graphviz", "--path", "./examples"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    assert result.returncode == 0
    assert "✅" in result.stdout or "saved" in result.stdout.lower()


def test_cli_entry_sql():
    result = subprocess.run(
        [sys.executable, "-m", "ovm_erd", "sql", "--path", "./examples", "--ensemble", "core"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    assert result.returncode == 0
    assert "SELECT" in result.stdout or "saved" in result.stdout.lower()


def test_cli_entry_drawio():
    result = subprocess.run(
        [sys.executable, "-m", "ovm_erd", "drawio", "--path", "./examples", "--ensemble", "core"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    assert result.returncode == 0
    assert "draw.io" in result.stdout or "saved" in result.stdout.lower()
