import os
import sys
import subprocess
from pathlib import Path

def test_demo_runner_execution():
    """
    Ensures that the demo runner script executes fully without errors.
    """
    script_path = Path(__file__).parent.parent / "scripts" / "demo_runner.py"
    result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
    
    assert result.returncode == 0, f"Demo runner failed with output: {result.stderr}"
    assert "Demonstration complete" in result.stdout
