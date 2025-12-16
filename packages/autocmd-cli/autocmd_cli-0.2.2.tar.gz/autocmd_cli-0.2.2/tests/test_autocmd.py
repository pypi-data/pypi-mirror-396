"""Basic tests for autocmd functionality."""
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path to import autocmd
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import autocmd_cli as autocmd


def test_get_config_dir():
    """Test that config directory is correctly identified."""
    config_dir = autocmd.get_config_dir()
    assert config_dir == Path.home() / ".config" / "autocmd"
    assert isinstance(config_dir, Path)


def test_detect_shell_zsh():
    """Test shell detection for zsh."""
    with patch.dict(os.environ, {"SHELL": "/bin/zsh"}):
        shell_type, rc_file = autocmd.detect_shell()
        assert shell_type == "zsh"
        assert rc_file == Path.home() / ".zshrc"


def test_detect_shell_bash():
    """Test shell detection for bash."""
    with patch.dict(os.environ, {"SHELL": "/bin/bash"}):
        shell_type, rc_file = autocmd.detect_shell()
        assert shell_type == "bash"
        assert rc_file in [Path.home() / ".bashrc", Path.home() / ".bash_profile"]


def test_detect_shell_unknown():
    """Test shell detection for unsupported shell."""
    with patch.dict(os.environ, {"SHELL": "/bin/fish"}):
        shell_type, rc_file = autocmd.detect_shell()
        assert shell_type is None
        assert rc_file is None


def test_is_shell_setup_false():
    """Test is_shell_setup when not set up."""
    config_dir = autocmd.get_config_dir()
    setup_marker = config_dir / ".shell_setup_done"

    # Ensure marker doesn't exist for this test
    if setup_marker.exists():
        # Skip this test if already set up
        return

    assert autocmd.is_shell_setup() is False


def test_get_api_key_from_env():
    """Test API key retrieval from environment variable."""
    test_key = "sk-ant-test-key-123"
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": test_key}):
        key = autocmd.get_api_key()
        assert key == test_key


if __name__ == "__main__":
    # Run tests manually
    print("Running tests...")
    test_get_config_dir()
    print("✓ test_get_config_dir")

    test_detect_shell_zsh()
    print("✓ test_detect_shell_zsh")

    test_detect_shell_bash()
    print("✓ test_detect_shell_bash")

    test_detect_shell_unknown()
    print("✓ test_detect_shell_unknown")

    test_is_shell_setup_false()
    print("✓ test_is_shell_setup_false")

    test_get_api_key_from_env()
    print("✓ test_get_api_key_from_env")

    print("\nAll tests passed!")
